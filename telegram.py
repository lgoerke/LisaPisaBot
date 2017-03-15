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

from algoliasearch import algoliasearch

# python3: urllib.parse.quote_plus
# python2: urllib.pathname2url

config = open('config.txt', 'r')
TOKEN = config.read()

algolia = open('config_search.txt', 'r')
algoliaTOKEN = algolia.read()
TOKEN1 = algoliaTOKEN.split()[0]
TOKEN2 = algoliaTOKEN.split()[1]

client = algoliasearch.Client(TOKEN1, TOKEN2)
index = client.init_index("ratedmovies_ge5")


# don't put this in your repo! (put in config, then import config)
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def load_gensim_data(fname):
    plots = []
    titles = []
    movies = pd.read_csv(fname, encoding='utf-8')
    for i in range(len(movies)):
        plot = html.unescape(html.unescape(movies['plot'][i]))
        plots.append(plot)
        title = html.unescape(html.unescape(movies['title'][i]))
        titles.append(title)

    return [titles, plots]


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

                # Finding out if the user has said his name
                name_str = None
                found_movie = False
                asked_to_find_movie = False
                right_movie = False
                global said_name
                global start_bot
                match = re.findall(said_name, message)
                if match:
                    print('Said_name')
                    for entry in match[0]:
                        if len(entry) > 0:
                            name_str = entry
                    question = 'Said_name_Bot'
                    start_bot = True

                # Finding out if the user has asked for identity
                global asked_name
                match = re.findall(asked_name, message)
                if match:
                    print('Asked_name')
                    question = 'Asked_name_Bot'
                    start_bot = True

                # Finding out if the user has greeted us
                global greeting
                match = re.findall(greeting, message)
                if match:
                    print('Greeting')
                    question = np.random.choice(['Alternative_Greeting_Bot','Greeting_Bot'], 1, p=[0.5, 0.5])[0]

                # Finding out if the user wants to know the plot of a movie
                global movie_name
                global moviequery
                match = re.findall(movie_name, message)
                if match:
                    moviequery = match[0].lower()
                    found_movie = True

                # Finding out if the user wants to know a movie with certain themes
                global movie_theme1
                match = re.findall(movie_theme1,message)
                if match:
                    print('Movie_theme')
                    question = match[0].lower()
                    asked_to_find_movie = True

                # Finding out if the user wants to know a movie with certain themes
                global movie_theme2
                match = re.findall(movie_theme2,message)
                if match:
                    print('Movie_theme')
                    question = match[0].lower()
                    asked_to_find_movie = True

                # Finding out if the user neglected what was said before
                global neglect
                match = re.findall(neglect, message)
                if match:
                    print('Neglect')
                    if start_bot:
                        question = 'Farewell_Bot'

                # Finding out if the user affirmed what was said before
                global affirm
                match = re.findall(affirm, message)
                if match:
                    print('Affirm')
                    if start_bot:
                        question = 'Started_Bot'

                global thanking
                match = re.findall(thanking, message)
                if match:
                    print('Thanking')
                    question = np.random.choice(['Alternative_Thanking_Bot','Thanking_Bot'], 1, p=[0.5, 0.5])[0]

                # GENSIM STUFF
                # if the user replied yes to:
                # "Do you want me to help you with deciding on a movie?"
                global model
                global titles
                global plots
                global documents
                if asked_to_find_movie:
                    # infer the vector for the user generated text
                    newmov = model.infer_vector(question.split())
                    # find the 5 most similar movies in the database
                    most_sim = model.docvecs.most_similar([newmov], topn=5)
                    # send them to the user
                    send_message('You might be interested in one of these movies:', chat)
                    time.sleep(1)
                    for i in range(len(most_sim)):
                        send_message(" - " + titles[most_sim[i][0]].title() + " - \n" + plots[most_sim[i][0]], chat)
                        time.sleep(1)

                    asked_to_find_movie = False
                    break
                    # newmov = model.infer_vector()
                    # if the user said yes to a movie recommendation

                # Search movie dict
                # question is the query for algolia
                ## TODO: instead of if q in movie_dict check algolia and return first / sensible hit(s)

                global asked_about_movie
                global movie_list
                if found_movie:
                    movie_list = index.search(moviequery)['hits']
                    if len(movie_list) != 0:
                        reply = movie_list[0]['title'] + '?'
                        send_message(reply, chat)
                        asked_about_movie = True
                        found_movie = False
                        print('asked_about_movie: ' + str(asked_about_movie))
                        movie_list = index.search(moviequery)['hits']
                # Finding out if the user affirmed what was said before
                elif asked_about_movie:
                    print('asked about movie.')
                    match = re.findall(affirm, message)
                    if match:
                        print('user affirmed.')
                        print('Movie list has len',len(movie_list))
                        reply = movie_list[0]['plot']
                        reply = reply[0:500] + '...'
                        send_message(reply, chat)
                        asked_about_movie = False
                    match = re.findall(neglect, message)
                    if match:
                        print('user said no, try next movie.')
                        movie_list.pop(0)
                        print('Movie list has len',len(movie_list))
                        reply = movie_list[0]['title'] + '?'
                        send_message(reply, chat)

                # Search chitchat dict
                elif question in chitchat_dict:
                    text = chitchat_dict[question]
                    if name_str is not None:
                        text = text + ', ' + name_str.title()
                    if second_answer_dict[question] == 'qwerty_bot':
                        send_message(text, chat)
                    else:
                        send_message(text, chat)
                        time.sleep(1.5)
                        send_message(second_answer_dict[question], chat)

                # Else just echo
                else:
                    if found_movie:
                        send_message('I don\'t know this movie :(', chat)
                    else:
                        send_message(question.title(), chat)

            else:
                send_message('Stickers are not supported', chat)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = parse.quote_plus(text)  # urllib.parse.quote_plus(text) # (python3)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)


