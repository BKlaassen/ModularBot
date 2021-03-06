import requests

from Errorlog import errorlog
from Send_message import send_message
import os


def load_deaths(FOLDER):
    global folder
    global deaths
    folder = FOLDER
    deaths = {}

    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Deaths.txt', 'r') as f:
            for line in f:
                key, value = line.strip("\n").split(":")
                deaths[key.lower()] = int(value)
    except:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Deaths.txt', 'w'):
            pass


def func_deaths(s, message, game, ismod):
    arguments = message.split(" ")
    cooldown_time = 0

    try:
        if len(arguments) > 3 and arguments[1] in ['add', 'set', 'remove']:
            game = " ".join(arguments[3:]).lower()
        if arguments[1] == "list":
            send_message(s, "Current games are: %s" % ", ".join(list(deaths.keys())))
            cooldown_time = 10
        elif arguments[1] == "add" and ismod:
            if game in deaths:
                deaths[game] += int(arguments[2])
            else:
                deaths[game] = int(arguments[2])
            send_message(s, "New death counter for %s is now: %s" % (game, deaths[game]))
            cooldown_time = 5
        elif arguments[1] == "set" and ismod:
            deaths[game] = int(arguments[2])
            send_message(s, "Deaths for %s set to %s" % (game, deaths[game]))
            cooldown_time = 5
        elif arguments[1] == "remove" and ismod:
            if deaths[game] - int(arguments[2]) < 0:
                send_message(s, "Deaths can't be negative. Current deaths: %s" % deaths[game])
            elif game in deaths:
                deaths[game] -= int(arguments[2])
                send_message(s, "New death counter for %s is now: %s" % (game, deaths[game]))
            else:
                send_message(s, "There are no deaths (yet) for %s" % game)
            cooldown_time = 5
        elif " ".join(arguments[1:]).lower() in deaths:
            game = " ".join(arguments[1:]).lower()
            send_message(s, "Deaths in %s: %d!" % (game, deaths[game]))
            cooldown_time = 20
        else:
            send_message(s, "Command \"!deaths %s\" not recognised or "
                            "no deaths yet for this game." %
                         " ".join(arguments[1:]))
            cooldown_time = 10

    except IndexError:
        if game in deaths:
            send_message(s, "Deaths in %s: %d!" % (game, deaths[game]))
        else:
            send_message(s, "There are no deaths (yet) for %s" % game)
        cooldown_time = 20
    except KeyError:
        send_message(s, "There are no deaths (yet) for %s" % game)
        cooldown_time = 20
    except Exception as errormsg:
        errorlog(errormsg, "!deaths", message)
        send_message(s, "Something went wrong. Please check your command.")
        cooldown_time = 5

    finally:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Deaths.txt', 'w') as f:
            for key, value in deaths.items():
                f.write("%s:%s\n" % (key, value))
        return cooldown_time


def dead(s, game):
    try:
        if game in deaths:
            deaths[game] += 1
        else:
            deaths[game] = 1
        send_message(s, "A new death! Deathcount: %d!" % deaths[game])
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Deaths.txt', 'w') as f:
            for key, value in deaths.items():
                f.write("%s:%s\n" % (key, value))
    except Exception as errormsg:
        send_message(s, "A error occured. Please try again.")
        errorlog(errormsg, "!dead", '')
