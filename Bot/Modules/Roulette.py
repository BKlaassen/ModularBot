import random
import time

from Modules.Required.Sendmessage import send_message
from Modules.Required.Errorlog import errorlog


def roulette(username):
    try:
        randint = random.randint(1, 6)
        send_message("%s spins the gun and pulls the trigger.." % username)
        time.sleep(1)
        if randint == 1:
            send_message("The gun fires and %s drops dead to the ground!" % username)
            send_message("/timeout %s 1" % username)
        else:
            send_message("A CLICK can be heard as nothing happends. %s lives!" % username)
    except Exception as errormsg:
        errorlog(errormsg, "roulette()", '')
