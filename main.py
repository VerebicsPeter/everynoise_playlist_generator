import os
import dataclasses
import downloader
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


@dataclasses.dataclass
class Artist:
    name: str
    link: str  # everynoise link


@dataclasses.dataclass
class Track:
    artist: Artist
    name: str
    link: str  # spotify link


def catchall(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            return []
    return wrapper


def get_html(url: str) -> str:
    with sync_playwright() as pw:
        # Launch a headless browser
        page = pw.chromium.launch(headless=True).new_page()
        # Navigate to the page
        page.goto(url)
        # Get the page content
        html = page.content()
    return html


@catchall
def scrape_genre_data(url: str) -> list[dict]:
    """Scrape data from an everynoise genre page"""
    data = []
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Scrape the page
    divs = soup.find_all("div", id=lambda x: x and x.startswith("item"))
    for div in divs:
        name = div.get_text(strip=True)[:-1]
        link = div.find("a").get("href")
        if not link:
            continue
        data.append(
            {
                "artist_name": name,
                "artist_link": link,
            }
        )
    # Return the scraped data
    return data


@catchall
def scrape_artist_data(url: str) -> list[dict]:
    """Scrape data from an everynoise artist page"""
    data = []
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Scrape the page
    rows = soup.find_all("tr", class_=["alltrackrow", "trackrow"])
    for row in rows:
        col = row.find_all("td")[2]
        if not (link := col.find("a")):
            continue
        track_name = link.get_text(strip=True)
        track_link = link.get("href")
        data.append(
            {
                "track_name": track_name,
                "track_link": track_link,
            }
        )
    # Return the scraped data
    return data


def get_artists(genre: str) -> list[Artist]:
    """Get artists of a genre"""
    genre = genre.replace(" ", "")
    data = scrape_genre_data(f"https://everynoise.com/engenremap-{genre}.html")
    artists = [
        Artist(
            name=row["artist_name"],
            link=row["artist_link"],
        )
        for row in data
    ]
    return artists


def get_tracks(artist: Artist) -> list[Track]:
    """Get tracks of an artist"""
    data = scrape_artist_data(f"https://everynoise.com/{artist.link}")
    tracks = [
        Track(
            artist,
            name=row["track_name"],
            link=row["track_link"],
        )
        for row in data
    ]
    return tracks


def generate_playlist(genre: str,
    max_artists_per_genre=5,
    max_tracks_per_artist=5,
):
    # Create the downloads directory if it does not exist
    if not os.path.isdir("./downloads"): os.mkdir("./downloads")
    # Get the artists
    artists = get_artists(genre)
    # Sample artists
    for artist in random.sample(artists, min(len(artists), max_artists_per_genre)):
        tracks = get_tracks(artist)
        # Sample tracks and dowload them
        for track in random.sample(tracks, min(len(tracks), max_tracks_per_artist)):
            query = f"{artist.name} - {track.name}"
            downloader.download_song(query, "downloads")


if __name__ == "__main__":
    genre = "gypsy fusion"
    generate_playlist(
        genre=genre,
        max_artists_per_genre=5,
        max_tracks_per_artist=1,
    )
