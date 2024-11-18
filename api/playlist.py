import random

import uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException
from data.models import Artist, Track, Playlist
from scrapers import everynoise
from services import exporter


# Global state for now, TODO: database and caching!!!
playlists = {}


router = APIRouter()


def get_artists(genre: str) -> list[Artist]:
    """Get artists of a genre"""
    genre = genre.replace(" ", "")
    data = everynoise.scrape_genre_data(
        f"https://everynoise.com/engenremap-{genre}.html"
    )
    artists = [
        Artist(
            name=row["artist_name"],
            link=row["artist_link"],
        )
        for row in data
    ]
    return artists


def get_tracks(artist: Artist) -> list[Track]:
    """Get tracks of an artist"""
    data = everynoise.scrape_artist_data(f"https://everynoise.com/{artist.link}")
    tracks = [
        Track(
            artist=artist,
            title=row["track_name"],
            link=row["track_link"],
        )
        for row in data
    ]
    return tracks


@router.get("/")
def index() -> dict:
    return {
        "message": " ".join(
            [
                "Welcome!",
                "This is a simple API for generating playlists",
                "based on genres listed on 'everynoise.com'.",
            ]
        )
    }


@router.get("/generate")
def generate_playlist(
    genre: str = "pop",
    max_artists: int = 5,
    tracks_per_artist: int = 3,
) -> dict:
    # Get the artists
    artists = get_artists(genre)

    if not artists:
        return {"message": f"No artists in genre: {genre}"}

    selected_tracks: list[Track] = []
    # Sample artists in genre
    for artist in random.sample(artists, min(len(artists), max_artists)):
        tracks = get_tracks(artist)
        # Sample tracks
        tracks = random.sample(tracks, min(len(tracks), tracks_per_artist))
        selected_tracks.extend(tracks)

    playlist = Playlist(uuid=uuid.uuid4(), name="new_playlist", tracks=selected_tracks)

    # Cache the playlist
    playlists[playlist.uuid] = playlist
    return {"playlist": playlist}


@router.get("/{uuid}/download")
def download_playlist(uuid: UUID):
    playlist = playlists[uuid]
    # Download using the YT converter
    exporter.YouTubeExporter().export(playlist)
    return {"message": "Downloaded playlist successfully."}
