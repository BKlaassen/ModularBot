from ModularBot import bot
from Modules.Required import Database as database
import multiprocessing

bots = dict()
TIMEOUT = 60

helpDict = {"add": "Adds another bot to the Database, requires a given name", "exit": "Closes all bots and exits the controller",
    "help": "Displays Commandlist or if command given details on the command",
    "lastChat": "Displays the last Chat received by the given Bot to check continued connection to twitch", "remove": "Removes bot from the Bot Database",
    "start": "Starts bot with given name", "status": "Displays Status of the given bot", "stop": "Stops the given bot"}

if __name__ == '__main__':
    mp.set_start_method('spawn')
    database.load_database("controller")
    for element in getallfromdb("bots"):
        bots.update(element['name']=dict('config'=element['config_path'])
    for name in bots.keys():
        bots.update(name=botStart(bots[name], name))

    while True:
        dead = filter(lambda x: aliveCheck(bots, x), bots.keys())
        if dead:
            for name in dead:
                print("Bot for Channel %s has died" % name)
                bots.update(name=botStart(bots[name], name))
        piped = filter(lambda x: pipeCheck(bots, x), bots.keys())
        if piped:
            for name in piped:
                print("There is something stuck in the pipe of %s: %s"% name bots[name]['pipe'].recv())
        try:
            line = sys.stdin.readline()
        except KeyboardInterrupt:
            break

        if 'exit' in line[:4]:
            break

        elif 'restart' in line[:7]:
            lsplit = line.split(" ")
            if len(lsplit)<2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                print("Restart requires a valid bot name to be executed.")
            else:
                if lsplit[1] == 'all':
                    for x in bots.keys():
                        bots.update(lsplit[1]=botStop(bots[x], x))
                        bots.update(lsplit[1]=botStart(bots[x], x))
                else:
                    bots.update(lsplit[1]=botStart(bots[lsplit[1]], lsplit[1]))
                    bots.update(lsplit[1]=botStop(bots[lsplit[1]], lsplit[1]))

        elif 'stop' in line[:5]:
            lsplit = line.split(" ")
            if len(lsplit)<2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                print("Stop requires a valid bot name to be executed.")
            else:
                if lsplit[1] == 'all':
                    for x in bots.keys():
                        bots.update(lsplit[1]=botStop(bots[x], x))
                else:
                    bots.update(lsplit[1]=botStop(bots[lsplit[1]], lsplit[1]))

        elif 'start' in line[:6]:
            lsplit = line.split(" ")
            if len(lsplit)<2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                print("Start requires a valid bot name to be executed.")
            else:
                if lsplit[1] == 'all':
                    for x in bots.keys():
                        bots.update(lsplit[1]=botStart(bots[x], x))
                else:
                    bots.update(lsplit[1]=botStart(bots[lsplit[1]], lsplit[1]))

        elif 'help' in line[:4]:
            lsplit = line.split(" ")
            if len(lsplit)<2:
                print("Available Commands are: add, exit, help, lastChat, remove, start, status, stop")
            else:
                if lsplit[1] in helpDict.keys():
                    print(helpDict[lsplit[1]])
                else:
                    print("Available Commands are: add, exit, help, lastChat, remove, start, status, stop")

        elif 'lastChat' in line[:8]:
            lsplit = line.split(" ")
            if len(lsplit)<2 or (not lsplit[1] in bots.keys() and not lsplit[1] == 'all'):
                print("lastChat requires a valid bot name to be executed.")
            else:
                if lsplit[1] == 'all':
                    for x in bots.keys():
                        bots[x]['pipe'].send("lastChat")
                        if bots[x]['pipe'].poll(TIMEOUT):
                            message = bots[x]['pipe'].recv()
                            print("Last Message of bot %s:" % bots[x]['name'] + message)
                        else:
                            print("%s does not answer right now, consider restarting it." % bots[x]['name'])
                else:
                    bots[lsplit[1]]['pipe'].send("lastChat")
                    if bots[lsplit[1]]['pipe'].poll(TIMEOUT):
                        message = bots[lsplit[1]]['pipe'].recv()
                        print("Last Message of bot %s:" % bots[lsplit[1]]['name'] + message)
                    else:
                        print("%s does not answer right now, consider restarting it." % bots[lsplit[1]]['name'])
        else:
            print('"%s" is not a recognised command.' % message)


for name in bots.keys:
    bots.update(name=botStop(bots[name], name))
sys.exit(0)

def botStop(bot, name):
    bot.update('pipe'=None)
    bot['process'].terminate()
    if bot['process'].join(TIMEOUT) is None:
        bot['process'].kill()
    bot.update('process'=None)
    return bot


def botStart(bot, name):
    parent, child = multiprocessing.Pipe()
    bot.update('pipe'=parent)
    process = Process(target=ModularBot.bot(), args=(bot['config'], child, ), Name=name)
    bot.update('process'=process)
    process.start()
    return bot


def aliveCheck(bots, key):
    proc = bots[key].get('process', None)
    if not proc == None:
        return not proc.is_alive()
    return False


def pipeCheck(bots, key):
    proc = bots[key].get('pipe', None)
    if not proc == None:
        return not proc.poll(0)
    return False
