import functools

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright


def catchall(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Await the function if async
            return await func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Return an empty list in case of error
            return []
    return wrapper


async def get_html(url: str) -> str:
    async with async_playwright() as pw:
        # Launch a headless browser asynchronously
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        # Navigate to the page asynchronously
        await page.goto(url)
        # Get the page content asynchronously
        html = await page.content()
        await browser.close()
    return html


@catchall
async def scrape_genre_names(url: str = "https://everynoise.com/") -> list[str]:
    """Scrape genre names from everynoise"""
    data = []
    html = await get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Scrape the page
    divs = soup.find_all("div", id=lambda x: x and x.startswith("item"))
    for div in divs:
        name = div.get_text(strip=True)[:-1]
        data.append(name)
    return data


@catchall
async def scrape_genre_data(url: str) -> list[dict]:
    """Scrape data from an everynoise genre page"""
    data = []
    html = await get_html(url)
    soup = BeautifulSoup(html, "html.parser")

    # Scrape the page
    divs = soup.find_all("div", id=lambda x: x and x.startswith("item"))
    for div in divs:
        artist_name = div.get_text(strip=True)[:-1]
        
        link = div.find("a").get("href")
        
        if not link or len(link.split('=')) != 2:
            continue
        
        artist_link = link.split('=')[1]
        
        data.append(
            {
                "artist_name": artist_name,
                "artist_link": artist_link,
            }
        )
    # Return the scraped data
    return data


@catchall
async def scrape_artist_data(url: str) -> list[dict]:
    """Scrape data from an everynoise artist page"""
    data = []
    html = await get_html(url)
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
