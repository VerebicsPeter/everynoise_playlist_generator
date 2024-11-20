# Playlist Generator Service

import os
import asyncio

import yt_dlp

from typing import Protocol
from data.schemas import PlaylistSchema


def run_yt_dlp(yt_dlp_opts, query):
    """Wrapper function to run yt_dlp within an executor to avoiding blocking IO"""
    with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl: ydl.download([f"ytsearch:{query}"])


class PlaylistExporter(Protocol):
    async def export(self, playlist: PlaylistSchema) -> str: ...


class YouTubeExporter(PlaylistExporter):
    def __init__(self, download_dir: str = "./downloads"):
        self.download_dir = download_dir
        # Create the downloads directory and subdirectory if needed
        os.makedirs(f"{self.download_dir}/mp3", exist_ok=True)

    async def export(self, playlist: PlaylistSchema) -> str:
        # Limit to 4 concurrent tasks to avoid resource exhaustion
        semaphore = asyncio.Semaphore(4)

        async def limited_download(query: str):
            async with semaphore:
                return await self.download_audio(query)

        tasks = [
            limited_download(query=f"{track.artist.name} - {track.name}")
            for track in playlist.tracks
        ]

        paths = await asyncio.gather(*tasks)

        playlist_file = f"{self.download_dir}/{playlist.uuid}.zip"
        # Use async subprocess to zip files
        zip_process = await asyncio.create_subprocess_exec(
            "zip", "-j", playlist_file, *paths,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await zip_process.communicate()

        return playlist_file

    async def download_audio(self, query: str) -> str:
        DOWN_PATH = f"{self.download_dir}/{query}"
        file_path = f"{self.download_dir}/mp3/{query}.mp3"

        # Return the path if it is already downloaded
        if os.path.isfile(file_path):
            return file_path

        yt_dlp_opts = {
            "format": "bestaudio/best",
            "outtmpl": DOWN_PATH,
        }
        # Download using yt_dlp
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run_yt_dlp, yt_dlp_opts, query)

        # Convert to mp3 using ffmpeg
        ffmpeg_process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-i", DOWN_PATH, file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await ffmpeg_process.communicate()

        # Remove the video file
        if os.path.isfile(DOWN_PATH):
            os.remove(DOWN_PATH)

        return file_path
