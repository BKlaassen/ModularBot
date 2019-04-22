from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import Modules.Required.Database as Database


def load_deaths():
    global deaths
    deaths = {}

    try:
        for document in Database.getallfromdb("Deaths"):
            deaths[document["game"]] = document["deaths"]
    except Exception as errormsg:
        errorlog(errormsg, "Deathcounter/Load_deaths()", "")


def func_deaths(message, game, ismod):
    arguments = message.split(" ")
    cooldown_time = 0
    skipdb = False

    try:
        if len(arguments) > 3 and arguments[1] in ['add', 'set', 'remove']:
            game = " ".join(arguments[3:]).lower()
        if arguments[1] == "list":
            send_message("Current games are: %s" % ", ".join(list(deaths.keys())))
            cooldown_time = 10
        elif arguments[1] == "add" and ismod:
            if game in deaths:
                deaths[game] += int(arguments[2])
            else:
                deaths[game] = int(arguments[2])
            send_message("New death counter for %s is now: %s" % (game, deaths[game]))
            cooldown_time = 5
        elif arguments[1] == "set" and ismod:
            deaths[game] = int(arguments[2])
            send_message("Deaths for %s set to %s" % (game, deaths[game]))
            cooldown_time = 5
        elif arguments[1] == "remove" and ismod:
            if deaths[game] - int(arguments[2]) < 0:
                send_message("Deaths can't   be negative. Current deaths: %s" % deaths[game])
            elif game in deaths:
                deaths[game] -= int(arguments[2])
                send_message("New death counter for %s is now: %s" % (game, deaths[game]))
            else:
                send_message("There are no deaths (yet) for %s" % game)
            cooldown_time = 5
        elif " ".join(arguments[1:]).lower() in deaths:
            game = " ".join(arguments[1:]).lower()
            send_message("Deaths in %s: %d!" % (game, deaths[game]))
            cooldown_time = 20
        else:
            send_message("Command \"!deaths %s\" not recognised or "
                         "no deaths yet for this game." %
                         " ".join(arguments[1:]))
            cooldown_time = 10

    except IndexError:
        if game in deaths:
            send_message("Deaths in %s: %d!" % (game, deaths[game]))
        else:
            send_message("There are no deaths (yet) for %s" % game)
            skipdb = True
        cooldown_time = 20
    except KeyError:
        send_message("There are no deaths (yet) for %s" % game)
        cooldown_time = 20
    except Exception as errormsg:
        errorlog(errormsg, "!deaths", message)
        send_message("Something went wrong. Please check your command.")
        cooldown_time = 5

    finally:
        if not skipdb:
            Database.updateoneindb("Deaths", {"game": game}, {"$set": {"deaths": deaths[game]}}, True)
        return cooldown_time


def dead(game):
    try:
        if game in deaths:
            deaths[game] += 1
        else:
            deaths[game] = 1
        send_message("A new death! Deathcount: %d!" % deaths[game])
        Database.updateoneindb("Deaths", {"game": game}, {"$set": {"deaths": deaths[game]}}, True)
    except Exception as errormsg:
        send_message("A error occured. Please try again.")
        errorlog(errormsg, "!dead", '')
