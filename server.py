import os

from flask import (
    Flask,
    render_template,
    session,
    request,
    redirect,
    url_for,
    flash,
)

# from flask_oauth import OAuth
from spotipy import Spotify, CacheHandler
from spotipy.oauth2 import SpotifyOAuth

SPOITFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")


class CacheSessionHandler(CacheHandler):
    def __init__(self, session, token_key):
        self.token_key = token_key
        self.session = session

    def get_cached_token(self):
        return self.session.get(self.token_key)

    def save_token_to_cache(self, token_info):
        self.session[self.token_key] = token_info
        session.modified = True


app = Flask(__name__)
app.secret_key = "DEV"
oauth_manager = SpotifyOAuth(
    client_id=SPOITFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri="http://localhost:5000",
    scope="user-read-email playlist-read-private playlist-read-collaborative",
    cache_handler=CacheSessionHandler(session, "spotify_token"),
)


# oauth = OAuth()
# spotify_app = oauth.remote_app(
#     "spotify",
#     consumer_key=SPOITFY_CLIENT_ID,
#     consumer_secret=SPOTIFY_CLIENT_SECRET,
#     request_token_url=None,
#     access_token_url="https://accounts.spotify.com/api/token",
#     authorize_url="https://accounts.spotify.com/authorize",
#     request_token_params={
#         "response_type": "code",
#         "scope": "user-read-email playlist-read-private playlist-read-collaborative",
#     },
#     access_token_method="POST",
# )


@app.route("/")
def homepage():
    jinja_env = {}

    if request.args.get("code") or oauth_manager.validate_token(
        oauth_manager.get_cached_token()
    ):
        oauth_manager.get_access_token(request.args.get("code"))
        return redirect("/spotify-info")

    return render_template(
        "index.html", spotify_auth_url=oauth_manager.get_authorize_url()
    )


@app.route("/spotify-info")
def show_spotify_info():
    if not oauth_manager.validate_token(oauth_manager.get_cached_token()):
        return redirect("/")

    sp = Spotify(auth_manager=oauth_manager)

    return render_template("spotify-info.html", spotify=sp)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, use_debugger=True)
