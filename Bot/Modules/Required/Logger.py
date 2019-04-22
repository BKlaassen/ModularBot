from unidecode import unidecode
import time
import os

from Modules.Required.Errorlog import errorlog
from Modules.Required.Database import insertoneindb


def logger(userid, displayname, message, issub, ismod, issystem=False):
    try:
        timestamp = str(time.strftime("%d-%m-%Y %H:%M:%S"))
        print(f"[{timestamp}] {displayname}: {message}")
        message = unidecode(message)
        insertoneindb("Chatlog", {"timestamp": timestamp, "displayname": displayname, "userid": userid,
                                  "message": message, "sub": issub, "mod": ismod, "systemmessage": issystem})

        return timestamp
    except Exception as errormsg:
        errorlog(errormsg, "Logger", message)


def logtofile(folder, func, line):
    now = str(time.strftime("%H:%M:%S"))
    with open(f"{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Errorlog.txt", "a") as f:
        f.write(f"[{now}] [{func}]: {line}")
