# Pydantic schemas for validation

from pydantic import BaseModel
from uuid import UUID


class ArtistSchema(BaseModel):
    name: str
    link: str  # EveryNoise link


class TrackSchema(BaseModel):
    name: str
    link: str  # Spotify link
    artist: ArtistSchema


class PlaylistSchema(BaseModel):
    uuid: UUID
    name: str
    tracks: list[TrackSchema]
