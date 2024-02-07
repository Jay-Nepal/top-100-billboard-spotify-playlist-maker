from flask import Flask, request, redirect, session, url_for, render_template
from spotipy import Spotify, oauth2
import os
from dotenv import load_dotenv
import secrets

load_dotenv()

# The developer ID and credentials from Spotify. Store them in a .env file in root directory
SPOTIPY_CLIENT_ID = os.getenv('spotify_id')
SPOTIPY_CLIENT_SECRET = os.getenv('spotify_secret')
SPOTIPY_REDIRECT_URI = os.getenv('redirect_url')
# Scopes needed to create playlists through API
SPOTIPY_SCOPE = 'playlist-modify-public playlist-modify-private'

# Spotipy OAuth configuration
sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID,
                               SPOTIPY_CLIENT_SECRET,
                               SPOTIPY_REDIRECT_URI,
                               scope=SPOTIPY_SCOPE)

# Flask configuration
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16) # Change this to a secure secret key


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    # This presents the user with Oauth for Spotify authorization
    auth_url = sp_oauth.get_authorize_url()

    return redirect(auth_url)


@app.route('/callback')
def callback():
    # Get the auth code after successful authorization
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    # Storing it in session info so it can be used later
    session['token_info'] = token_info

    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    token_info = session.get('token_info')
    # Send user back to index page if they aren't logged in and try accessing profile
    if not token_info:
        return redirect(url_for('index'))

    sp = Spotify(auth=token_info['access_token'])
    user_profile = sp.current_user()

    return f'Logged in as {user_profile["display_name"]}'


if __name__ == '__main__':
    app.run(debug=True)
