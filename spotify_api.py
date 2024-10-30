import requests
import base64
from urllib.parse import urlencode
from utils import handle_http_errors
from lastfm_api import get_track_tags
from extensions import socketio
from time import sleep 


def get_authorization_url(client_id, redirect_uri, scope):
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri
    }
    return f"{auth_url}?{urlencode(params)}"

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
    return handle_http_errors(lambda: requests.post(endpoint, headers=headers, data=data)).json()["access_token"]

def get_user_saved_tracks(access_token, endpoint="https://api.spotify.com/v1/me/tracks?limit=50&market=FR"):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = handle_http_errors(lambda: requests.get(endpoint, headers=headers)).json()
    return response

def get_all_tracks_ids(response):
    return [(track["track"]["id"], track["track"]["name"], track["track"]["artists"]) for track in response["items"]]


def run_spotify_api(access_token, lastfm_api_key):
    # Fetch user's saved tracks
    tracks = []
    results = get_user_saved_tracks(access_token)
    tracks += get_all_tracks_ids(results)
    while results.get("next"):
        results = get_user_saved_tracks(access_token, results["next"])
        tracks += get_all_tracks_ids(results)

    total_tracks = len(tracks)
    # Emit total number of tracks for progress bar initialization
    socketio.emit('total_tracks', {'total': total_tracks})
    
    tracks_tags = []
    for index, track in enumerate(tracks):
        artist = track[2][0]['name']
        track_name = track[1]

        if artist and track_name:
            # Emit progress (current track number)
            socketio.emit('progress', {
                'current': index + 1, 
                'total': total_tracks,
                'artist': artist,
                'track_name': track_name
                })
            print(f"Processing: {artist} - {track_name}")
            
            # Simulating some delay for each track (optional)
            # sleep(0.5)

            # Get tags for the current track
            tags = get_track_tags(artist, track_name, lastfm_api_key)
            tracks_tags.append((artist, track_name, tags))

    # Save all tracks and tags to a file
    tracks_tags_text = "\n".join(
        f"{track[0]} - {track[1]} - {', '.join(tag['name'] for tag in track[2] if isinstance(tag, dict)) if track[2] else 'No tags available'}"
        for track in tracks_tags
    )
    with open('tracks_tags.txt', 'w', encoding='utf-8') as f:
        f.write(tracks_tags_text)
    
    # Emit completion event
    socketio.emit('processing_complete', {'message': 'Processing complete!'})
