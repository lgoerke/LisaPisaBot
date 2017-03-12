# basic telegram bot
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial/blob/master/part1/echobot.py

import codecs
import gensim
import gensim.models.doc2vec as d2v
import pandas as pd
import html

import json 
import requests
import time
import csv
import re
import numpy as np
from urllib import parse
# python3: urllib.parse.quote_plus
# python2: urllib.pathname2url

config = open('config.txt', 'r') 
TOKEN = config.read() 

# don't put this in your repo! (put in config, then import config)
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def load_movies_gensim(fname):
    docs = pd.read_csv(fname)
    for i, line in enumerate(docs["answer"]):
        if i != 41:
            line = html.unescape(html.unescape(line))
            yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

def load_names_gensim(fname):
    docs = pd.read_csv(fname)
    for i, line in enumerate(docs["question"]):
        if i != 41:
            line = html.unescape(html.unescape(line))
            yield line


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def echo_all(updates, chitchat_dict, second_answer_dict, movie_dict, second_movie_dict):
    for update in updates["result"]:
        if "message" in update:
            chat = update["message"]["chat"]["id"]
            if "text" in update["message"]:
                message = update["message"]["text"].lower()
                question = message.lower()

                # GENSIM STUFF
                # if the user replied yes to:
                # "Do you want me to help you with deciding on a movie?"
                global asked_to_find_movie
                global model
                global titles
                global documents
                if asked_to_find_movie:
                    # infer the vector for the user generated text
                    newmov = model.infer_vector(question.split())
                    # find the 5 most similar movies in the database
                    most_sim = model.docvecs.most_similar([newmov],topn = 5)
                    # send them to the user
                    send_message('You might be interested in one of these movies:',chat)
                    for i in range(len(most_sim)):
                        send_message(" - "+titles[most_sim[i][0]]+" - \n"+second_movie_dict[titles[most_sim[i][0]]],chat)

                    asked_to_find_movie = False
                    break
                    # newmov = model.infer_vector()
                    # if the user said yes to a movie recommendation


                # Finding out if the user has said his name
                name_str = None
                found_movie = False
                global said_name
                global start_bot
                match = re.findall(said_name,message)
                if match:
                    for entry in match[0]:
                        if len(entry) > 0:
                            name_str = entry
                    question = 'Said_name_Bot'
                    start_bot = True


                # Finding out if the user has asked for identity
                global asked_name
                match = re.findall(asked_name,message)
                if match:
                    question = 'Asked_name_Bot'
                    start_bot = True


                # Finding out if the user has greeted us
                global greeting
                match = re.findall(greeting,message)
                if match:
                    question = np.random.choice(['Alternative_Greeting_Bot','Greeting_Bot'], 1, p=[0.5, 0.5])[0]

                # Finding out if the user wants to know the plot of a movie
                global movie_name
                match = re.findall(movie_name,message)
                if match:
                    question = match[0].lower()
                    found_movie = True

                # Finding out if the user wants to know a movie with certain themes
                global movie_theme
                match = re.findall(movie_theme,message)
                if match:
                    question = match[0].lower()
                    print(question)

                # Finding out if the user neglected what was said before
                global neglect
                match = re.findall(neglect,message)
                if match:
                    if start_bot:
                        question = 'Farewell_Bot'
    
                # Finding out if the user affirmed what was said before
                global affirm
                match = re.findall(affirm,message)
                if match:
                    if start_bot:
                        question = 'Started_Bot'
                        asked_to_find_movie = True


                # Search movie dict
                if question in movie_dict:
                    send_message(second_movie_dict[question], chat)
                # Search chitchat dict
                elif question in chitchat_dict:
                    text = chitchat_dict[question]
                    if name_str is not None:
                        text = text + ', ' + name_str
                    if second_answer_dict[question] == 'qwerty_bot':
                        send_message(text, chat)
                    else:
                        send_message(text, chat)
                        time.sleep(1.5)
                        send_message(second_answer_dict[question], chat)
                
                # Else just echo
                else:
                    if found_movie:
                        send_message('I don\'t know this movie :(',chat)
                    else:
                        send_message(question, chat)

            else:
                send_message('Stickers are not supported', chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = parse.quote_plus(text) # urllib.parse.quote_plus(text) # (python3)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():

    ## doc2vec stuff
    global documents
    # load movies into Gensim format
    documents = list(load_movies_gensim('movie_db.csv'))
    
    # load titles in the same order as Gensim vectors
    global titles
    titles = list(load_names_gensim('movie_db.csv'))

    # Define and train Gensim doc2vec model on the movie descriptions
    # using parameters from the Gensim Lee dataset jupyter tutorial
    global model
    model = d2v.Doc2Vec(documents, size=100, window=8, min_count=2, workers=4)
    assert gensim.models.doc2vec.FAST_VERSION > -1, "this will be painfully slow otherwise"
    alpha, min_alpha = (0.025, 0.001)
    model.alpha, model.min_alpha = alpha, alpha
    model.train(documents)
    ## end doc2vec stuff


    # flag whether the person said yes to movie recommendations
    global asked_to_find_movie
    asked_to_find_movie = False

    # Compile regex
    global said_name

    said_name = re.compile('my name is (\w+)|i am (\w+)')
    #r'@(\w+)

    global asked_name
    asked_name = re.compile('who are you\040?\??|what are you\040?\??')

    global greeting
    greeting = re.compile('hi|hey|hello|hallo|whats up')

    global movie_name
    movie_name = re.compile('what is (\w+[" "\w]*) about\040?\??')

    global movie_theme
    movie_theme = re.compile('can you suggest me a movie about (\w+[,? \w]*)\040?\??')

    global neglect
    neglect = re.compile('no[pe?]?')

    global affirm
    affirm = re.compile('ye[s|p]')



    # Load chitchat dict
    chitchat_dict = {}
    second_answer_dict = {}
    with open('chitchat.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            chitchat_dict[row['question']] = row['answer']
            second_answer_dict[row['question']] = row['second_answer']

    # Load movie dict
    movie_dict = {}
    second_movie_dict = {}
    with codecs.open('movie_db.csv', 'r', 'utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            movie_dict[row['question']] = row['answer']
            second_movie_dict[row['question']] = row['second_answer']

    global start_bot
    start_bot = False

    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates, chitchat_dict, second_answer_dict, movie_dict, second_movie_dict)
        # TODO change time depending on message length
        time.sleep(2)


if __name__ == '__main__':
    main()
