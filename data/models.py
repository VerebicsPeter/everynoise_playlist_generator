from pydantic import BaseModel
from uuid import UUID


class Artist(BaseModel):
    name: str
    link: str  # EveryNoise link


class Track(BaseModel):
    artist: Artist
    title: str
    link: str  # Spotify link


class Playlist(BaseModel):
    uuid: UUID
    tracks: list[Track]
    name: str