def main():
    ## doc2vec stuff
    # load titles in the same order as Gensim vectors
    global titles
    global plots
    [titles, plots] = load_gensim_data('moremovies_ge5.csv')

    print("DATA LOADED")

    # Define and train Gensim doc2vec model on the movie descriptions
    # using parameters from the Gensim Lee dataset jupyter tutorial
    global model
    model = d2v.Doc2Vec.load('doc2vec_ge5_model')
    print("MODEL LOADED")
    # model = d2v.Doc2Vec(documents, size=100, window=8, min_count=2, workers=4)
    assert gensim.models.doc2vec.FAST_VERSION > -1, "this will be painfully slow otherwise"
    # alpha, min_alpha = (0.025, 0.001)
    # model.alpha, model.min_alpha = alpha, alpha
    # model.train(documents)
    ## end doc2vec stuff

    # Compile regex
    global said_name
    said_name = re.compile('my name is (\w+)|i am (\w+)')
    # r'@(\w+)

    global asked_name
    asked_name = re.compile('who are you\040?\??|what are you\040?\??')

    global greeting
    greeting = re.compile('hi|hey|hello|hallo|whats up')

    global movie_name
    movie_name = re.compile('what is (\w+[" "\w]*) about\040?\??')

    global movie_theme1
    movie_theme1 = re.compile('can you recommend a movie about (\w+[,? \w]*)\040?\??')
    global movie_theme2
    movie_theme2 = re.compile('can you suggest me a movie about (\w+[,? \w]*)\040?\??')

    global neglect
    neglect = re.compile('no[pe?]?')

    global affirm
    affirm = re.compile('ye[s|p]')

    global thanking
    thanking = re.compile('thank [you]?|thx|thanks')

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
    global asked_about_movie
    asked_about_movie = False
    #global right_movie
    #right_movie = False

    global movie_list
    movie_list = []

    global moviequery
    moviequery = 'noooooosingleresult!'

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