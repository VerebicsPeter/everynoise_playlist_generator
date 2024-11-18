import os
import yt_dlp
import subprocess


DOWNLOAD_PATH = './downloads/target.mp4'


def download_song(query: str, destination: str):
    ydl_opts = {
        'format': 'best', 'outtmpl': DOWNLOAD_PATH,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([f'ytsearch:{query}'])
    # Convert to mp3
    subprocess.run(['ffmpeg', '-i', DOWNLOAD_PATH, f"./{destination}/{query}.mp3"])
    # Remove the video file
    if os.path.exists(DOWNLOAD_PATH): os.remove(DOWNLOAD_PATH)
