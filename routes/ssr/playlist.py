from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data.db import async_engine, Genre
from data.schemas import PlaylistSchema
from services import playlist_generator

AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@router.get("/search-genre", response_class=HTMLResponse)
async def search_genre(request: Request):
    genre_name = request.query_params.get("genre_name", "")
    if genre_name:
        async with AsyncSessionLocal() as session:
            query = select(Genre.name).where(Genre.name.ilike(f"%{genre_name.lower()}%")).limit(5)
            result = await session.execute(query)
            genres = [row[0] for row in result.fetchall()]
        context = {"request": request, "genres": genres }
    else:
        context = {"request": request, "genres": [] }
    return templates.TemplateResponse("genre_list.html", context)


@router.get("/generate", response_class=HTMLResponse)
async def generate_playlist(request: Request):
    name = request.query_params.get("name", "my playlist")
    genre_name = request.query_params.get("genre_name", "pop")
    # Limit both values to 10 for reducing playlist size
    num_artists = min(int(request.query_params.get("num_artists", 5)), 10)
    num_t_per_a = min(int(request.query_params.get("num_t_per_a", 1)), 10)

    result = await playlist_generator.get_playlist(
        name.strip(),
        genre_name.strip(),
        num_artists,
        num_t_per_a,
    )
    
    if not isinstance(result, PlaylistSchema):
        error = "Playlist could not be generated."
        message = result.get("message", "Something went wrong.")
        context = {"error": error, "message": message}
        return templates.TemplateResponse(request, "error_message.html", context)
    
    if not result.tracks:
        error = "Playlist could not be generated."
        context = {"error": error, "message": "No tracks found."}
        return templates.TemplateResponse(request, "error_message.html", context)
    
    context = {"uuid": result.uuid, "tracks": result.tracks, "name": result.name}
    return templates.TemplateResponse(request, "playlist_tracks.html", context)


@router.get("/convert/{uuid}", response_class=HTMLResponse)
async def convert_playlist(request: Request, uuid: UUID):
    result = await playlist_generator.export_playlist(uuid)
    context = {"uuid": uuid, "result": result}
    return templates.TemplateResponse(request, "playlist_result.html", context)
