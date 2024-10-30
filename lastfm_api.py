import requests

def get_track_tags(artist, track, lastfm_api_key):
    endpoint = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getInfo",
        "artist": artist,
        "track": track,
        "api_key": lastfm_api_key,
        "format": "json"
    }
    response = requests.get(endpoint, params=params)
    response.raise_for_status()
    return response.json()["track"]["toptags"]["tag"]
