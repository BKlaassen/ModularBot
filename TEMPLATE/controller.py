from ModularBot import bot
from Modules.Required import Database as database
import multiprocessing

bots = dict()

if __name__ == '__main__':
    mp.set_start_method('spawn')
    database.load_database("controller")
    for element in getallfromdb("bots"):
        bots.update(element['name']=dict('config'=element['config_path'])
    for name in bots.keys():
        bots.update(name=botStart(bots[name], name))

    while True:
        dead = filter(lambda x: not bots[x]['process'].is_alive(), bots.keys())
        if not dead:
            for name in dead:
                print("Bot for Channel %s has died" % name)
                bots.update(name=botStart(bots[name], name))



def botstart(bot, name):
    parent, child = multiprocessing.Pipe()
    bot.update('pipe'=parent)
    process = Process(target=ModularBot.bot(), args=(bot['config'], child, ), Name=name)
    bot.update('process'=process)
    process.start()
    return bot
