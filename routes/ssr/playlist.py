# TODO: maybe use a templating engine

from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from data.schemas import PlaylistSchema
from services import playlist_generator

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index():
    html_content = \
    """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Every Noise at Once Playlist Generator</title>
        <!-- Tailwind CSS CDN -->
        <script src="https://cdn.tailwindcss.com"></script>
        <!-- Include HTMX CDN -->
        <script src="https://unpkg.com/htmx.org@1.8.4"></script>
    </head>
    <body class="bg-gray-100 text-gray-800 font-sans">

        <!-- Main container -->
        <div class="max-w-4xl mx-auto p-6">
            <!-- Header -->
            <h1 class="text-3xl font-bold text-center text-blue-600 mb-8">Every Noise at Once Playlist Generator</h1>

            <!-- Input form -->
            <form 
                hx-get="/playlist/generate" 
                hx-target="#playlist_data"
                hx-swap="innerHTML"
                hx-indicator="#spinner"
                class="bg-white shadow-md rounded-lg p-6 space-y-4"
            >
                <!-- Playlist Name -->
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-700">Playlist Name:</label>
                    <input 
                        type="text" 
                        id="name" 
                        name="name" 
                        required 
                        class="mt-1 p-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                </div>

                <!-- Genre -->
                <div>
                    <label for="genre_name" class="block text-sm font-medium text-gray-700">Genre:</label>
                    <input 
                        type="text" 
                        id="genre_name" 
                        name="genre_name" 
                        required 
                        class="mt-1 p-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                </div>

                <!-- Number of Artists -->
                <div>
                    <label for="num_art" class="block text-sm font-medium text-gray-700">Number of Artists:</label>
                    <input 
                        type="number" 
                        id="num_art" 
                        name="num_artists" 
                        value="5" 
                        min="1" 
                        max="10" 
                        required 
                        class="mt-1 p-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                </div>

                <!-- Tracks per Artist -->
                <div>
                    <label for="num_tpa" class="block text-sm font-medium text-gray-700">Tracks per Artist:</label>
                    <input 
                        type="number" 
                        id="num_tpa" 
                        name="num_t_per_a" 
                        value="1" 
                        min="1" 
                        max="10" 
                        required 
                        class="mt-1 p-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                </div>
                <hr>
                <!-- Submit Button -->
                <div class="text-center">
                    <button 
                        type="submit" 
                        class="bg-blue-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                    >
                        Create Playlist
                    </button>
                </div>
            </form>

            <!-- Divider -->
            <hr class="border-t-2 border-gray-300 my-3">

            <!-- Playlist Data -->
            <div id="playlist" class="bg-white shadow-md rounded-lg p-6 text-center">
                <p id="playlist_data" class="text-gray-600 mb-2">Playlist will appear here.</p>
                <div id="spinner" class="htmx-indicator mx-auto w-8 h-8 border-4 border-t-transparent border-blue-500 rounded-full animate-spin"></div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/generate", response_class=HTMLResponse)
async def generate_playlist(request: Request):
    name = request.query_params.get('name', 'my playlist')
    genre_name = request.query_params.get('genre_name', 'pop punk')
    # Limit both values to 10
    num_artists = min(int(request.query_params.get('num_artists', 5)), 10)
    num_t_per_a = min(int(request.query_params.get('num_t_per_a', 1)), 10)
    
    response = await playlist_generator.get_playlist(name, genre_name, num_artists, num_t_per_a)
    
    if not isinstance(response, PlaylistSchema):
        html_content = f'<p class="text-lg font-semibold text-red-600">Playlist could not be generated!</p>'
        html_content += f"<p>{response.get('message', 'Something went wrong.')}</p>"
        return HTMLResponse(content=html_content)
    
    playlist = response
    
    tracks = playlist.tracks
    
    html_content = """
    <div class="bg-white">
        <p class="text-lg font-semibold text-green-600">Playlist generated!</p>
        <ul class="list-none list-inside text-gray-800 mt-2">
    """
    for track in tracks: html_content += f"<li class='py-1'>{track.artist.name} - {track.name}</li>"
    html_content += f"""
        </ul>
        <div class="mt-4">
            <button id="convert-button"
            hx-target="#convert-button"
            hx-get="/playlist/convert/{playlist.uuid}"
            hx-swap="outerHTML"
            hx-indicator="#spinner"
            class="bg-blue-600 text-white font-medium py-2 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
                Convert Playlist
            </button>
        </div>
    </div>
    """
    return HTMLResponse(content=html_content)


@router.get("/convert/{uuid}", response_class=HTMLResponse)
async def convert_playlist(uuid: UUID):
    result = await playlist_generator.export_playlist(uuid)
    
    if result.get("status", "") == "Success":
        html_content = f"""Converted playlist. <br> <a href="/api/playlist/download/{uuid}">Download Playlist</a>"""
    else:
        html_content = f"Conversion failed."
    
    return HTMLResponse(content=html_content)
