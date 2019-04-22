import requests
import base64

from Modules.Required.Sendmessage import send_message
from Modules.Required.Errorlog import errorlog
import Modules.Required.Database as Database


def getauthtoken():
    with open("files/token.txt", "r") as f:
        client_id, client_secret = f.read().split(":")

    credentials = f"{client_id}:{client_secret}".encode("utf-8")
    credentials = base64.standard_b64encode(credentials)
    url = 'https://accounts.spotify.com/api/token/'
    headers = {"Authorization": f"Basic {credentials.decode()}", "Content-Type": "application/x-www-form-urlencoded"}
    data = "grant_type=client_credentials"
    r = requests.post(url, data, headers=headers)
    r = r.json()
    token = r["access_token"]
    return token


def songonspotify(song):
    url = f'https://api.spotify.com/v1/search?q={song}&type=track&market=GB&offset=0&limit=1'
    authorisation = f'Bearer {authtoken}'
    headers = {'Authorization': authorisation, 'Accept': 'application/json', 'Content-Type': 'application/json'}
    result = requests.get(url, headers=headers).json()
    try:
        if result["tracks"]["items"]:
            return "Yes"
    except:
        return "No"


def load_suggestions():
    global authtoken
    authtoken = getauthtoken()


def suggest(message):
    try:
        messagesplit = message.split(" ")
        suggestion = messagesplit[1:]
        wrongchars = ['<', '>', '{', '}', '(', ')', '#', '%', '*', '\:', "\"", "|"]
        for elem in wrongchars:
            if elem in suggestion:
                suggestion = suggestion.replace(elem, "")

        suggestion = " ".join(suggestion)
        Database.insertoneindb("SongSuggestions", {"suggestion": suggestion, "on_spotify": songonspotify(suggestion)})
        send_message("Song suggestion registered!")
    except Exception as errormsg:
        send_message("There was an error adding this. Please try again!")
        errorlog(errormsg, "SongSuggestions/suggest()", message)
        raise errormsg


def clearsuggestions():
    result = Database.clearcollection("SongSuggestions")
    if result:
        send_message("List cleared!")
    else:
        send_message("An error occured. Please ask bastixx to check.")

