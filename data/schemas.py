# Pydantic schemas for validation

from pydantic import BaseModel, Field
from uuid import UUID

from typing import List, Optional


class ArtistSchema(BaseModel):
    name: str
    spotify_id: str


class TrackSchema(BaseModel):
    name: str
    spotify_id: str
    artists: List[ArtistSchema]
    # Optional: duration in milliseconds
    duration_ms: Optional[int] = 0
    # Optional: Spotify link to preview the track
    spotify_preview_url: Optional[str] = None


class PlaylistSchema(BaseModel):
    uuid: UUID
    name: str
    # Limit playlist size for now
    tracks: List[TrackSchema] = Field(..., max_items=100)
