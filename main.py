import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, redirect, session, request
import requests
import os
from dotenv import load_dotenv
from socket import gethostname

load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

app = Flask(__name__)
app.secret_key = "irea11yd0nTcar3"

# This code references heavily from the following Medium article: https://medium.com/@ruixdsgn/a-guide-to-implementing-oauth-authorization-using-spotipy-for-a-playlist-generator-app-6ab50cdf6c3.
# Thanks to ruixdsgn for helping me understand how to implement the Spotify OAuth flow with the Spotipy module, as the docs are pretty confusing and bare regarding this topic.
# I've done it before the dirty way with requests, but trying to use spotipy for the auth is new to me.

HOST = "127.0.0.1"
scope = "playlist-modify-private"
redirect_uri = f"http://{HOST}:5000/callback"

sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)

@app.route("/")
def index():
    return "<a href='/login'>log into Spotify</a>"

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    session["token_info"] = sp_oauth.get_cached_token()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    token_info = sp_oauth.get_access_token(request.args['code'])
    session["token_info"] = token_info
    return redirect("/generate")

@app.route("/generate")
def generate_playlist():
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect("/login")
    
    sp = spotipy.Spotify(auth=token_info["access_token"])

    user = sp.current_user()
    playlist = sp.user_playlist_create(user['id'], 'Test Playlist', public=False, description="This was made with Flask!")
    sp.playlist_add_items(playlist['id'], ["https://open.spotify.com/track/7o2AeQZzfCERsRmOM86EcB?si=7d6f3ab5c80f4004"])
    return "Your playlist should've been created!"


if __name__ == "__main__":
    app.run(debug=True)