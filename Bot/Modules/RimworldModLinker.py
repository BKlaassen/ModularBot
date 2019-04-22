from bs4 import BeautifulSoup
import requests
import re
import json

from Modules.Required.Errorlog import errorlog
from Modules.Required.Sendmessage import send_message


def load_mod(STEAMAPIKEY):
    global steamAPIkey
    steamAPIkey = STEAMAPIKEY


def linkmod(message):
    messagesplit = message.split(" ")
    searchterm = "+".join(messagesplit[1:])

    try:
        r = requests.get(f'https://steamcommunity.com/workshop/browse/?appid=294100&searchtext={searchterm}&childpublishedfileid=0&browsesort=textsearch&section=items&requiredtags[]=Mod')
        webpage = r.text
        soup = BeautifulSoup(webpage, "html.parser")
        # for item in soup.find_all(re.compile("SharedFileBindMouseHover\(.+({.+})")):
        for item in soup.find_all("script"):
            itemtext = re.sub('[\\r\\t\\n]', '', item.text)
            if 'SharedFileBindMouseHover' in itemtext:
                item = re.search('({.*})', itemtext)
                jsonitem = json.loads(item.group(1))
                modtitle = jsonitem['title']
                modid = jsonitem['id']
                break

        try:
            send_message(f'Found the mod: {modtitle} https://steamcommunity.com/sharedfiles/filedetails/?id={modid}')
        except:
            send_message("No mods found.")
    except Exception as errormsg:
        errorlog(errormsg, "ModSearch()", "")
