import requests
import time
import Modules.Required.Database as Database

from Modules.Required.Errorlog import errorlog


# Try and get the ID for the mod channel. This is used for the moderation log.
def load_modlog(CHANNEL_ID, headers):
    global modroom_available
    global modroom_id
    global channel_id
    channel_id = CHANNEL_ID
    rooms = {}
    try:
        url = 'https://api.twitch.tv/kraken/chat/%s/rooms' % channel_id
        r = requests.get(url, headers=headers).json()
        roomlist = r['rooms']
        for room in roomlist:
            rooms[room['name']] = room['_id']
        modroom_id = rooms['modlog']
        modroom_available = True
    except:
        modroom_available = False
        print(">>No room to post modlog found.")


def modlog(duration, userid, username, reason=""):
    timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
    issub = False
    ismod = False
    duration = int(duration)
    displayname = "MOD-ACTION"

    # Mod action logging
    try:
        if duration == 0:
            message = f"Banned: {username}. Reason: {reason}"
            Database.insertoneindb("Modlog", {"action": "banned", "username": username, "userid": userid, "duration": 0,
                                     "reason": reason, "timestamp": timestamp})
            Database.insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                      "sub": issub, "mod": ismod})
            # if modroom_available:
            #     s.send(
            #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
            #         channel_id.encode(), modroom_id.encode(), message.encode()))
        elif duration <= 5:
            message = f"purged: {username}. reason: {reason}"

            Database.insertoneindb("Modlog", {"action": "purged", "username": username, "duration": duration,
                                     "reason": reason, "timestamp": timestamp})
            Database.insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                      "sub": issub, "mod": ismod})
            # if modroom_available:
            #     s.send(
            #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
            #         channel_id.encode(), modroom_id.encode(), message.encode()))
        else:
            message = f"Timed out: {username}. Duration: {duration}. Reason: {reason}"
            Database.insertoneindb("Modlog", {"action": "timed out", "username": username, "duration": duration,
                                     "reason": reason, "timestamp": timestamp})

            Database.insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "message": message,
                                      "sub": issub, "mod": ismod})
            # if modroom_available:
            #     s.send(
            #         b"PRIVMSG #chatrooms:%s:%s :%s\r\n" % (
            #         channel_id.encode(), modroom_id.encode(), message.encode()))

    except Exception as errormsg:
        errorlog(errormsg, "Modlog", message)
        raise errormsg


def removedmessage(username, userid, message):
    timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
    issub = False
    ismod = False
    displayname = "MOD-ACTION"
    try:
        message = f"Removed message from: {username}. Message: {removedmessage}"
        Database.insertoneindb("Modlog", {"action": "message removed", "username": username, "userid": userid,
                                 "message": message, "timestamp": timestamp})
        Database.insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "userid": userid, "message": message,
                                  "sub": issub, "mod": ismod})
    except Exception as errormsg:
        errorlog(errormsg, "Modlog", message)
        raise errormsg
