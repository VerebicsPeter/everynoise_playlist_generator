from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routes.api import playlist as playlist_api
from routes.ssr import playlist as playlist_ssr


app = FastAPI()

# Include resource routers
app.include_router(playlist_ssr.router, prefix="/playlist", tags=["Playlists"])
app.include_router(playlist_api.router, prefix="/api/playlist", tags=["Playlists"])

@app.get("/")
def index():
    return RedirectResponse(url="/playlist")
