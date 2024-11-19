import os
import yt_dlp
import subprocess

# TODO/FIXME: this won't work if it's async, USE A TEMP FILE
DOWNLOAD_PATH = './downloads/target.mp4'


def download_audio(query: str, destination: str) -> str:
    file_path = f"{destination}/{query}.mp3"
    
    # Return the path if it is already downloaded
    if os.path.isfile(file_path): return file_path
    
    ydl_opts = {
        'format': 'best', 'outtmpl': DOWNLOAD_PATH,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([f'ytsearch:{query}'])

    # Convert to mp3
    subprocess.run(['ffmpeg', '-i' , DOWNLOAD_PATH, file_path])
    # Remove the video file
    if os.path.isfile(DOWNLOAD_PATH): os.remove(DOWNLOAD_PATH)
    
    return file_path
