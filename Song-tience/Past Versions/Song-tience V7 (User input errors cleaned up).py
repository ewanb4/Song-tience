import os
import base64
from dotenv import load_dotenv # Allows retrieval from .env file
from requests import post, get # Allows sending a post request
import json # Needed to load results of post/get
import sqlite3
from pprint import pprint # Useful for debugging


load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
username = os.getenv("SPOTIFY_USERNAME")


# def get_user_auth():
#     url = 'https://accounts.spotify.com/authorize?'
#     query = ({
#         'response_type': 'code',
#         'client_id': client_id,
#         'redirect_uri': redirect_uri,
#         'show_dialog': True
#         })
    
#     result = get(url,query)
#     pprint(result.content)
#     json_result = json.loads(result.content)
#     return json_result


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

def get_user_profile(token,username):
    url = f"https://api.spotify.com/v1/users/{username}"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    return json_result

def search_for_playlist(token, username):
# Uses the username of the user to find the playlists in their account (currently only works for public playlists)
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

def get_playlist_tracks(token, playlists, playlist_selection):
# Retrieves songs using the playlist ID
    loop_count = 1
    offset = 0
    
    while True:

        playlist_id = playlists[playlist_selection-1]["id"]
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks/?"
        query = f"q{playlist_id}&type=track&offset={offset}"
        headers = get_auth_header(token)
        songs = get(url+query, headers=headers)
        json_songs = json.loads(songs.content)["items"]
        json_temp = json_songs
        
        if len(json_songs) < 100 and loop_count == 1:
            return json_songs
        
        elif loop_count == 1:
            json_song_store = json_temp
            loop_count += 1
            offset += 100
            print("fetching playlist items...\n")
            
        elif len(json_songs) < 1 and loop_count > 1:
            return json_song_store

        else:
            json_song_store = json_song_store + json_temp
            # print(json_song_store)
            offset+=100
            loop_count += 1
            
    
# auth = get_user_auth()
# user_id = get_user_profile(token, username)
# print(user_id)


## Main Code
if __name__ == "__main__":
    
    token = get_access_token()
    
    con = sqlite3.connect("Song-tience Database.db") # Creates a connection to database, creating one if it doesnt exist
    cur = con.cursor() # Creates a database cursor to execute and fetch SQL queries
    #cur.execute("CREATE TABLE playlist(number, title, artist)")
    
    
    exit_code = False
    while exit_code == False:
        
        playlists = search_for_playlist(token, username)
        
        playlist_selection = 0
        while playlist_selection < 1 or playlist_selection > len(playlists):
            counter = 1
            for playlist in playlists:
                print(counter, "-", playlist["name"])    
                counter += 1
            
            try:
                playlist_selection = int(input("\nPlease choose which playlist to retrieve songs: "))
                print("")
            
                if playlist_selection < 1 or playlist_selection > len(playlists):
                    print("Out of index range, please choose a valid index\n ")
                    
                else:
                    break
                
            except ValueError:
                print("Invalid response")
                playlist_selection = 0
                
            
                
        
        tracks = get_playlist_tracks(token, playlists, int(playlist_selection))
        
        
        song_counter = 1
        for track in tracks:
            song_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            print(song_counter,"-",song_name,'-',artist_name)
            
            data_retrieved = [(song_counter), (song_name), (artist_name)]
            cur.execute("INSERT INTO playlist VALUES(?, ?, ?)",data_retrieved)
            con.commit()
            # Inserts the data retrieved into a database using SQL
            
            # for row in cur.execute("SELECT number, title, artist FROM playlist"):
            #     print(row)
            # Use above code in console to output database
                
            song_counter += 1
    
        response = False
        
        while response == False:
            print("")
            continue_search = str(input("Would you like to search again? (Y/N) ")).lower()
            
            if continue_search == 'y':
                response = True
            
            elif continue_search == 'n':
                response = True
                exit_code = True
                
            else:
                print("\nInvalid Response.")
        
        
        
        
        
        
        