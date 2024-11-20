# Pydantic schemas for validation

from pydantic import BaseModel, Field
from uuid import UUID

from typing import List


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
    tracks: List[TrackSchema] = Field(..., max_items=50)
