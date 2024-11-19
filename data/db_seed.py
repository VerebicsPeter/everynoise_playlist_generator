# Populates the database with data scraped from everynoise

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from tqdm import tqdm

from data.db import engine
from data.models import Artist, Genre

from scrapers import everynoise


Session = sessionmaker(bind=engine)
session = Session()


if __name__ == "__main__":
    print("Scraping genres names ...")
    
    genre_names = everynoise.scrape_genre_names()
    
    for genre_name in tqdm(genre_names, desc="Processing genres"):
        
        genre = session.query(Genre).filter_by(name=genre_name).first()

        if not genre:
            genre = Genre(name=genre_name)
            session.add(genre)
            # Commit here to ensure that the genre is added
            session.commit()
        
        artists = everynoise.scrape_genre_data(
            f"https://everynoise.com/engenremap-{genre_name.replace(' ', '')}.html"
        )
        
        for artist in artists:
            name = artist["artist_name"]
            link = artist["artist_link"]
            # Check if the artist already exists
            artist = session.query(Artist).filter_by(link=link).first()
            # Create and add the new artist if needed
            if not artist:
                artist = Artist(name=name, link=link)
                session.add(artist)
            # Associate the artist with the current genre
            if genre not in artist.genres:
                artist.genres.append(genre)
        
        session.commit()
    
    print("Finished processing genres.")
    
    try:
        session.commit()
    except IntegrityError as error:
        print("Integrity error, rolling back.")
        session.rollback()
    
    session.close()
    
    print("SUCCESS.")
