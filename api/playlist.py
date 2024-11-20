import os
import random
import uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import sessionmaker

from data.db import engine, Genre
from data.schemas import ArtistSchema, TrackSchema, PlaylistSchema
from scrapers import everynoise
from services import exporter

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

# Async session setup
ASYNC_ENGINE = create_async_engine(str(engine.url), echo=True)
AsyncSessionLocal = sessionmaker(
    ASYNC_ENGINE, class_=AsyncSession, expire_on_commit=False
)

# Global state for now
playlists: dict[UUID, PlaylistSchema] = {}

router = APIRouter()


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


@router.get("/")
async def index() -> dict:
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
async def generate_playlist(
    name: str = "new playlist",
    genre_name: str = "pop",
    num_artists: int = 5,
    tracks_per_artist: int = 3,
) -> dict:
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
            tracks = random.sample(tracks, min(len(tracks), tracks_per_artist))
            selected_tracks.extend(tracks)

        playlist = PlaylistSchema(uuid=uuid.uuid4(), name=name, tracks=selected_tracks)

        # Cache the playlist
        playlists[playlist.uuid] = playlist
        return {"playlist": playlist}


@router.get("/download/{uuid}")
async def download_playlist(uuid: UUID, background_tasks: BackgroundTasks):
    BUFFERIZE = 1024 * 1024  # Reading in 1 MB chunks

    playlist = playlists.get(uuid, None)

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found.")

    export_file = await exporter.YouTubeExporter().export(playlist)

    # Add a cleanup task for removing the zip file
    def cleanup():
        try:  # Remove the zip file
            if os.path.isfile(export_file):
                os.remove(export_file)
        except Exception as error:
            # Log the error if cleanup fails
            print(f"Cleanup failed: {error}")

    background_tasks.add_task(cleanup)

    # Create a generator to stream the zip file
    async def iterfile():
        with open(export_file, "rb") as file:
            while chunk := file.read(BUFFERIZE):
                yield chunk

    headers = {"Content-Disposition": f'attachment; filename="{playlist.name}"'}

    # Return the zip file as a streaming response
    return StreamingResponse(iterfile(), headers=headers, media_type="application/zip")
