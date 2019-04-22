import requests

from Modules.Required import Errorlog, Sendmessage

def pun():
    try:
        joke = requests.get('https://icanhazdadjoke.com/', headers={"Accept": "application/json", "User-Agent": ""}).json()
        Sendmessage.send_message(joke['joke'])
    except Exception as errormsg:
        Errorlog.errorlog(errormsg, "pun()", "")