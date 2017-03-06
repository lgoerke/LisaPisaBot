# basic telegram bot
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial/blob/master/part1/echobot.py

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
    with open('movie_db.csv') as csvfile:
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
