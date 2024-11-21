from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from data.schemas import PlaylistSchema
from services import playlist_generator

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)


@router.get("/generate", response_class=HTMLResponse)
async def generate_playlist(request: Request):
    name = request.query_params.get("name", "my playlist")
    genre_name = request.query_params.get("genre_name", "pop punk")
    # Limit both values to 10
    num_artists = min(int(request.query_params.get("num_artists", 5)), 10)
    num_t_per_a = min(int(request.query_params.get("num_t_per_a", 1)), 10)

    result = await playlist_generator.get_playlist(
        name, genre_name,
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
    
    context = {"uuid": result.uuid, "tracks": result.tracks}
    return templates.TemplateResponse(request, "playlist_tracks.html", context)


@router.get("/convert/{uuid}", response_class=HTMLResponse)
async def convert_playlist(request: Request, uuid: UUID):
    print(f"Received UUID: {uuid} of type {type(uuid)}")
    result = await playlist_generator.export_playlist(uuid)

    context = {"uuid": uuid, "result": result}
    return templates.TemplateResponse(request, "playlist_result.html", context)
