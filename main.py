from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from api import playlist


app = FastAPI()

# Include resource routers
app.include_router(playlist.router, prefix="/api/playlist", tags=["Playlists"])


@app.get("/")
def index():
    return RedirectResponse(url="/api/playlist")
