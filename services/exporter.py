import os

import asyncio

from typing import Protocol

from data.schemas import PlaylistSchema
from services.downloader import download_audio


class PlaylistExporter(Protocol):
    async def export(self, playlist: PlaylistSchema) -> str: ...


class YouTubeExporter(PlaylistExporter):
    def __init__(self):
        # Create the downloads directory if it's not present
        os.makedirs("./downloads/mp3", exist_ok=True)

    async def export(self, playlist: PlaylistSchema) -> str:
        # Limit to 4 concurrent tasks to avoid resource exhaustion
        semaphore = asyncio.Semaphore(4)

        async def limited_download(query: str, path: str):
            async with semaphore:
                return await download_audio(query, path)

        tasks = [
            limited_download(f"{track.artist.name} - {track.name}", "./downloads/mp3")
            for track in playlist.tracks
        ]

        paths = await asyncio.gather(*tasks)

        playlist_file = f"./downloads/{playlist.uuid}.zip"
        # Use async subprocess to zip files
        zip_process = await asyncio.create_subprocess_exec(
            "zip",
            "-j",
            playlist_file,
            *paths,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await zip_process.communicate()
        return playlist_file
