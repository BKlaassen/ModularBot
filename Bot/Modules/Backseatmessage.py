import threading
import requests

from Modules.Required.Sendmessage import send_message
from Modules.Required.Errorlog import errorlog
import Modules.Required.Database as Database


def load_bsmessage():
    global bsmessagestr; global backseating
    backseating = False

    try:
        for document in Database.updateoneindb("BackseatMessage"):
            bsmessagestr = document["messagetext"]
    except Exception as errormsg:
        errorlog(errormsg, "Backseatmessage/load_bsmessage()", "")
        bsmessagestr = "/me Please don't backseat. This is a blind playthrough!"
    # TODO Explicitly handle Database connection error(s).


def bsmessage():
    global bstimer
    if backseating:
        try:
            bstimer = threading.Timer(900, bsmessage)
            bstimer.start()
            send_message(bsmessagestr)
        except Exception as errormsg:
            errorlog(errormsg, "Backseatmessage()", '')


def backseatmessage(message):
    global bstimer; global bsmessagestr; global backseating
    messageparts = message.split(" ")
    if messageparts[1] == "on":
        if not backseating:
            backseating = True
            bstimer = threading.Timer(900, bsmessage)
            bstimer.start()
            send_message("Backseating message enabled.")
        else:
            send_message("BSM already enabled.")
    elif messageparts[1] == "off":
        if backseating:
            backseating = False
            bstimer.cancel()
            send_message("Backseating message disabled.")
        else:
            send_message("BSM already off.")
    elif messageparts[1] == "set":
        try:
            newbsmessage = " ".join(messageparts[2:])
            bsmessagestr = newbsmessage

            # Empty filter will match all elements,
            # but since there will be only 1 element in the database this won't be an issue.
            Database.updateoneindb("BackseatMessage", {}, {"messagetext": bsmessagestr}, True)
            send_message("Backseat message changed.")
        except Exception as errormsg:
            errorlog(errormsg, 'backseatmessage/set()', message)
            send_message("There was an error changing the backseatmessage. Please try again.")


def bsmcheck(channel_id, client_id):
    global backseating
    url = 'https://api.twitch.tv/helix/streams?user_id=%s' % channel_id
    headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get(url, headers=headers).json()
    response = r["data"]
    try:
        if response[0]["type"] == "live":
            pass
    except:
        backseating = False
