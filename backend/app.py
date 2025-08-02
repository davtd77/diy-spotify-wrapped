from fastapi import FastAPI
from dotenv import load_dotenv 
import os               
from fastapi.responses import RedirectResponse
from fastapi import Request
import requests
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()  # NEW: Load variables from .env file

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecret")

# Test endpoint to verify backend is running
@app.get("/test")
async def test():
    return {"message": "Hello from the backend!"}

# Endpoint to initiate Spotify login
@app.get("/login")
def login():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
    scope = "user-top-read"

    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={client_id}"
        "&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )

    return RedirectResponse(auth_url)

# Callback endpoint to handle Spotify's response
@app.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    token_url = "https://accounts.spotify.com/api/token"
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(token_url, data=payload, headers=headers)
    token_data = response.json()

    request.session["access_token"] = token_data.get("access_token")

    return RedirectResponse("/top-tracks")

# Endpoint to get user's top tracks
@app.get("/top-tracks")
def get_top_tracks(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return {"error": "Not authenticated yet."}

    # Get range from query, default to short_term
    time_range = request.query_params.get("range", "short_term")
    if time_range not in {"short_term", "medium_term", "long_term"}:
        return {"error": "Invalid time_range. Use short_term, medium_term, or long_term."}

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(
        f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=10",
        headers=headers
    )
    data = response.json() 

    prettified = []
    for item in data.get("items", []):
        prettified.append({
            "track_name": item["name"],
            "artist": item["artists"][0]["name"],
            "album": item["album"]["name"],
            "preview_url": item["preview_url"],
            "external_url": item["external_urls"]["spotify"]
        })
    return {"top_tracks": prettified}

# Endpoint to get user's top artists
@app.get("/top-artists")
def get_top_artists(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return {"error": "Not authenticated yet."}

    # Get time range from query parameter (default to short_term)
    time_range = request.query_params.get("range", "short_term")
    if time_range not in {"short_term", "medium_term", "long_term"}:
        return {"error": "Invalid time_range. Use short_term, medium_term, or long_term."}

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Make request to Spotify API for top artists
    response = requests.get(
        f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit=10",
        headers=headers
    )
    data = response.json()

    # Clean up and simplify the response
    formatted_artists = []
    for artist in data.get("items", []):
        formatted_artists.append({
            "name": artist["name"],
            "genres": artist["genres"],
            "image": artist["images"][0]["url"] if artist["images"] else None,
            "popularity": artist["popularity"]
        })

    return {"top_artists": formatted_artists}

@app.get("/wrapped")
def get_wrapped(request: Request):
    access_token = request.session.get("access_token")
    if not access_token:
        return {"error": "Not authenticated yet."}

    # Get time_range from query (default: short_term)
    time_range = request.query_params.get("range", "short_term")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Get top tracks
    tracks_response = requests.get(
        f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit=10",
        headers=headers
    )
    top_tracks = tracks_response.json()

    # Get top artists
    artists_response = requests.get(
        f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit=10",
        headers=headers
    )
    top_artists = artists_response.json()
    
        # Prettify top tracks
    pretty_tracks = [
        {
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "album": track["album"]["name"],
            "image": track["album"]["images"][0]["url"],
            "popularity": track["popularity"]
        }
        for track in top_tracks.get("items", [])
    ]

    # Prettify top artists
    pretty_artists = [
        {
            "name": artist["name"],
            "genres": artist["genres"],
            "image": artist["images"][0]["url"],
            "popularity": artist["popularity"]
        }
        for artist in top_artists.get("items", [])
    ]

    return {
        "time_range": time_range,
        "top_tracks": pretty_tracks,
        "top_artists": pretty_artists
    }

