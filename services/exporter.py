import os

import services.downloader as downloader
from data.models import Playlist
from typing import Protocol


class PlaylistExporter(Protocol):
    def export(self, playlist: Playlist): ...


class YouTubeExporter(PlaylistExporter):
    def __init__(self):
        # Create the downloads directory if it's not present
        if not os.path.isdir("./downloads"): os.mkdir("./downloads")
    
    def export(self, playlist: Playlist):
        playlist_path = f'./downloads/{playlist.name}'
        if not os.path.isdir(playlist_path): os.mkdir(playlist_path)
        for track in playlist.tracks:
            query = f"{track.artist.name} - {track.title}"
            downloader.download_audio(query, playlist_path)
