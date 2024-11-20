import os
import asyncio
import yt_dlp


def run_yt_dlp(ydl_opts, query):
    """Wrapper function to run yt_dlp synchronously within an executor"""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'ytsearch:{query}'])


async def download_audio(query: str, destination: str) -> str:
    DOWNLOAD_PATH = f'./downloads/{query}'
    file_path = f"{destination}/{query}.mp3"
    
    # Return the path if it is already downloaded
    if os.path.isfile(file_path):
        return file_path
    
    # Download using yt_dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': DOWNLOAD_PATH,
    }

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, run_yt_dlp, ydl_opts, query)

    # Convert to mp3 using ffmpeg
    ffmpeg_process = await asyncio.create_subprocess_exec(
        'ffmpeg', '-i', DOWNLOAD_PATH, file_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await ffmpeg_process.communicate()

    # Remove the video file
    if os.path.isfile(DOWNLOAD_PATH):
        os.remove(DOWNLOAD_PATH)
    
    return file_path
