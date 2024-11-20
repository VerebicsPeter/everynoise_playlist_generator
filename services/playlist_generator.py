import random

import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select

from data.db import async_engine, Genre
from data.schemas import ArtistSchema, TrackSchema, PlaylistSchema

from scrapers import everynoise
from services import playlist_exporter


# In memory storage
playlists: dict[UUID, PlaylistSchema] = {}
filepaths: dict[UUID, str] = {}

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_tracks(artist: ArtistSchema) -> list[TrackSchema]:
    """Get tracks of an artist"""
    data = await everynoise.scrape_artist_data(
        f"https://everynoise.com/artistprofile.cgi?id={artist.link}"
    )
    tracks = [
        TrackSchema(
            artist=artist,
            name=row["track_name"],
            link=row["track_link"],
        )
        for row in data
    ]
    return tracks


async def get_playlist(
    name: str,
    genre_name: str,
    num_artists: int,
    num_t_per_a: int,
) -> PlaylistSchema:
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

        selected_tracks: list[TrackSchema] = []
        # Sample artists in genre
        for artist in random.sample(artists, min(len(artists), num_artists)):
            tracks = await get_tracks(ArtistSchema(name=artist.name, link=artist.link))
            # Sample tracks
            tracks = random.sample(tracks, min(len(tracks), num_t_per_a))
            selected_tracks.extend(tracks)

        playlist = PlaylistSchema(uuid=uuid.uuid4(), name=name, tracks=selected_tracks)

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
