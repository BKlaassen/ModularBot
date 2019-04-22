import requests
from Modules.Required.Errorlog import errorlog


def load_apicalls(CLIENTID, CHANNELID):
    global channel_id
    global client_id
    channel_id = CHANNELID
    client_id = CLIENTID


def follows(userid):
    try:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid, channel_id)
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()

        # Returns data about when x follows y, or {} if x doesnt follow y
        return r.data[0]
    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/follows()', "Userid:" + userid)


def idtousername(userid):
    username = ""
    try:
        url = 'https://api.twitch.tv/helix/users?id=' + userid
        headers = {'Client-ID': client_id, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        result = requests.get(url, headers=headers).json()
        username = result["data"][0]["display_name"]
        if username == "":
            return username
        else:
            username = result["data"][0]["login"]
            return username

    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/idtousername()', "Displayname:" + username)


def usernametoid(username):
    userid = ""
    try:
        url = 'https://api.twitch.tv/helix/users?login=' + username
        headers = {'Client-ID': client_id, 'Accept': 'application/json', 'Content-Type': 'application/json'}
        result = requests.get(url, headers=headers).json()
        userid = result["data"][0]["id"]
        return userid

    except Exception as errormsg:
        errorlog(errormsg, 'APICalls/usernametoid()', "Userid:" + userid)
