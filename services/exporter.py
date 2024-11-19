import os
import subprocess

import services.downloader as downloader
from data.schemas import PlaylistSchema
from typing import Protocol


class PlaylistExporter(Protocol):
    def export(self, playlist: PlaylistSchema): ...


class YouTubeExporter(PlaylistExporter):
    def __init__(self):
        # Create the downloads directory if it's not present
        if not os.path.isdir("./downloads/mp3"): os.mkdir("./downloads/mp3")
    
    def export(self, playlist: PlaylistSchema) -> str:
        file_paths: list[str] = []
        
        for track in playlist.tracks:
            query = f"{track.artist.name} - {track.name}"
            path = downloader.download_audio(query, "./downloads/mp3")
            # add the file path to the list of paths
            file_paths.append(path)
        
        playlist_file = f'./downloads/{playlist.uuid}.zip'
        subprocess.run(['zip', '-j', playlist_file, *file_paths])
        return playlist_file
