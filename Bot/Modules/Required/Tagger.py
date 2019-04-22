from Modules.Modlog import modlog, removedmessage
from Modules.Required.Logger import logger


# def load_tagger(CLIENTID):
#     global clientid
#     clientid = CLIENTID


def tagprivmsg(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value
    ismod = tags.get("mod")
    issub = tags.get("subscriber")
    username = tags.get("display-name")
    userid = tags.get("user-id")

    # message
    try:
        message = lineparts[2].rstrip("\r")
    except:
        message = lineparts[1].rstrip("\r")

    # username. This is only set if the displayname is not set.
    if username == "":
        try:
            username = lineparts[1].split("!")[0]
        except:
            username = "Undefined_username"
    return username, userid, message, issub, ismod


def tagclearchat(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value

    if len(lineparts) > 0:
        duration = tags.get("ban-duration")
    else:
        duration = 0

    userid = tags.get("target-user-id")
    username = lineparts[2]

    # displayname, username = idlookup(userid)
    modlog(duration, userid, username)


def tagclearmsg(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value

    message = lineparts[2]
    username = tags.get("login")
    userid = tags.get("user-id")

    removedmessage(username, userid, message)


def tagusernotice(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value
    message = lineparts[2]
    username = tags.get("display-name")
    ismod = tags.get("mod")
    issub = tags.get("subscriber")
    userid = tags.get("user-id")

    if username == "":
        username = tags.get("login")

    logger(userid, username, message, issub, ismod)


def tagnotice(line):
    tags = {}
    line = line.lstrip("@")
    lineparts = line.split(":")
    temptags = lineparts[0].split(";")
    for tag in temptags:
        key, value = tag.split("=")
        tags[key] = value
    message = lineparts[2]
    logger(0000000, "NOTICE", message, False, False, True)

# Unused for now.
# def taguserstate(line):
#     msgtype = "USERSTATE"
#     return msgtype
