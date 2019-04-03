import random

from Required.Errorlog import errorlog
from Required.Sendmessage import send_message
from Errors import InsufficientParameterException


def paddle(displayname, message):
    messagesplit = message.split(" ")
    if len(messagesplit) != 2:
        raise InsufficientParameterException
    randint = random.randint(1, 20)
    if randint == 1:
        send_message("/timeout %s 5 Get paddled!" % messagesplit[1])
        send_message("%s got paddled so hard by %s they need a few seconds to recover..." %
                     (messagesplit[1].strip("@"), displayname))
    else:
        send_message("%s gets a paddling from %s! andyt90bat" %
                     (messagesplit[1].strip("@"), displayname))
