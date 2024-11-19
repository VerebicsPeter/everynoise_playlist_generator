from data.db import engine, Base
from data.models import Artist, Genre, artist_genre_table

# Make linter happy
_ = [Artist, Genre, artist_genre_table]

# Create tables if this is ran as a script
Base.metadata.create_all(engine)
