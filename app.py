from flask import Flask, redirect, request, render_template
from spotify_api import get_authorization_url, get_access_token, run_spotify_api
import os
from dotenv import load_dotenv
import threading
from extensions import socketio

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Your app configurations and routes go here

# Initialize SocketIO with the app
socketio.init_app(app)

# Client configuration
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
lastfm_api_key = os.getenv("LASTFM_API_KEY")
scope = "user-library-read playlist-modify-public playlist-modify-private"
code = None

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/start", methods=["POST"])
def start():
    auth_url = get_authorization_url(client_id, redirect_uri, scope)
    return redirect(auth_url)

@app.route("/callback")
def callback():
    global code  # Use the global variable
    code = request.args.get('code')
    if code:
        access_token = get_access_token(client_id, client_secret, redirect_uri, code)
        # Start the Spotify API run in a background thread
        threading.Thread(target=run_spotify_api, args=(access_token, lastfm_api_key)).start()
        return render_template('callback.html', code=code)
    else:
        return "No authorization code received."

@app.route("/process")
def process():
    if code is None:
        return "No authorization code available. Please authorize first."
    
    access_token = get_access_token(client_id, client_secret, redirect_uri, code)

    # Start the Spotify API run in a background thread
    threading.Thread(target=run_spotify_api, args=(access_token,)).start()

    return "Processing started! You will receive the output once it's done."

if __name__ == "__main__":
    app.run(port=8080, debug=True)
