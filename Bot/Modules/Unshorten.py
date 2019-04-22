from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message
import requests


def unshorten(shorturl):
    try:
        url = f'https://unshorten.me/json/https://{shorturl}'
        r = requests.get(url).json()
        longurl = r["resolved_url"]
        if shorturl not in longurl and longurl != "":
            send_message(f"This link expands to: {longurl}")
    except Exception as errormsg:
        errorlog(errormsg, "unshorten()", "")
