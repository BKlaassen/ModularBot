import sys
import os
import ctypes
import socket
import ast
import threading
import requests
import time
# import validators
from unidecode import unidecode

# Append path to modules to path variable and load custom modules
# sys.path.append(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\modules')

# from Required.Getgame import *  # TODO Keep as seperate module?
# from Random_stuff import *  # TODO split into seperate modules

from Modules.Required.Errors import *
from Modules.Required.Getgame import get_current_game
from Modules.Required import Sendmessage, Tagger, Errorlog, Logger, Database, APICalls
from Modules import Backseatmessage, Roulette, Quotes, Raffles, Deathcounter, Rules, BrokenBoner, RimworldAutomessage,\
    RimworldModLinker, Paddle, Questions, Modlog, Conversions, Unshorten, SongSuggestions, CustomCommands, \
    responseParse, Pun, FollowerGoals


def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))


def parse_ast(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


def enabled(module):  # MB use this in the giant List of modules?
    return modules[module]["config"]["enabled"]


def oncooldown(module, func):
    if modules[module]["functions"][func]["next use"] >= time.time():
        return True
    else:
        return False


def command_limiter(command):  # Allows for cooldowns to be set on commands
    global comlimits
    comlimits.remove(command)


# def logline(line):  # Debug setting to save the raw data recieved to a file
#     try:
#         line = unidecode(line)
#         with open(f"{os.path.dirname(os.path.dirname(__file__))}/{FOLDER}/files/chatlogs/raw-" + time.strftime(
#                 "%d-%m-%Y") + ".txt", 'a+') as f:
#             f.write("[%s] %s\n" % (str(time.strftime("%H:%M:%S")), line))
#     except Exception as errormsg:
#         Errorlog.errorlog(errormsg, "logline()", line)


# def nopong():  # Function to restart the bot in case of connection lost
#     Errorlog.errorlog("Connection lost, bot restarted", "nopong", '')
#     os.execv(sys.executable, [sys.executable, f"{os.path.dirname(__file__)}/{FOLDER}/{FOLDER}.py"] + sys.argv)


def botinstance(channelid, channelname, pipe):
    global modules
    # sys.stderr = open(f"D:\Dropbox\Dropbox\Python\ModularBot\Bot\{channelname}_errorlog.txt", 'w+')
    # sys.stdout = open(f"D:\Dropbox\Dropbox\Python\ModularBot\Bot\{channelname}_log.txt", 'w+')
    try:
        Database.load_database(channelname)
        config = Database.getonefromdb("Config")
        HOST = config["Host"]
        NICK = config["Nickname"].encode()
        PORT = int(config["Port"])
        PASS = config["Password"].encode()
        CHANNEL = channelname.encode()
        CLIENTID = config["Client ID"]
        OAUTH = PASS.decode().split(":")[1]
        FOLDER = config["Folder"]
        STEAMAPIKEY = config['SteamAPIkey']
        # Headers for the Twitch API calls being made.
        headers = {'Client-ID': CLIENTID, 'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': "OAuth " + OAUTH}

        modules = {'SM': {"name": 'Sendmessage'},
                   'EL': {"name": 'Errorlog'},
                   'LO': {"name": 'Logger'},
                   'DC': {"name": 'Deathcounter'},
                   'QU': {"name": 'Quotes'},
                   'RF': {"name": 'Raffles'},
                   'RO': {"name": 'Roulette'},
                   'BSM': {"name": 'Backseatmessage'},
                   'RU': {"name": 'Rules'},
                   'BT': {"name": 'BrokenBoner'},
                   'RA': {"name": 'RimworldAutomessage'},
                   'PA': {"name": 'Paddle'},
                   'QS': {"name": 'Questions'},
                   'ML': {"name": 'Modlog'},
                   'CV': {"name": 'Conversions'},
                   'FG': {"name": 'FollowerGoals'},
                   'RML': {"name": 'RimworldModLinker'},
                   'SS': {"name": 'SongSuggestions'},
                   'CC': {"name": 'CustomCommands'},
                   'RP': {"name": 'ResponseParse'},
                   'US': {"name": 'Unshorten'},
                   'PU': {"name": 'Pun'}}

        # Enabling modules if set to true in config file
        modulesconfig = {}
        for document in Database.getallfromdb('Modules'):
            modulesconfig[document["module"]] = {"enabled": document["enabled"], "mandatory": document["mandatory"]}

        for module in modules.keys():
            modules[module]["config"] = modulesconfig[modules[module]["name"]]
            modules[module]["functions"] = {}
            if modules[module]["config"]["enabled"] and not modulesconfig[modules[module]["name"]]["mandatory"]:
                tree = parse_ast("modules/" + modules[module]["name"] + ".py")
                for func in top_level_functions(tree.body):
                    modules[module]["functions"][func.name] = {"next use": time.time()}

        # modules['other'] = {"name": "Other"}
        # Connecting to Twitch IRC by passing credentials and joining a certain channel
        sock = socket.socket()
        sock.connect((HOST, PORT))
        sock.send(b"PASS " + PASS + b"\r\n")
        sock.send(b"NICK " + NICK + b"\r\n")
        # Sending a command to make twitch return tags with each message
        sock.send(b"CAP REQ :twitch.tv/tags \r\n")
        sock.send(b"CAP REQ :twitch.tv/commands \r\n")
        # Join the IRC channel of the channel
        sock.send(b"JOIN #" + CHANNEL + b"\r\n")

        # Starting the timer in case of a disconnect
        # keepalivetimer = threading.Timer(310, nopong)
        # keepalivetimer.start()

        # Loading the basic modules
        # Tagger.load_tagger(CLIENTID)
        Sendmessage.load_send_message(FOLDER, CHANNEL, sock)
        Errorlog.load_errorlog(FOLDER)

        # Load all the modules that were enabled in the config file
        Database.load_database(FOLDER)
        APICalls.load_apicalls(CLIENTID, channelid)
    except Exception as errormsg:
        Errorlog.errorlog(errormsg, "Bot/startup", "Channel:" + channelname)
        # pipe.send(f"Error: {errormsg}")

        # load_tagger()

    if enabled("RU"):
        Rules.load_rules()
    if enabled("BSM"):
        Backseatmessage.load_bsmessage()
    if enabled("DC"):
        Deathcounter.load_deaths()
    if enabled("QU"):
        Quotes.load_quotes()
    if enabled("RF"):
        Raffles.load_raffles(CLIENTID, channelid)
    if enabled("BT"):
        BrokenBoner.load_bonertimer()
    if enabled("RA"):
        RimworldAutomessage.load_rimworldautomessage(channelid, CLIENTID)
    if enabled("QS"):
        Questions.load_questions()
    if enabled("ML"):
        Modlog.load_modlog(channelid, headers)
    if enabled("FG"):
        FollowerGoals.load_followergoals(FOLDER)
    if enabled("RML"):
        RimworldModLinker.load_mod(STEAMAPIKEY)
    if enabled("SS"):
        SongSuggestions.load_suggestions()
    if enabled("CC"):
        customcommands = CustomCommands.load_commands()
    if enabled("RP"):
        responseParse.load_responses()

    global comlimits
    readbuffer = ""
    modt = False
    comlimits = []

    print("Setup done, entering command loop...")
    # Infinite loop waiting for commands
    while True:
        try:
            # Read messages from buffer to temp, which we then line by line disect.
            readbuffer = readbuffer + sock.recv(1024).decode()
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:

                print(line)  # testing purposes

                # Checks if  message is PING. If so reply pong and extend the timer for a restart
                if "PING" in line:
                    sock.send(b"PONG\r\n")
                    # try:
                    #     keepalivetimer.cancel()
                    #     keepalivetimer = threading.Timer(310, nopong)
                    #     keepalivetimer.start()
                    # except Exception as errormsg:
                    #     Errorlog.errorlog(errormsg, "keepalivetimer", '')

                    # if modules["FG"]["Enabled"]:
                    #     try:
                    #         followergoal(channel_id, CHANNEL, CLIENTID)
                    #     except Exception as errormsg:
                    #         Errorlog.errorlog(errormsg, "Main/followergoal()", "")

                    if enabled("BSM"):
                        Backseatmessage.bsmcheck(channelid, CLIENTID)

                else:
                    # Splits the given string so we can work with it better
                    if modt and "ACK" not in line:
                        parts = line.split(" :", 2)
                    else:
                        parts = line.split(":", 2)

                    # Only works after twitch is done announcing stuff (modt = Message of the day)
                    if modt:
                        msgtype = ""
                        if line.find("PRIVMSG") != -1:
                            username, userid, message, issub, ismod = Tagger.tagprivmsg(line)
                            msgtype = "PRIVMSG"
                            Logger.logger(userid, username, message, issub, ismod)
                        elif line.find("CLEARCHAT") != -1:
                            Tagger.tagclearchat(line)
                            msgtype = "CLEARCHAT"
                        elif line.find("CLEARMSG") != -1:
                            Tagger.tagclearmsg(line)
                            msgtype = "CLEARMSG"
                        elif line.find("USERNOTICE") != -1:
                            Tagger.tagusernotice(line)
                            msgtype = "USERNOTICE"
                        elif line.find("USERSTATE") != -1:
                            msgtype = "USERSTATE"
                        elif line.find("NOTICE") != -1:
                            Tagger.tagnotice(line)
                            msgtype = "NOTICE"

                        # Unshortener TODO fix this thing
                        # if enabled("US"):
                        #     # disable("US")
                        #     tempmessage = message.split(" ")
                        #     for shorturl in tempmessage:
                        #         if validators.url("http://" + shorturl) or validators.url("https://" + shorturl):
                        #             unshorten(shorturl)

                        # These are the actual commands
                        if msgtype == "PRIVMSG" and message[0] == '!':
                            cooldown_time = 0
                            try:
                                messagelow = message.lower()
                                if messagelow == "!test":
                                    Sendmessage.send_message("Test successful. Bot is online!")

                                elif "!pun" in messagelow[0:4] and not oncooldown("other", "pun"):
                                    functionname = "pun"
                                    cooldown_time = 30

                                    Pun.pun()

                                elif "!commandlist" in messagelow[0:12] and not oncooldown("other", "commandlist"):
                                    functionname = "commandlist"
                                    cooldown_time = 30

                                    Sendmessage.send_message(f"Commands for this channel can be found here: "
                                                             f"http://www.bastixx.nl/twitch/{FOLDER}/commands.php")

                                if enabled("RU"):
                                    if "!rule" in messagelow[0:5] and ismod and not oncooldown("RU", "rule"):
                                        custommodule = "RU"
                                        functionname = "rule"
                                        cooldown_time = 5

                                        Rules.func_rules(message)

                                if enabled("DC"):
                                    if "!deaths" in messagelow[0:7] and not oncooldown("DC", "func_deaths"):
                                        custommodule = "DC"
                                        functionname = "func_deaths"

                                        game = str(get_current_game(channelid, CLIENTID)).lower()
                                        cooldown_time = Deathcounter.func_deaths(message, game, ismod)

                                    if "!dead" in messagelow[0:5] and not oncooldown("DC", "dead") and (ismod or issub):
                                        custommodule = "DC"
                                        functionname = "dead"
                                        cooldown_time = 10

                                        game = str(get_current_game(channelid, CLIENTID)).lower()
                                        Deathcounter.dead(game)

                                if enabled("RF"):
                                    if ("!raffle" in messagelow[0:7] or "!giveaway" in messagelow[0:9]) and ismod:
                                        custommodule = "RF"
                                        functionname = "raffle"
                                        cooldown_time = 5

                                        Raffles.raffle(message)

                                    elif "!join" in messagelow[0:5]:
                                        custommodule = "RF"
                                        Raffles.join_raffle(userid, username, message, issub, ismod)

                                if enabled("RO"):
                                    if "!roulette" in messagelow[0:9] and not oncooldown("RO", "roulette"):
                                        custommodule = "RO"
                                        functionname = "roulette"
                                        cooldown_time = 20

                                        Roulette.roulette(username)

                                if enabled("PA"):
                                    if "!paddle" in messagelow[0:7] and not oncooldown("PA", "paddle"):
                                        custommodule = "PA"
                                        try:
                                            cooldown_time = 20
                                            functionname = "paddle"
                                            Paddle.paddle(username, message)

                                        except InsufficientParameterException:
                                            cooldown_time = 0
                                            Sendmessage.send_message("Usage: !paddle <username>")

                                        except KeyError:
                                            pass

                                        except Exception as errormsg:
                                            Errorlog.errorlog(errormsg, "!paddle", message)

                                if enabled("QU"):
                                    if "!lastquote" in messagelow[0:10] and (not oncooldown("QU", "last_quote") or ismod):
                                        custommodule = "QU"
                                        functionname = "last_quote"
                                        cooldown_time = 15

                                        Quotes.last_quote()

                                    elif "!quote" in messagelow[0:6] and (not oncooldown("QU", "quote") or ismod):
                                        custommodule = "QU"
                                        functionname = "quote"
                                        cooldown_time = 15

                                        game = get_current_game(channelid, CLIENTID)
                                        Quotes.quote(message, game)

                                if enabled("BSM"):
                                    if ("!backseatmessage" in messagelow[0:16] or '!bsm' in messagelow[0:4]) and ismod:
                                        Backseatmessage.backseatmessage(message)

                                if enabled("BT"):
                                    if "!bet" in messagelow[0:4] or "!bets" in messagelow[0:5]:
                                        custommodule = "BT"
                                        BrokenBoner.bet(username, userid, message, ismod)

                                    elif "!currentboner" in messagelow[0:13] and not oncooldown("BT", "currentboner"):
                                        custommodule = "BT"
                                        functionname = "currentboner"
                                        cooldown_time = 30
                                        BrokenBoner.currentboner()

                                    elif "!brokenboner" in messagelow[0:12] and not oncooldown("BT", "brokenboner"):
                                        custommodule = "BT"
                                        functionname = "brokenboner"
                                        cooldown_time = 30
                                        BrokenBoner.brokenboner()

                                    elif "!setboner" in messagelow[0:9] and ismod:
                                        BrokenBoner.setboner(message)

                                    elif "!timer" in messagelow[0:6] and (not oncooldown("BT", "timer") or ismod):
                                        custommodule = "BT"
                                        functionname = "timer"
                                        cooldown_time = 30
                                        BrokenBoner.timer(message, ismod)

                                    elif "!fidwins" in messagelow[0:8] and ismod:
                                        custommodule = "BT"
                                        BrokenBoner.fidwins()

                                    elif "!winner" in messagelow[0:7] and ismod:
                                        custommodule = "BT"
                                        BrokenBoner.winner(message)

                                if enabled("QU"):
                                    if "!question" in messagelow[0:9] and not oncooldown("QU", "question"):
                                        custommodule = "QU"
                                        functionname = "question"
                                        cooldown_time = Questions.question(message, ismod)

                                if "!bot" in messagelow[0:4]:
                                    Sendmessage.send_message("This bot is made by Bastixx669. "
                                                             "Github: https://github.com/bastixx/ModularBot")

                                if enabled("CV"):
                                    if "!convert" in messagelow[0:8] and not oncooldown("CV", "convert"):
                                        custommodule = "CV"
                                        functionname = "convert"
                                        cooldown_time = 10
                                        Conversions.convert(message)

                                if enabled("RML"):
                                    if "!linkmod" in messagelow[0:8] and not oncooldown("RML", "linkmod"):
                                        custommodule = "RML"
                                        functionname = "linkmod"
                                        cooldown_time = 15

                                        RimworldModLinker.linkmod(message)

                                if enabled("RA"):
                                    if "!rimworldmessage" in messagelow[0:15]:
                                        custommodule = "RA"
                                        functionname = "setmessage"
                                        RimworldAutomessage.setmessage(message)

                                if enabled("SS"):
                                    if "!suggest" in messagelow[0:8] and (not oncooldown("SS", "suggest")or ismod):
                                        custommodule = "SS"
                                        functionname = "suggest"
                                        cooldown_time = 5

                                        SongSuggestions.suggest(message)

                                    elif "!clearsuggestions" in messagelow[0:17] and ismod:
                                        custommodule = "SS"
                                        SongSuggestions.clearsuggestions()

                                if enabled("CC"):
                                    if "!command" in messagelow[0:8] and ismod:
                                        custommodule = "CC"
                                        CustomCommands.func_command(message)
                                    else:
                                        if messagelow.split(" ")[0] in customcommands.keys():
                                            CustomCommands.eval_command(message)

                                # if '!restart' in messagelow[0:8] and username == 'bastixx669':
                                #     nopong()

                                elif "!module" in messagelow[0:7] and username == 'bastixx669':
                                    messageparts = message.split(" ")
                                    var_break = False
                                    if messageparts[1] == "enable":
                                        try:
                                            templist = []
                                            keyword = " ".join(messageparts[2:])
                                            with open('config.ini', 'r+') as f:
                                                for lineinfile in f:
                                                    if keyword in lineinfile:
                                                        if "False" in lineinfile:
                                                            lineinfile = lineinfile.replace('False', 'True')
                                                        else:
                                                            Sendmessage.send_message("Module already enabled.")
                                                            var_break = True
                                                    templist.append(lineinfile)
                                                f.seek(0)
                                                for lineinfile in templist:
                                                    f.write(lineinfile)
                                            if not var_break:
                                                Sendmessage.send_message(f"Module {keyword} enabled.")
                                                # nopong()
                                        except Exception as errormsg:
                                            Errorlog.errorlog(errormsg, "custommodule/enable", message)
                                            Sendmessage.send_message("Error enabling this custommodule.")
                                    elif messageparts[1] == "disable":
                                        try:
                                            templist = []
                                            keyword = " ".join(messageparts[2:])
                                            with open('config.ini', 'r+') as f:
                                                for lineinfile in f:
                                                    if keyword in lineinfile:
                                                        if "True" in lineinfile:
                                                            lineinfile = lineinfile.replace('True', 'False')
                                                        else:
                                                            Sendmessage.send_message("Module already disabled.")
                                                            var_break = True
                                                    templist.append(lineinfile)
                                                f.seek(0)
                                                for lineinfile in templist:
                                                    f.write(lineinfile)
                                            if not var_break:
                                                Sendmessage.send_message(f"Module {keyword} disabled.")
                                                # nopong()
                                        except Exception as errormsg:
                                            Errorlog.errorlog(errormsg, "custommodule/disable", message)
                                            Sendmessage.send_message("Error disabling this custommodule.")
                            except Exception as errormsg:
                                Errorlog.errorlog(errormsg, "main/functions", message)
                                Sendmessage.send_message("There was an error with the command. "
                                                         "Please check your command and try again.")

                            finally:
                                if cooldown_time != 0:
                                    # tempdict = {custommodule: {"functions": {functionname: {"next use": time.time() + cooldown_time}}}}
                                    modules[custommodule]["functions"][functionname] = {"next use": time.time() + cooldown_time}
                                    # modules.update(tempdict)
                        else:
                            if enabled('RP') and msgtype == "PRIVMSG":
                                responseParse.parse_response(message)

                    for l in parts:
                        if "End of /NAMES list" in l:
                            modt = True
                            Logger.logger(0000000, '>>Bot', f'Bot ready in channel {CHANNEL.decode()}', False, True, True)
                            modulelist = []
                            for custommodule in modules.keys():
                                if modules[custommodule]["config"]["enabled"]:
                                    x = modules[custommodule]["name"]
                                    modulelist.append(x)
                            timestamp = Logger.logger(0000000, ">>Bot", "Modules loaded: %s" % ", ".join(modulelist), False, True, True)

                    # Disabled due to testing purposes.
                    # try:
                    #     if pipe.poll():
                    #         controllercommand = pipe.recv()
                    #         if controllercommand == "lastChat":
                    #             pipe.send(timestamp)
                    # except Exception as errormsg:
                    #     Errorlog.errorlog(errormsg, "Multiprocessing", "")

        except Exception as errormsg:
            # Disabled due to testing purposes.
            # try:
            #     Errorlog.errorlog(errormsg, 'Main()', temp)
            # except Exception:
            #     Errorlog.errorlog(errormsg, 'Main()', '')
            raise errormsg


# todo add cache for follows
# todo rework bonertimer module
# todo streamline functions/names


# Testing purposes. This file is not meant to be run directly
if __name__ == '__main__':
    botinstance(000000, "Louiseyhannah", "none")