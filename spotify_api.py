import os
import pprint as pp
import json
import base64
import requests
from dotenv import load_dotenv

load_dotenv(".env")

client_id = os.getenv("CLIENT_ID")
client_sk = os.getenv("CLIENT_SK")


def client_to_base64(client_id: str, client_sk: str) -> str:
    auth_bytes = f"{client_id}:{client_sk}".encode("utf-8")
    return str(base64.b64encode(auth_bytes), "utf-8")


def get_access_token() -> str:
    headers = {
        "Authorization": f"Basic {client_to_base64(client_id, client_sk)}"
    }
    
    data = {
        "grant_type": "client_credentials"
    }
    
    url = "https://accounts.spotify.com/api/token"
    result = requests.post(url, headers=headers, data=data)
    result = json.loads(result.content)
    
    token = result["access_token"]
    return token


def search_for_artist(access_token: str, artist_name: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    query = f"?q={artist_name}&type=artist&limit=1"
    url = "https://api.spotify.com/v1/search"
    url += query
    
    result = requests.get(url, headers=headers)
    result = json.loads(result.content)
    result = result["artists"]["items"]
    return result


def get_songs_by_artist(access_token: str, artist_id: str):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=HU"
    
    result = requests.get(url, headers=headers)
    result = json.loads(result.content)
    result = result["tracks"]
    return result


if __name__ == "__main__":
    artist_name = "Nótár Mary"
    
    token = get_access_token()
    print("\nAccess token generated.\n")
    
    artists = search_for_artist(token, artist_name)
    if artists:
        print(f"Arstis named: {artist_name} found. ID: {artists[0]['id']}")
    else:
        print(f"Artist named: {artist_name} was not found.")
        exit(0)
    
    tracks = get_songs_by_artist(token, artists[0]['id'])
    
    print('\nTracks:\n')
    for track in tracks:
        print(track.keys())
        pp.pp(
            {
                'name': track['name'], 'id': track['id'], "preview_url": track['preview_url']
            }
        )
