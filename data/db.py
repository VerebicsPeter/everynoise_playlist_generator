from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from data.base import Base
from data.paths import DATABASE_PATH

# These need to be imported for table creation to work
from data.models import Artist, Genre, artist_genre_table

# Make linter happy
_ = [Base, Artist, Genre, artist_genre_table]

engine = create_engine(DATABASE_PATH, echo=True)

async_engine = create_async_engine(DATABASE_PATH, echo=True)
