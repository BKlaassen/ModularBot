from ModularBot import bot
from Modules.Required import Database as database
import multiprocessing

bots = dict()

if __name__ == '__main__':
    mp.set_start_method('spawn')
    database.load_database("controller")
    for element in getallfromdb("bots"):
        bots.update(element['name']=[element['folder']])
