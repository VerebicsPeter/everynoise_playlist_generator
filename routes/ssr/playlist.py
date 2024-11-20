# TODO: maybe use a templating engine

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from data.schemas import PlaylistSchema
from services import playlist_generator


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index():
    html_content = \
    f"""
    <html>
        <head>
            <title>Playlist Generator</title>
            <!-- Include HTMX CDN -->
            <script src="https://unpkg.com/htmx.org@1.8.4"></script>
        </head>
        <body>
            <h1>Playlist Generator</h1>
            
            <hr>
            
            <!-- Input form to enter parameters -->
            <form hx-get="/playlist/generate" hx-target="#playlist_data" hx-swap="innerHTML">
                <label for="name">Playlist Name:</label>
                <input type="text" id="name" name="name" required>
                
                <label for="genre_name">Genre:</label>
                <input type="text" id="genre_name" name="genre_name" required><br><br>
                
                <label for="num_art">Number of Artists:</label>
                <input type="number" id="num_art" name="num_artists" value="5" min="1" max="10" required><br><br>
                
                <label for="num_tpa">Tracks per Artist:</label>
                <input type="number" id="num_tpa" name="num_t_per_a" value="1" min="1" max="10" required><br><br>
                
                <button type="submit">Create Playlist</button>
            </form>
            
            <hr>
            
            <div id="playlist_data">
                <p>Playlist will appear here.</p>
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
        html_content = f"<p>Playlist could not be generated.</p>"
        html_content += f"<p>{response}</p>"
        return HTMLResponse(content=html_content)
    
    playlist = response
    html_content = f"""<p>Playlist generated successfully.</p>"""
    html_content += f"<p>Tracks:"
    html_content += f"<ul>"
    for track in playlist.tracks:
        html_content += f"<li>{track.artist.name} - {track.name}</li>"
    html_content += f"</ul>"
    html_content += f"<a href='/api/playlist/download/{playlist.uuid}'>Download</a>"
    
    return HTMLResponse(content=html_content)
