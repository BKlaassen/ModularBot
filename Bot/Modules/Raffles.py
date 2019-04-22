import requests
import random
from datetime import datetime, timedelta

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database


def load_raffles(CLIENTID, CHANNELID):
    global raffles
    global rafflewinners
    global rafflelist
    global client_id
    global channel_id
    raffles = {}
    rafflelist = {}
    rafflewinners = {}
    client_id = CLIENTID
    channel_id = CHANNELID

    try:
        if Database.collectionexists("Raffles"):
            for document in Database.getallfromdb("Raffles"):
                raffles[document["rafflename"]] = document["mode"]
        for i in rafflelist.keys():
            raffles[i] = []
            rafflewinners[i] = []

            col = Database.getallfromdb("raffle_" + i)
            for document in col:
                if raffles[i]:
                    raffles[i].append(document["username"])
                else:
                    raffles[i] = [document["username"]]

            for document in col:
                if document["haswon"]:
                    if rafflewinners[i]:
                        rafflewinners[i].append(document["username"])
                    else:
                        rafflewinners[i] = document["username"]

    except Exception as errormsg:
        errorlog(errormsg, "Raffles/Load_raffles()", "")


def raffle(message):
    global raffles
    global rafflewinners
    try:
        arguments = message.split(" ")
        raffle = " ".join(arguments[2:])
        if arguments[1] == "add":
            try:
                mode = 'all'
                raffles[raffle] = []
                rafflewinners[raffle] = []
                rafflelist[raffle] = mode

                Database.insertoneindb("Raffles", {"rafflename": raffle, "mode": mode})
                Database.insertoneindb("raffle_" + raffle, {"username": "initialuser", "haswon": False})
                send_message("Raffle \"%s\" created!" % raffle)
            except:
                send_message("Error creating raffle!")
        elif arguments[1] == "remove":
            try:
                del raffles[raffle]
                Database.deletecollection("raffle_" + raffle)
                Database.deleteoneindb("Raffles", {"rafflename": raffle})
                send_message("Raffle \"%s\" deleted!" % raffle)
            except Exception as e:
                send_message("Error removing raffle!")
                print(e)
        elif arguments[1] == "set":
            # !raffle set mode raffle
            try:
                if arguments[2] in ['sub', 'follower', 'follower_7', 'all']:
                    mode = arguments[2]
                    raffle = " ".join(arguments[3:])
                    rafflelist[raffle] = mode
                    Database.updateoneindb("Raffles", {"rafflename": raffle}, {"mode": mode})
                    send_message(f"Mode changed for raffle {raffle}.")
                else:
                    send_message("Correct modes are: sub, follower, follower_7 and all")
            except Exception as errormsg:
                send_message("Error changing mode for this raffle.")
                errorlog(errormsg, "Raffle/set()", message)

        elif arguments[1] == "list":
            if len(raffles.keys > 0):
                send_message("Current raffles are: %s." % ", ".join(raffles.keys()))
            else:
                send_message("There are currently no raffles going.")
        elif arguments[1] == "roll":
            if len(raffles[raffle]) == 0:
                send_message("No contestants left!")
            else:
                rafflewinner = random.choice(raffles[raffle])
                raffles[raffle].remove(rafflewinner)
                rafflewinners[raffle].append(rafflewinner)

                Database.updateoneindb("raffle_" + raffle, {"username": rafflewinner}, {"haswon": True})
                send_message("The winner is: %s!" % rafflewinner)
        elif arguments[1] == "adduser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])

            if user not in raffles[raffle]:
                if user not in rafflewinners[raffle]:
                    raffles[raffle].append(user)
                    Database.insertoneindb("raffle_" + raffle, {"username": user, "haswon": False})
                    send_message("@%s joined raffle: \"%s\"!" % (user, raffle))
                else:
                    send_message("user @%s already won this raffle!" % user)
            else:
                send_message("User @%s is already in this raffle!" % user)
        elif arguments[1] == "removeuser":
            user = arguments[2]
            raffle = " ".join(arguments[3:])

            if user in raffles[raffle]:
                raffles[raffle].remove(user)
                Database.deleteoneindb("raffle_" + raffle, {"username": user})
                send_message("@%s removed from raffle: \"%s\"!" % (user, raffle))
            else:
                send_message("User @%s is not in this raffle!" % user)
        elif arguments[1] == "resetwinners":
            raffle = " ".join(arguments[2:])
            if raffle in rafflewinners.keys():
                rafflewinners[raffle] = []

                Database.updatemanyindb("raffle_" + raffle, {"haswon": True}, {"haswon": False})
                send_message("Rafflewinners \"%s\" cleared!" % raffle)
            else:
                send_message(f"Raffle {raffle} has no winners or does not exist.")
        elif arguments[1] == "stats":
            raffle = " ".join(arguments[2:])
            if raffle in raffles.keys():
                send_message(f"There are currently {len(raffles[raffle])} people in this raffle.")

        elif arguments[1] == "mode":
            send_message(f"{rafflelist[raffle]}")

    except IndexError:
        send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                     "%s" % ", ".join(raffles.keys()))

    except Exception as errormsg:
        errorlog(errormsg, "!raffle", message)


def join_raffle(userid, username, message, issub, ismod):
    global raffles
    allowed = False
    arguments = message.split(" ")
    raffle = " ".join(arguments[1:])

    time_now = datetime.now()
    try:

        if ismod:
            followed_at = '2010-01-01T22:33:44Z'
        else:
            url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid, channel_id)
            headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            followed_at = r["data"][0]['followed_at']

        followed_at_formatted = datetime.strptime(followed_at, '%Y-%m-%dT%H:%M:%SZ')

        following = True
    except IndexError:
        following = False
    except Exception as errormsg:
        following = False
        errorlog(errormsg, "Raffles/join()", message)


    try:
        mode = rafflelist[raffle]
    except:
        send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                     "%s" % ", ".join(raffles.keys()))
        return

    if mode == "sub" and issub:
        allowed = True
    elif mode == "follower" and following:
        allowed = True
    elif mode == "follower_7" and following:
        if time_now - followed_at_formatted >= timedelta(days=7):
            allowed = True
    elif mode == "all":
        allowed = True
    else:
        allowed = False

    if allowed:
        try:
            if userid not in raffles[raffle]:
                if userid not in rafflewinners[raffle]:
                    raffles[raffle].append(userid)
                    Database.insertoneindb("raffle_" + raffle, {"userid": userid, "username": username, "Haswon": False})
                    send_message("@%s joined raffle: \"%s\"!" % (username, raffle))
                else:
                    send_message("@%s you already won this raffle!" % username)
            else:
                send_message("@%s you are already in this raffle!" % username)
        except IndexError:
            send_message("To join a raffle, use !join <raffle name>. Current raffles are: "
                         "%s" % ", ".join(raffles.keys()))
        except Exception:
            send_message("Error adding user %s to raffle: \"%s\". Check if you spelled the "
                         "raffle name correctly." % (username, raffle))
    else:
        if mode == 'sub':
            send_message("This raffle is for subscribers only.")
        elif mode == 'follower':
            send_message("You have to be following this channel to join this raffle.")
        elif mode == 'follower_7':
            send_message("You have to be following this channel for at least 7 days to join this raffle")
