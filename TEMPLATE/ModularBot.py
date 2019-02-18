import sys
import os
import ctypes
import socket
import configparser
import requests
import validators
from unidecode import unidecode

# Append path to modules to path variable and load custom modules
sys.path.append(f'{os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}\\modules')
from Roulette import roulette
from Sendmessage import send_message, load_send_message
from Getgame import getgame  # TODO Keep as seperate module?
from Backseatmessage import backseatmessage, load_bsmessage, bsmcheck
from Errorlog import load_errorlog, errorlog
from Logger import logger, load_logger
from Quotes import load_quotes, quote, last_quote
from Raffles import load_raffles, raffle, join_raffle
from Deathcounter import load_deaths, func_deaths, dead
from Rules import load_rules, func_rules
from BonerTimer import *
from RimworldAutomessage import load_rimworldautomessage
from Paddle import paddle
from Questions import load_questions, question, add_question, remove_question
from Modlog import load_modlog, modlog
from Conversions import convert
from Random_stuff import unshorten, followergoal, load_followergoals, pun  # TODO split into seperate modules
from RimworldModLinker import load_mod, linkmod
from SongSuggestions import load_suggestions, suggest, clearsuggestions

# Load all the variables necessary to connect to Twitch IRC from a config file
config = configparser.ConfigParser()
config.read('Config.ini')
settings = config['Settings']

HOST = settings['host']
NICK = b"%s" % settings['Nickname'].encode()
PORT = int(settings['port'])
PASS = b"%s" % settings['Password'].encode()
CHANNEL = b"%s" % settings['Channel'].encode()
CLIENTID = settings['Client ID']
OAUTH = PASS.decode().split(":")[1]
FOLDER = settings['Folder']
STEAMAPIKEY = settings['SteamApiKey']

# For debugging purposes
debug = config['Debug']
printmessage = debug.getboolean('Print message')
printraw = debug.getboolean('Print raw')
lograw = debug.getboolean('Log raw')
printparts = debug.getboolean('Print tags')

modules = {'SM': {"name": 'Sendmessage'},
           'EL': {"name": 'Errorlog'},
           'LO': {"name": 'Logger'},
           'DC': {"name": 'Deathcounter'},
           'QU': {"name": 'Quotes'},
           'RF': {"name": 'Raffles'},
           'RO': {"name": 'Roulette'},
           'BSM': {"name": 'Backseatmessage'},
           'RU': {"name": 'Rules'},
           'BT': {"name": 'BonerTimer'},
           'RA': {"name": 'RimworldAutomessage'},
           'PA': {"name": 'Paddle'},
           'QS': {"name": 'Questions'},
           'ML': {"name": 'Modlog'},
           'CV': {"name": 'Conversions'},
           'FG': {"name": 'FollowerGoals'},
           'RML': {"name": 'RimworldModLinker'},
           'SS': {"name": 'SongSuggestions'}}

# Enabling modules if set to true in config file
modulesConfig = config['Modules']
for module in modules.keys():
    modules[module]["enabled"] = modulesConfig.getboolean(modules[module]["name"])
    if modules[module]["enabled"]:
        modules[module]["functions"] = dir(modules[module]["name"])
# filter(lambda x: modules[x]["enabled"], modules.keys())

# setting the name of the window to bot name for easier distinguishing
ctypes.windll.kernel32.SetConsoleTitleW(f"{FOLDER}")

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


def command_limiter(command):  # Allows for cooldowns to be set on commands
    global comlimits
    comlimits.remove(command)


def logline(line):  # Debug setting to save the raw data recieved to a file
    try:
        line = unidecode(line)
        with open(f"{os.path.dirname(os.path.dirname(__file__))}/{FOLDER}/files/chatlogs/raw-" + time.strftime(
                "%d-%m-%Y") + ".txt", 'a+') as f:
            f.write("[%s] %s\n" % (str(time.strftime("%H:%M:%S")), line))
    except Exception as errormsg:
        errorlog(errormsg, "logline()", line)


def nopong():  # Function to restart the bot in case of connection lost
    errorlog("Connection lost, bot restarted", "nopong", '')
    os.execv(sys.executable, [sys.executable, f"{os.path.dirname(__file__)}/{FOLDER}/{FOLDER}.py"] + sys.argv)


