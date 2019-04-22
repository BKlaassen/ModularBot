import threading
import requests

from Modules.Required.Sendmessage import send_message
from Modules.Required.Getgame import get_current_game
from Modules.Required.Errorlog import errorlog
import Modules.Required.Database as Database


def load_rimworldautomessage(channelid, CLIENTID):
    global messagetext
    global channel_id
    global client_id
    channel_id = channelid
    client_id = CLIENTID

    try:
        for document in Database.getallfromdb("RimworldAutomessage"):
            messagetext = document["messagetext"]
    except:
        messagetext = "/me If you want a colonist to be renamed to your username then join our raffle!" \
                      " Simply type '!join colonist' to enter!"
    threading.Timer(300, rimworldautomessage).start()


def rimworldautomessage():
    game = get_current_game(channel_id, client_id)

    url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
    headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get(url, headers=headers).json()
    response = r["data"]
    try:
        if response[0]["type"] == "live" and game == "RimWorld":
            send_message(messagetext)

    except IndexError:
        pass
    except Exception as errormsg:
        errorlog(errormsg, "Rimworldautomessage", '')
    finally:
        threading.Timer(900, rimworldautomessage).start()


def setmessage(message):
    global messagetext
    arguments = message.split(" ")
    try:
        if arguments[1] == "set":
            messagetext = " ".join(arguments[2:])
            Database.updateoneindb("RimworldAutomessage", {}, {"messagetext": messagetext}, True)
            send_message("Message updated!")
    except Exception as errormsg:
        errorlog(errormsg, "Rimworldautomessage/setmessage()", message)
        send_message("There was an error setting the message. Please check your command and try again.")

