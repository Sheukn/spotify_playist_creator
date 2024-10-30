import requests
import json
from urllib.parse import urlparse, parse_qs, urlencode
import base64
from flask import Flask, redirect, request, render_template_string

app = Flask(__name__)

client_id = "fa5a17778a2d4345903394c6178008b2"
client_secret = "2613fcadd45945e8af063654b99f5045"
redirect_uri = "http://localhost:8080/callback"
scope = "user-library-read playlist-modify-public playlist-modify-private"
lastfm_api_key = "62366faf0dfefe8277e9dbc72598c274"
lastfm_secret = "c200df84bad9e4504dc8541087814436"


# Generate authorization URL
def get_authorization_url(client_id, redirect_uri, scope):
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri
    }
    return f"{auth_url}?{urlencode(params)}"



# Get access token using the authorization code
def get_access_token(client_id, client_secret, redirect_uri, code):
    endpoint = "https://accounts.spotify.com/api/token"
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    try:
        response = requests.post(endpoint, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")



def get_user_saved_tracks(access_token, endpoint="https://api.spotify.com/v1/me/tracks?limit=50&market=FR"):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


# Get all tracks ids
def get_all_tracks_ids(response):
    tracks = response["items"]
    track_ids = []
    for track in tracks:
        track_ids.append((track["track"]["id"], track["track"]["name"], track["track"]["artists"]))
    return track_ids


# Get track artists' ids
def get_track_artist_info(tracks : tuple, access_token, offset=0):
    endpoint = "https://api.spotify.com/v1/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    ids = ",".join([track[0] for track in tracks[offset:offset+50]])
    market = "FR"
    endpoint += f"?ids={ids}&market={market}"
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        tracks = response.json()["tracks"]
        # Create set of artists
        set_artists = set()
        for track in tracks:
            set_artists.update(track["artists"][0]["id"])
        return set_artists
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


# Get artist genres
def get_artist_genres(artists_set, access_token, offset=0):
    endpoint = f"https://api.spotify.com/v1/artists"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    ids = ",".join(list(artists_set)[offset:offset+50])
    endpoint += f"?ids={ids}"
    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        artists = response.json()["artists"]
        tab_genres = []
        for artist in artists:
            tab_genres.append((artist['name'],artist["id"], artist["genres"]))
        return tab_genres
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


# Get lastfm tracks tags
def get_lastfm_track_tags(artist, track):
    endpoint = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.gettoptags",
        "artist": artist,
        "track": track,
        "api_key": lastfm_api_key,
        "format": "json"
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")


def process(code: str):
    token = get_access_token(client_id, client_secret, redirect_uri, code)

    # Fetch user's saved tracks
    tracks_ids = []
    print("Fetching user saved tracks (call 1)")
    results = get_user_saved_tracks(token)
    tracks_ids += get_all_tracks_ids(results)
    count = 1
    while len(results["items"]) > 0:
        tracks_ids += get_all_tracks_ids(results)
        if results["next"] != None:
            count += 1
            results = get_user_saved_tracks(token, results['next'])
        else:
            break

    # Fetch track artists' info
    track_artists_set = set()
    offset = 0
    count = 0
    while offset < len(tracks_ids):
        count += 1
        track_artists_set.update(get_track_artist_info(tracks_ids, token, offset))
        offset += 50
    
    # Fetch artist genres
    artist_genres = []
    offset = 0
    count = 0
    while offset < len(track_artists_set):
        count += 1
        artist_genres.extend(get_artist_genres(track_artists_set, token, offset))
        offset += 50
    
    




    

@app.route("/")
def home():
    return render_template_string("""
        <html>
            <head><title>Spotify Authorization</title></head>
            <body>
                <h2>Click OK to start Spotify authorization process:</h2>
                <form action="/start" method="POST">
                    <input type="submit" value="OK" />
                </form>
            </body>
        </html>
    """)

@app.route("/start", methods=["POST"])
def start():
    auth_url = get_authorization_url(client_id, redirect_uri, scope)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get('code')
    if code:
        process(code)
        return "Authorization and data retrieval complete. Check the console for details."
    else:
        return "No authorization code received."

if __name__ == "__main__":
    app.run(port=8080)
