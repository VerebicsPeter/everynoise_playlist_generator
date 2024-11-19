import pprint as pp

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from data.db import engine, Artist, Genre

Session = sessionmaker(bind=engine)
session = Session()

# Examples for a simple queries

print('number of artists:', session.query(Artist).count())

pp.pp([
    artist.name + f"{[genre.name for genre in artist.genres]}"
    for artist in session.query(Artist).limit(10).all()
])

artists = session.query(Artist).filter(Artist.genres.any(Genre.name == "magyar mulatos"))

pp.pp([ artist.name for artist in artists ])

# Example for a more complex query

artist_count = (
    session
        .query(Genre.name, func.count(Artist.id))
        .join(Artist.genres)
        .filter(Genre.name.like('%metal%'))
        .group_by(Genre.name)
        .all()
)

for genre, count in artist_count:
    print(f"Genre: {genre}, artist count: {count}")

