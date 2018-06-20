#! /usr/bin/python3

import json
import requests
import time
import urllib

from rivescript import RiveScript

# Initialise the bot
bot = RiveScript()
bot.load_directory("./eg/brain")
bot.sort_replies()

# Token of the chatbot, and the URL of the chatbot
TOKEN = "600286721:AAFDXIjbMPo1EFbz6-1-n3QY4_TPAh_hVLo"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

def import_recycle_bin_data():
    global recyclebins
    with open('cleanupData.json') as data_file:
        recyclebins = json.load(data_file)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)


def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def return_recycle_bin_location(distance_threshold, location, chat_id):
    # We want to find out how many bins are close to the user.
    # Dividing by 111 gives the distance in degrees
    threshold = distance_threshold / 110
    threshold = threshold * threshold
    recycle_bin_list = []
    for bins in recyclebins:
        lat = location["latitude"]
        long = location["longitude"]
        difference = (long - bins[0])**2 + (lat - bins[1])**2
        if difference < threshold:
            recycle_bin_list.append((difference, bins))

    if len(recycle_bin_list) != 0:
        recycle_bin_list.sort()
        url = URL + "sendMessage?text={}&chat_id={}".format("You have " + str(len(recycle_bin_list)) + " recycle bins within " + str(distance_threshold) + "km of you! Here is the nearest one.", chat_id)
        get_url(url)
        url = URL + "sendLocation?longitude={}&latitude={}&chat_id={}".format(recycle_bin_list[0][1][0], recycle_bin_list[0][1][1], chat_id)
        print (url)
        get_url(url)

    # There isn't any bins closeby
    else:
        url = URL + "sendMessage?text={}&chat_id={}".format("There are no recycle bins within " + str(distance_threshold) + "km of you... Want to increase the search radius?", chat_id)
        get_url(url)
        # Set up the inline keyboard

def echo_all(updates):
    for update in updates["result"]:
        print (update)
        # Check if the message is a location message:
        if "location" in update["message"]:
            chat = update["message"]["chat"]["id"]
            reply = return_recycle_bin_location(1, update["message"]["location"], chat)
        else:
            try:
                text = update["message"]["text"]
                reply = bot.reply("localuser",text)
                chat = update["message"]["chat"]["id"]
                if "|||" in reply:
                    send_message(reply.split('|||')[-1], chat)
                else:
                    send_message(reply, chat)
            except Exception as e:
                print(e)


def main():
    import_recycle_bin_data()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)

if __name__== '__main__':
    main()
