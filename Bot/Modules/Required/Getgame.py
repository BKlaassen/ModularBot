import requests


def get_current_game(channel_id, CLIENTID):
    url = 'https://api.twitch.tv/kraken/channels/%s/' % channel_id
    headers = {'Client-ID': CLIENTID, 'Accept': 'application/vnd.twitchtv.v5+json'}
    r = requests.get(url, headers=headers).json()
    game = r["game"]
    return game
