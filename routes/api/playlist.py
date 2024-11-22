# TODO: request schemas

import os
from uuid import UUID

from fastapi import APIRouter, HTTPException
from fastapi.background import BackgroundTasks
from fastapi.responses import StreamingResponse

from services import playlist_generator

router = APIRouter()


@router.get("/download/{uuid}")
async def download_playlist(uuid: UUID, background_tasks: BackgroundTasks):
    BUFFERIZE = 1024 * 1024  # Reading in 1 MB chunks

    if not (playlist := playlist_generator.playlists.get(uuid, None)):
        raise HTTPException(status_code=404, detail="Playlist not found.")
    
    if not (filepath := playlist_generator.filepaths.get(uuid, None)):
        raise HTTPException(status_code=404, detail="Playlist file not found.")

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Playlist file not found.")
    
    # Create a generator to stream the zip file
    async def iterfile():
        with open(filepath, "rb") as file:
            while chunk := file.read(BUFFERIZE): yield chunk

    headers = {"Content-Disposition": f'attachment; filename="{playlist.name}"'}
    
    # Add a cleanup task for removing the zip file
    def cleanup():
        try:  # Remove the zip file
            if os.path.isfile(filepath): os.remove(filepath)
            del playlist_generator.filepaths[filepath]
        except Exception as error:
            # Log the error if cleanup fails
            print(f"Cleanup failed: {error}")
        # TODO: investigate, this seems to fail even if the zip file is cleaned up

    background_tasks.add_task(cleanup)

    # Return the zip file as a streaming response
    return StreamingResponse(iterfile(), headers=headers, media_type="application/zip")
