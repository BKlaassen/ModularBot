import requests
import os

from Modules.Required import Database, Errorlog, Sendmessage


def load_followergoals(folder):
    global goals
    goals = []
    try:
        with open(f'{os.path.dirname(os.path.dirname(__file__))}/{folder}/files/Goals.txt', 'r') as f:
            for line in f:
                goals.append(line)
    except Exception as errormsg:
        Errorlog.errorlog(errormsg, "load_followergoals()", '')


def followergoal(channel_id, channel, client_id):
    try:
        url = f'https://api.twitch.tv/helix/users/follows?to_id={channel_id}'
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        total = r["total"]
        if int(total) % 250 == 0 and total not in goals:
            Sendmessage.send_message(f"@{channel.decode()} congrats on {total} followers!")
            goals.append(total)
    except Exception as errormsg:
        Errorlog.errorlog(errormsg, "followergoals()", "")