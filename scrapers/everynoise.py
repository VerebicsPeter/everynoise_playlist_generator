from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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
