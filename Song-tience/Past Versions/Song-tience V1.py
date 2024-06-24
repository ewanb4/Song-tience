import os
import base64
from dotenv import load_dotenv
from requests import post, get # Allows sending a post request
import json
import sqlite3
import spotipy
from pprint import pprint


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

def get_user_auth():
    url = 'https://accounts.spotify.com/authorize?'
    query = ({
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'show_dialog': True
        })
    
    result =  get(url,query)
    
    return result


def get_access_token():
    auth_string = client_id + ":" + client_secret 
    #Authorisation includes Client ID and the Client Secret
    
    auth_bytes = auth_string.encode("utf-8")
    # String needs to be encoded and here UTF-8 us used
    
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    # Returns base 64 object needed for passing headers whens requesting
    
    scope = 'user-read-private,user-read-email'
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials",
            "scope": scope,
            }
    result = post(url, headers=headers, data=data) 
    json_result = json.loads(result.content) # Turns string of results into dictionary
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return{"Authorization": "Bearer " + token}

def get_profile(token):
    url = "https://api.spotify.com/v1/me"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    return result.content
    
    

def search_for_playlist(token, username):
    url = f"https://api.spotify.com/v1/users/{username}/playlists/"
    headers = get_auth_header(token)
    query = f"q{username}&type=track"
    # f string allows direct variable insertion 
    
    query_url = url + "?" + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["items"]
    if len(json_result) == 0:
        print("no playlists exist")
        return None
    
    return json_result

def get_playlist_tracks(token, playlists):
    
    
    for playlist in playlists:
        playlist_id = playlist["id"]
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = get_auth_header(token)
        songs = get(url, headers=headers)
        json_songs = json.loads(songs.content)["items"]
        return json_songs
        
    
token = get_access_token()
playlists = search_for_playlist(token, "jlof5ok09g8ajgspo6ojm6z88")

# pprint(playlists)

tracks = get_playlist_tracks(token, playlists)


for track in tracks:
    print(track['track']['name'])

# for playlist in playlists:
#     print(playlist["name"])    
#     print(playlist["id"])
#     playlist_ref = playlist["href"]
#     print("")
    

    
    
    
    
    
    