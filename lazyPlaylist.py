import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from num2words import num2words
from flask import Flask, request, url_for, session, redirect, render_template

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Place Holder'
app.secret_key = 'Place Holder'

TOKEN_INFO = 'token_info'

@app.route('/')

def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')

def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('lazy_playlist', external = True))


@app.route('/lazyPlaylist')

def lazy_playlist():
    try:
        token_info = get_token()
    except:
        print("User not logged in")
        return redirect("/")
    
    lazyPlaylist = None
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playlists = sp.current_user_playlists()['items']
    userID = sp.current_user()['id']
    currentPlaylist = []

    for playlist in current_playlists :
        if(playlist['name'] == "Creation of Laziness"):
            lazyPlaylist = playlist['id']
            lazyPlaylistItems = sp.playlist_items(lazyPlaylist)
            for song in lazyPlaylistItems['items']:
                uri = song['track']['id']
                currentPlaylist.append(uri)

    if(lazyPlaylist == None):
        creator = sp.user_playlist_create(userID,"Creation of Laziness",True)
        lazyPlaylist = creator['id']

    songURIS = []
    top5Tracks = sp.current_user_top_tracks(5,0,"short_term")

    for toptrack in top5Tracks['items']:
        uri = toptrack['id']
        songURIS.append(uri)

    tempList = []
    for newURIS in songURIS:
        if newURIS not in currentPlaylist:
            tempList.append(newURIS)

    userName=sp.current_user()["display_name"]

    if(len(currentPlaylist)) == 0:
        render_template("index.html",holder = "The lazy playlist was created and updated", userName = userName )
    
    if len(tempList) == 0:
        return render_template("index.html", userName = userName, holder = "There are no new songs added to lazy playlist this month :( ")
    
    sp.user_playlist_add_tracks(userID,lazyPlaylist,tempList)
    num = num2words(len(tempList))
    str = num + " songs were added to the lazy playlist, keep up the work ;)"
    return render_template("index.html", userNAME = userName, holder = str)



def get_token():
    token_info = session.get(TOKEN_INFO,None)
    if not token_info:
        redirect(url_for('login', external = False))
    
    now  = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(client_id= "Place Holder",
                        client_secret= "Place Holder",
                        redirect_uri= url_for('redirect_page', _external = True),
                        scope= 'user-library-read user-top-read playlist-read-private playlist-modify-public playlist-modify-private user-read-private'
                        )

app.run(host="0.0.0.0", port=5000,debug=True)
