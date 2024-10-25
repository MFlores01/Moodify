spotify_api_key = "<Your_Spotify_API_Key>"
openai_api_key = "<Your_OpenAI_API_Key>"
google_gemini_api_key = "AIzaSyB7-6Ust2YttExAT0Zw63P1Xf2z0Z8v6yk"

import requests
from apikey import spotify_api_key

# Endpoint to get the user's top tracks
def get_spotify_top_tracks():
    headers = {"Authorization": f"Bearer {spotify_api_key}"}
    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)
    return response.json() if response.status_code == 200 else None
