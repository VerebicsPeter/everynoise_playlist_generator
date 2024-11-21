import os
import random
import base64
import json
import asyncio
import aiohttp
import requests

from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from data.db import async_engine, Genre, Artist
from data.schemas import PlaylistSchema, ArtistSchema, TrackSchema

from services import playlist_exporter

from dotenv import load_dotenv

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

load_dotenv(".env")

client_id = os.getenv("CLIENT_ID")
client_sk = os.getenv("CLIENT_SK")

# In memory storage
playlists: dict[UUID, PlaylistSchema] = {}
filepaths: dict[UUID, str] = {}


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


SPOT_API_URL = "https://api.spotify.com/v1"
TOKEN = spot_get_access_token()


async def fetch(session: aiohttp.ClientSession, url: str, params=None):
    global TOKEN
    headers = {"Authorization": f"Bearer {TOKEN}"}

    async with session.get(url, headers=headers, params=params) as response:
        # Authorized
        if response.status != 401:
            return await response.json()
        # Unauthorized, token likely expired
        TOKEN = spot_get_access_token()
        headers = {"Authorization": f"Bearer {TOKEN}"}
        # Retry the request with the new token
        async with session.get(url, headers=headers, params=params) as retry_response:
            print("Retrying with new token.")
            return await retry_response.json()


async def spot_get_artist_albums(session: aiohttp.ClientSession, artist_id: str):
    albums = []
    url = f"{SPOT_API_URL}/artists/{artist_id}/albums"
    params = {"include_groups": "album,single", "limit": 50, "offset": 0}

    while url:
        data = await fetch(session, url, params)
        albums.extend(data["items"])
        url = data.get("next")  # Next page
        params = None  # Params only needed for the first call
    return albums


async def spot_get_album_tracks(session: aiohttp.ClientSession, album_id: str):
    tracks = []
    url = f"{SPOT_API_URL}/albums/{album_id}/tracks"
    params = {"limit": 50, "offset": 0}

    while url:
        data = await fetch(session, url, params)
        tracks.extend(data["items"])
        url = data.get("next")  # Next page
        params = None  # Params only needed for the first call
    return tracks


async def spot_get_top_tracks_by_artist(artist_id: str):
    url = f"{SPOT_API_URL}/artists/{artist_id}/top-tracks?country=HU"

    async with aiohttp.ClientSession() as session:
        tracks = await fetch(session, url=url)
        return tracks["tracks"]


async def spot_get_all_tracks_by_artist(artist_id: str):
    all_tracks = []

    async with aiohttp.ClientSession() as session:
        albums = await spot_get_artist_albums(session, artist_id)
        tasks = [spot_get_album_tracks(session, album["id"]) for album in albums]
        tracks = await asyncio.gather(*tasks)

    for album_tracks in tracks:
        all_tracks.extend(album_tracks)

    unique_tracks = {track["id"]: track for track in all_tracks}
    return list(unique_tracks.values())


async def get_tracks(artist: Artist, get_all: bool = False) -> list[TrackSchema]:
    """Get tracks of an artist"""
    artist_schema = ArtistSchema(name=artist.name, spotify_id=artist.spotify_id)
    # Select the appropriate getter based on `get_all`
    getter = spot_get_all_tracks_by_artist if get_all else spot_get_top_tracks_by_artist
    tracks = await getter(artist.spotify_id)
    result = [
        TrackSchema(
            artist=artist_schema,
            name=track["name"],
            spotify_id=track["id"],
            spotify_preview_url=track["preview_url"],
        ) for track in tracks
    ]
    return result


async def get_playlist(
    name: str,
    genre_name: str,
    num_artists: int,
    num_t_per_a: int,
) -> PlaylistSchema:

    async def sample_tracks(artist: Artist):
        tracks = await get_tracks(artist, get_all=False)
        return random.sample(tracks, min(len(tracks), num_t_per_a))

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Genre).options(joinedload(Genre.artists)).filter_by(name=genre_name)
        )

        genre = result.scalars().first()
        if not genre:
            return {"message": f"No genre named: {genre_name}"}

        artists = genre.artists
        if not artists:
            return {"message": f"No artists in genre: {genre_name}"}

        sampled_tracks: list[TrackSchema] = []

        # Sample artists in genre
        artists = random.sample(artists, min(len(artists), num_artists))
        tasks = [sample_tracks(artist) for artist in artists]
        tracks = await asyncio.gather(*tasks)

        for artists_tracks in tracks:
            sampled_tracks.extend(artists_tracks)

        playlist = PlaylistSchema(uuid=uuid4(), name=name, tracks=sampled_tracks)

        # Cache the playlist
        playlists[playlist.uuid] = playlist
        return playlist


async def export_playlist(uuid: UUID):
    playlist = playlists.get(uuid, None)

    if not playlist:
        return {"message": "Playlist not found."}

    try:
        file_path = await playlist_exporter.YouTubeExporter().export(playlist)
        filepaths[uuid] = file_path
    except Exception as error:
        print(f"Something went wrong while converting playlist: {error}")
        return {"message": "Playlist conversion failed."}

    return {"status": "Success"}
