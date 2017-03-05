# basic telegram bot
# https://www.codementor.io/garethdwyer/building-a-telegram-bot-using-python-part-1-goi5fncay
# https://github.com/sixhobbits/python-telegram-tutorial/blob/master/part1/echobot.py

import json 
import requests
import time
import csv
import re
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


def echo_all(updates, chitchat_dict, second_answer_dict):
    for update in updates["result"]:
        if "message" in update:
            chat = update["message"]["chat"]["id"]
            if "text" in update["message"]:
                # Finding out if the user has said his name
                name_str = None
                global name
                match = re.findall(name,update["message"]["text"])
                if match:
                    for entry in match[0]:
                        if len(entry) > 0:
                            name_str = entry
                    question = 'Said_name'
                else:
                    question = update["message"]["text"]



                if question in chitchat_dict:
                    text = chitchat_dict[question]
                    if name_str is not None:
                        text = text + ', ' + name_str
                    if second_answer_dict[question] == 'qwerty':
                        send_message(text, chat)
                    else:
                        send_message(text, chat)
                        time.sleep(1.5)
                        send_message(second_answer_dict[question], chat)
                else:
                    text = question
                    send_message(text, chat)
                # Not echo

            else:
                text = 'Stickers are not supported'
                send_message(text, chat)


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
    global name
    name = re.compile('[m|M]y name is (\w+)|[i|I] am (\w+)')
    #r'@(\w+)

    # Load chitchat dict
    chitchat_dict = {}
    second_answer_dict = {}
    with open('chitchat.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            chitchat_dict[row['question']] = row['answer']
            second_answer_dict[row['question']] = row['second_answer']

    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates, chitchat_dict, second_answer_dict)
        # TODO change time depending on message length
        time.sleep(2)


if __name__ == '__main__':
    main()
