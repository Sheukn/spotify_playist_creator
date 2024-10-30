from flask import Blueprint, render_template, request, redirect
from app.api.spotify_api import get_authorization_url, get_access_token, run_spotify_api
from app.extensions import socketio
import os
import threading

# Define a blueprint for the main app routes
main = Blueprint('main', __name__)

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
lastfm_api_key = os.getenv("LASTFM_API_KEY")
scope = "user-library-read playlist-modify-public playlist-modify-private"
code = None

@main.route("/")
def home():
    return render_template('home.html')

@main.route("/start", methods=["POST"])
def start():
    auth_url = get_authorization_url(client_id, redirect_uri, scope)
    return redirect(auth_url)

@main.route("/callback")
def callback():
    global code
    code = request.args.get('code')
    if code:
        access_token = get_access_token(client_id, client_secret, redirect_uri, code)
        threading.Thread(target=run_spotify_api, args=(access_token, lastfm_api_key)).start()
        return render_template('callback.html', code=code)
    else:
        return "No authorization code received."

@main.route("/process")
def process():
    if code is None:
        return "No authorization code available. Please authorize first."

    access_token = get_access_token(client_id, client_secret, redirect_uri, code)
    threading.Thread(target=run_spotify_api, args=(access_token,)).start()
    return "Processing started! You will receive the output once it's done."
