from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from typing import List

from data.base import Base


# Association Table for the Many-to-Many Relationship
artist_genre_table = Table(
    "artist_genre",
    Base.metadata,
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


# Artist Model
class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    link = Column(String, nullable=False, unique=True)  # EveryNoise link ID

    genres: Mapped[List["Genre"]] = relationship(
        "Genre", secondary=artist_genre_table, back_populates="artists"
    )


# Genre Model
class Genre(Base):
    __tablename__ = "genres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  

    artists: Mapped[List["Artist"]] = relationship(
        "Artist", secondary=artist_genre_table, back_populates="genres"
    )
