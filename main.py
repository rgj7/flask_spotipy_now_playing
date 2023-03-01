import datetime
from flask import Flask, session, request, redirect, url_for
from flask_session import Session
import logging
import os
import redis
import shortuuid
import spotipy

app = Flask(__name__)
redis_obj = redis.from_url(os.getenv('REDIS_URL'))
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
Session(app)

logger = logging.getLogger()


@app.route('/')
def index(): 
    if not session.get("username"):
        session["username"] = shortuuid.uuid()[:7]
        logger.debug(f"session set. username = {session['username']}")

    cache_handler = spotipy.cache_handler.RedisCacheHandler(redis_obj, session["username"])
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope='user-read-currently-playing',
        cache_handler=cache_handler,
        show_dialog=True
    )

    token_info = auth_manager.validate_token(cache_handler.get_cached_token())
    if token_info is None:
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'
    logger.debug(f"token_info for '{session['username']}': {token_info}")

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    display_name = spotify.me()["display_name"]
    return f"""
        <h2><h2>Signed in as: {display_name} <small><a href="{ url_for('sign_out' )}">[sign out]<a/></small></h2>
        <a href="{url_for('currently_playing', username=session['username'])}">show currently playing</a>
    """

@app.route('/callback')
def callback():
    if not session.get("username"):
        logger.warning("session username is not set")
        return redirect(url_for("index"))
    cache_handler = spotipy.cache_handler.RedisCacheHandler(redis_obj, session["username"])
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope='user-read-currently-playing',
        cache_handler=cache_handler
    )
    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"), as_dict=False)
        logger.debug("access token created")
        return redirect(url_for("index"))
    logger.warning("no code was found in query")
    return redirect(url_for("index"))

@app.route('/sign_out')
def sign_out():
    redis_obj.delete(session["username"])
    session.pop("username")
    return redirect(url_for("index"))

@app.route('/currently_playing/<username>')
def currently_playing(username):
    cache_handler = spotipy.cache_handler.RedisCacheHandler(redis_obj, username)
    auth_manager = spotipy.oauth2.SpotifyOAuth(
        scope='user-read-currently-playing',
        cache_handler=cache_handler
    )
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        logger.error(f"failed to validate token for {username}")
        return f"Failure to validate token."
    
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    track = spotify.current_user_playing_track()
    if not track is None:  # and track["is_playing"]:
        song = track["item"]["name"]
        artists = ", ".join([artist["name"] for artist in track["item"]["artists"]])
        return f"Currently Playing: {artists} - {song}"
    return f"No track currently playing."


application = app

if __name__ == '__main__':
    app.run()