def main(s=sock):
    global comlimits
    readbuffer = ""
    modt = False
    comlimits = []

    # Starting the timer in case of a disconnect
    keepalivetimer = threading.Timer(310, nopong)
    keepalivetimer.start()

    # Loading the basic modules
    load_send_message(FOLDER, CHANNEL, s)
    load_logger(FOLDER)
    load_errorlog(FOLDER)

    # Resolve user id to channel id via the Twitch API
    try:
        url = "https://api.twitch.tv/helix/users?login=" + CHANNEL.decode()
        headers = {'Client-ID': CLIENTID, 'Accept': 'application/vnd.twitchtv.v5+json',
                   'Authorization': "OAuth " + OAUTH}
        r = requests.get(url, headers=headers).json()
        channel_id = r['data'][0]['id']
    except Exception as errormsg:
        errorlog(errormsg, 'Twitch API/get Client_id', '')
        exit(0)

    # Load all the modules that were enabled in the config file
    if modules['RU']["enabled"]:
        load_rules(FOLDER)
    if modules['BSM']["enabled"]:
        load_bsmessage(FOLDER)
    if modules['DC']["enabled"]:
        load_deaths(FOLDER)
    if modules['QU']["enabled"]:
        load_quotes(FOLDER)
    if modules['RF']["enabled"]:
        load_raffles(FOLDER, CLIENTID, channel_id)
    if modules['BT']["enabled"]:
        load_bonertimer(FOLDER)
    if modules['RA']["enabled"]:
        load_rimworldautomessage(s, FOLDER, channel_id, CLIENTID)
    if modules['QS']["enabled"]:
        load_questions(FOLDER)
    if modules['ML']["enabled"]:
        load_modlog(channel_id, headers, FOLDER)
    if modules['FG']["enabled"]:
        load_followergoals(FOLDER)
    if modules['RML']["enabled"]:
        load_mod(STEAMAPIKEY)
    if modules['BT']["enabled"]:
        load_suggestions(FOLDER)

    # Infinite loop waiting for commands
    while True:
        try:
            # Read messages from buffer to temp, which we then line by line disect.
            readbuffer = readbuffer + s.recv(1024).decode()
            temp = readbuffer.split("\n")
            readbuffer = temp.pop()

            for line in temp:
                if printraw:
                    print(line)
                if lograw:
                    logline(line)
                # Checks if  message is PING. If so reply pong and extend the timer for a restart
                if "PING" in line:
                    s.send(b"PONG\r\n")
                    try:
                        keepalivetimer.cancel()
                        keepalivetimer = threading.Timer(310, nopong)
                        keepalivetimer.start()
                    except Exception as errormsg:
                        errorlog(errormsg, "keepalivetimer", '')

                    if modules["FG"]["Enabled"]:
                        try:
                            followergoal(s, channel_id, CHANNEL, CLIENTID)
                        except Exception as errormsg:
                            errorlog(errormsg, "Main/followergoal()", "")

                    if modules["BSM"]["Enabled"]:
                        bsmcheck(channel_id, CLIENTID)

                else:
                    # Splits the given string so we can work with it better
                    if modt and "ACK" not in line:
                        parts = line.split(" :", 2)
                    else:
                        parts = line.split(":", 2)
                    if printparts:
                        print(parts)
                    if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1] and "ACK" not in \
                            parts[1]:
                        issub = False
                        ismod = False

                    if "CLEARCHAT" in parts[1] and modules["ML"]["Enabled"]:
                        modlog(s, parts)

                    templist = ['QUIT', 'JOIN', 'PART', 'ACK', 'USERSTATE', 'ROOMSTATE', 'CLEARCHAT', "NOTICE",
                                'HOSTTARGET']
                    try:
                        tempparts = parts[1].split(" ")
                    except:
                        tempparts = parts[0].split(" ")

                    if "NOTICE" in tempparts[1]:
                        print(">>>" + parts[2][:len(parts[2]) - 1])

                    if not any(s in tempparts[1] for s in templist):
                        # noinspection PyBroadException
                        try:
                            # Sets the message variable to the actual message sent
                            message = parts[2][:len(parts[2]) - 1]
                        except:
                            message = ""
                        # Sets the username variable to the actual username
                        usernamesplit = str.split(parts[1], "!")
                        username = usernamesplit[0]
                        displayname = username
                        tags = str.split(parts[0], ';')

                        # Get index of mod and sub status dynamically because tag indexes are not fixed
                        subindex = [i for i, z in enumerate(tags) if 'subscriber' in z]
                        modindex = [i for i, z in enumerate(tags) if 'mod' in z]
                        displayindex = [i for i, z in enumerate(tags) if 'display-name' in z]

                        # Only works after twitch is done announcing stuff (modt = Message of the day)
                        if modt:
                            subindex = subindex[0]
                            modindex = modindex[0]
                            displayindex = displayindex[0]
                            if tags[displayindex] != 'display-name=':
                                displayname = tags[displayindex]
                                displayname = displayname.split("=")[1]
                                displayname = displayname.replace("\\s", '')

                            if tags[subindex] == 'subscriber=1' or 'subscriber' in tags[0]:
                                issub = True
                            else:
                                issub = False

                            if tags[modindex] == 'mod=1' or 'mod' in tags[0] or 'broadcaster' in tags[0]:
                                ismod = True
                            else:
                                ismod = False

                            if printmessage:
                                if message != "":
                                    print(displayname + ": " + message)

                            if message != "":
                                logger(displayname, message, issub, ismod)

                            if modules["US"]["Enabled"]:
                                tempmessage = message.split(" ")
                                for shorturl in tempmessage:
                                    if validators.url("http://" + shorturl) or validators.url("https://" + shorturl):
                                        unshorten(s, shorturl)

                            # These are the actual commands
                            if message == "":
                                pass
                            # elif messagekeywords in QAlist:
                            #     pass

                            elif message[0] == '!':
                                if message.lower() == "!test":
                                    send_message("Test successful. Bot is online!")

                                # elif "!pun" in message.lower() and "!pun" not in comlimits:
                                #     threading.Timer(15, command_limiter, ['!pun']).start()
                                #     comlimits.append('!pun')
                                #     pun(s)
                                #
                                # elif "!commandlist" in message.lower() and "!commandlist" not in comlimits:
                                #     threading.Timer(15, command_limiter, ['!commandlist']).start()
                                #     comlimits.append('!commandlist')
                                #     send_message(f"Commands for this channel can be found here: "
                                #                  f"http://www.bastixx.nl/twitch/{FOLDER}/commands.php")
                                #
                                # if module_rules:
                                #     if "!rule" in message.lower() and ismod and '!rule' not in comlimits:
                                #         threading.Timer(5, command_limiter, ['!rule']).start()
                                #         comlimits.append('!rule')
                                #         func_rules(s, message)
                                #
                                # if module_deathcounter:
                                #     if "!deaths" in message.lower() and "!deaths" not in comlimits:
                                #         game = str(getgame(channel_id, CLIENTID)).lower()
                                #
                                #         cooldown_time = func_deaths(s, message, game, ismod)
                                #         threading.Timer(cooldown_time, command_limiter, ['!deaths']).start()
                                #         comlimits.append('!deaths')
                                #
                                # if message.lower() == "!dead" and "!dead" not in comlimits and (ismod or issub):
                                #     threading.Timer(30, command_limiter, ['!dead']).start()
                                #     comlimits.append('!dead')
                                #     game = str(getgame(channel_id, CLIENTID)).lower()
                                #     dead(s, game)
                                #
                                # if module_raffles:
                                #     if "!raffle" in message.lower() and ismod:
                                #         raffle(s, message)
                                #
                                #     elif "!join" in message.lower():
                                #         join_raffle(s, displayname, message, issub, ismod)
                                #
                                # if module_roulette:
                                #     if "!roulette" in message.lower() and "!roulette" not in comlimits and \
                                #             module_roulette:
                                #         threading.Timer(20, command_limiter, ['!roulette']).start()
                                #         comlimits.append('!roulette')
                                #         roulette(displayname, s)
                                #
                                # if module_paddle:
                                #     if "!paddle" in message and "!paddle" not in comlimits:
                                #         threading.Timer(20, command_limiter, ['!paddle']).start()
                                #         comlimits.append('!paddle')
                                #         paddle(s, displayname, message)
                                #
                                # if module_quotes:
                                #     if message.lower() == "!lastquote" and ("!quote" not in comlimits or ismod):
                                #         threading.Timer(15, command_limiter, ['!quote']).start()
                                #         comlimits.append('!quote')
                                #         last_quote(s)
                                #
                                #     elif "!quote" in message.lower() and ("!quote" not in comlimits or ismod):
                                #         threading.Timer(15, command_limiter, ['!quote']).start()
                                #         comlimits.append('!quote')
                                #         game = getgame(channel_id, CLIENTID)
                                #         quote(s, message, game)
                                #
                                # if module_backseatmessage:
                                #     if "!backseatmessage" in message.lower() or '!bsm' in message.lower() and ismod:
                                #         backseatmessage(s, message)
                                #
                                # if module_bonertimer:
                                #     if "!starttimer" in message.lower() and ismod and ismod:
                                #         starttimer(s)
                                #
                                #     elif "!stoptimer" in message.lower() and ismod:
                                #         stoptimer(s)
                                #
                                #     elif "!openbets" in message.lower() and ismod:
                                #         openbets(s)
                                #
                                #     elif "!closebets" in message.lower() and ismod:
                                #         closebets(s)
                                #
                                #     elif message.lower() == "!betstats":
                                #         betstats(s)
                                #
                                #     elif "!bet" in message.lower():
                                #         bet(s, displayname, message)
                                #
                                #     elif "!mybet" in message.lower():
                                #         mybet(s, displayname)
                                #
                                #     elif "!clearbets" in message.lower() and ismod:
                                #         clearbets(s)
                                #
                                #     elif "!addbet" in message.lower() and ismod:
                                #         addbet(s, message)
                                #
                                #     elif ("!rembet" or "!removebet") in message.lower() and ismod:
                                #         removebet(s, message)
                                #
                                #     elif "!currentboner" in message.lower():
                                #         currentboner(s)
                                #
                                #     elif "!brokenboner" in message.lower():
                                #         brokenboner(s)
                                #
                                #     elif "!setboner" in message.lower():
                                #         setboner(s, message)
                                #
                                #     elif "!addending" in message.lower():
                                #         addending(s, message)
                                #
                                #     elif "!timer" in message.lower():
                                #         timer(s)
                                #
                                #     elif "!resettimer" in message.lower() and ismod:
                                #         resettimer(s)
                                #
                                #     elif "!fidwins" in message.lower() and ismod:
                                #         fidwins(s)
                                #
                                #     elif "!winner" in message.lower() and ismod:
                                #         winner(s, message)
                                #
                                # if module_questions:
                                #     if message == "!question" and "!question" not in comlimits:
                                #         threading.Timer(15, command_limiter, ['!question']).start()
                                #         comlimits.append('!question')
                                #         question(s, message)
                                #
                                #     elif "!addquestion" in message and ismod:
                                #         add_question(s, message)
                                #
                                #     elif "!removequestion" in message and ismod:
                                #         threading.Timer(5, command_limiter, ['!removequestion']).start()
                                #         comlimits.append('!removequestion')
                                #         remove_question(s, message)
                                #
                                # if "!bot" in message.lower():
                                #     send_message("This bot is made by Bastixx669. Feel free to message him with "
                                #                  "questions, idea's or cookies!")
                                #
                                # if module_conversion:
                                #     if "!convert" in message.lower():
                                #         convert(s, message)
                                #
                                # if module_rimmods:
                                #     if "!linkmod" in message.lower() and "!linkmod" not in comlimits:
                                #         threading.Timer(15, command_limiter, ['!linkmod']).start()
                                #         comlimits.append('!linkmod')
                                #         linkmod(s, message)
                                #
                                # if module_SongSuggestions:
                                #     if "!suggest" in message.lower() and "!suggest" not in comlimits:
                                #         threading.Timer(10, command_limiter, ['!linkmod']).start()
                                #         comlimits.append('!linkmod')
                                #         suggest(s, message)
                                #     elif "!clearsuggestions" in message.lower() and ismod:
                                #         clearsuggestions(s)

                                if message.lower() == '!restart' and username == 'bastixx669':
                                    nopong()

                                elif "!module" in message.lower() and username == 'bastixx669':
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
                                                            send_message("Module already enabled.")
                                                            var_break = True
                                                    templist.append(lineinfile)
                                                f.seek(0)
                                                for lineinfile in templist:
                                                    f.write(lineinfile)
                                            if not var_break:
                                                send_message(f"Module {keyword} enabled.")
                                                nopong()
                                        except Exception as errormsg:
                                            errorlog(errormsg, "module/enable", message)
                                            send_message("Error enabling this module.")
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
                                                            send_message("Module already disabled.")
                                                            var_break = True
                                                    templist.append(lineinfile)
                                                f.seek(0)
                                                for lineinfile in templist:
                                                    f.write(lineinfile)
                                            if not var_break:
                                                send_message(f"Module {keyword} disabled.")
                                                nopong()
                                        except Exception as errormsg:
                                            errorlog(errormsg, "module/disable", message)
                                            send_message("Error disabling this module.")

                        for l in parts:
                            if "End of /NAMES list" in l:
                                modt = True
                                print(">>>Bot ready in channel: %s" % CHANNEL.decode())
                                logger('>>>Bot', f'Bot ready in channel {CHANNEL.decode()}', False, True)
                                print(">>>modules loaded: %s" % ", ".join(modules.keys()))

        except Exception as errormsg:
            try:
                errorlog(errormsg, 'Main()', temp)
            except Exception:
                errorlog(errormsg, 'Main()', '')


main()
