import aiohttp
import asyncio
import pprint as pp
import os
import base64
import json
import requests
from dotenv import load_dotenv

load_dotenv(".env")

client_id = os.getenv("CLIENT_ID")
client_sk = os.getenv("CLIENT_SK")


def client_to_base64(client_id: str, client_sk: str) -> str:
    auth_bytes = f"{client_id}:{client_sk}".encode("utf-8")
    return str(base64.b64encode(auth_bytes), "utf-8")


def spot_get_access_token() -> str:
    headers = {"Authorization": f"Basic {client_to_base64(client_id, client_sk)}"}

    data = {"grant_type": "client_credentials"}

    url = "https://accounts.spotify.com/api/token"
    result = requests.post(url, headers=headers, data=data)
    result = json.loads(result.content)

    token = result["access_token"]
    return token


BASE_URL = "https://api.spotify.com/v1"
TOKEN = spot_get_access_token()


headers = {"Authorization": f"Bearer {TOKEN}"}


async def fetch(session, url, params=None):
    async with session.get(url, headers=headers, params=params) as response:
        return await response.json()


async def get_artist_albums(session, artist_id):
    albums = []
    url = f"{BASE_URL}/artists/{artist_id}/albums"
    params = {"include_groups": "album,single", "limit": 50, "offset": 0}

    while url:
        data = await fetch(session, url, params)
        albums.extend(data["items"])
        url = data.get("next")  # Next page
        params = None  # Params only needed for the first call
    return albums


async def get_album_tracks(session, album_id):
    tracks = []
    url = f"{BASE_URL}/albums/{album_id}/tracks"
    params = {"limit": 50, "offset": 0}

    while url:
        data = await fetch(session, url, params)
        tracks.extend(data["items"])
        url = data.get("next")  # Next page
        params = None  # Params only needed for the first call
    return tracks


async def get_all_artist_tracks(artist_id):
    all_tracks = []

    async with aiohttp.ClientSession() as session:
        # First fetch all albums
        albums = await get_artist_albums(session, artist_id)
        # Create tasks for fetching album tracks
        tasks = [get_album_tracks(session, album["id"]) for album in albums]
        # Await all tasks
        tracks = await asyncio.gather(*tasks)

    for album_tracks in tracks:
        all_tracks.extend(album_tracks)

    # Remove duplicates by track ID
    unique_tracks = {track["id"]: track for track in all_tracks}
    return list(unique_tracks.values())


# Main event loop

artist_id = "6YyFqdyYBAylLQK6Eemz94"  # Notár Mary
tracks = asyncio.run(get_all_artist_tracks(artist_id))

print("Tracks:")
# Print track data
for track in tracks:
    print(track.keys())
    pp.pp(
        {
            "name": track["name"],
            "id": track["id"],
            "preview_url": track["preview_url"],
            "duration": track["duration_ms"] / 1000,
            "type": track["type"]
        }
    )
