# TODO: request schemas

import os
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.responses import StreamingResponse

from services import playlist_generator, playlist_exporter


router = APIRouter()


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
    num_art: int = 5,
    num_tpa: int = 3,
) -> dict:
    playlist = await playlist_generator.get_playlist(
        name=name,
        genre_name=genre_name,
        num_artists=num_art,
        num_t_per_a=num_tpa,
    )
    return {"playlist": playlist}

# FIXME: memory leak?
@router.get("/download/{uuid}")
async def download_playlist(uuid: UUID, background_tasks: BackgroundTasks):
    BUFFERIZE = 1024 * 1024  # Reading in 1 MB chunks

    playlist = playlist_generator.playlists.get(uuid, None)

    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found.")

    export_file = await playlist_exporter.YouTubeExporter().export(playlist)

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
