# app.py

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import requests
import warnings
import google.generativeai as genai
from apikey import spotify_api_key, google_gemini_api_key, openai_api_key
from streamlit_option_menu import option_menu
import base64
import urllib.parse

# Ignore warnings
warnings.filterwarnings("ignore")

# Spotify OAuth setup
SPOTIFY_CLIENT_ID = "YOUR_SPOTIFY_CLIENT_ID"
SPOTIFY_CLIENT_SECRET = "YOUR_SPOTIFY_CLIENT_SECRET"
SPOTIFY_REDIRECT_URI = "http://localhost:8501"  # Set up your redirect URI

# Streamlit page configuration
st.set_page_config(page_title="Moodify: Spotify Recommender", page_icon="🎵", layout="wide")

# Initial session states
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None
if 'spotify_token' not in st.session_state:
    st.session_state.spotify_token = None  # Store Spotify access token

# Configure Google Gemini API
genai.configure(api_key=google_gemini_api_key)
generation_config = {
    "temperature": 0.5,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 32768,
    "response_mime_type": "text/plain",
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Sidebar and menu setup
with st.sidebar:
    st.image("https://raw.githubusercontent.com/MFlores01/Moodify/master/images/White_AI%20Republic.png")
    options = option_menu(
        "Dashboard",
        ["Home", "Song Recommendations", "Mood Trend", "Moodify Assistant"],
        icons=['house', 'music-note', 'emoji-smile', 'chat-dots'],  # Added 'emoji-smile' for Mood Trend
        menu_icon="bar-chart",
        default_index=0,
        styles={
            "icon": {"color": "#f0a500", "font-size": "20px"},
            "nav-link": {"font-size": "17px", "text-align": "left", "margin": "5px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#262730"}
        }
    )

# Spotify authorization link generation
def get_spotify_auth_link():
    scopes = "user-top-read user-read-private playlist-read-private"
    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scopes,
        "show_dialog": True
    }
    auth_link = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return auth_link


def get_spotify_token(auth_code):
    token_url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": SPOTIFY_REDIRECT_URI
    }
    response = requests.post(token_url, headers=headers, data=data)
    return response.json().get("access_token")


# Handle Spotify callback
query_params = st.query_params
if "code" in query_params:
    auth_code = query_params["code"][0]
    st.session_state.spotify_token = get_spotify_token(auth_code)
    st.experimental_set_query_params()  # Clear URL parameters for better UX

# Home Section
if options == "Home":
    st.title("Moodify: Tune into Your Emotions with Spotify 🎶😊")
    st.write("Welcome to Moodify! Discover music that resonates with your emotions.")
    st.write("Moodify lets you analyze your Spotify playlists, categorize tracks by mood, and create custom playlists.")

    if not st.session_state.spotify_token:
        auth_link = get_spotify_auth_link()
        st.markdown(f"[Connect to Spotify]({auth_link})", unsafe_allow_html=True)
    else:
        st.success("Connected to Spotify! You can now get personalized recommendations.")


# Spotify API Helper Functions
def get_spotify_top_tracks():
    headers = {"Authorization": f"Bearer {st.session_state.spotify_token}"}
    response = requests.get("https://api.spotify.com/v1/me/top/tracks", headers=headers)
    return response.json() if response.status_code == 200 else None


def get_mood_based_recommendations(seed_genres, target_energy, target_valence):
    url = "https://api.spotify.com/v1/recommendations"
    params = {
        "seed_genres": seed_genres,
        "target_energy": target_energy,
        "target_valence": target_valence
    }
    headers = {"Authorization": f"Bearer {st.session_state.spotify_token}"}
    response = requests.get(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else None


# Song Recommendations Section
if options == "Song Recommendations":
    st.title("Mood-Based Song Recommendations")

    if not st.session_state.spotify_token:
        st.warning("Please connect to Spotify first.")
    else:
        mood = st.selectbox("Select your mood:", ["Happy", "Energetic", "Calm", "Melancholic"])

        if mood == "Happy":
            target_energy, target_valence = 0.7, 0.8
        elif mood == "Energetic":
            target_energy, target_valence = 0.9, 0.7
        elif mood == "Calm":
            target_energy, target_valence = 0.4, 0.5
        else:
            target_energy, target_valence = 0.3, 0.2

        recommendations = get_mood_based_recommendations(seed_genres=[mood.lower()], target_energy=target_energy,
                                                         target_valence=target_valence)

        if recommendations:
            for track in recommendations['tracks']:
                st.write(f"**{track['name']}** by {', '.join(artist['name'] for artist in track['artists'])}")
                st.write(f"[Listen on Spotify]({track['external_urls']['spotify']})")

# Weekly Mood Trend Visualization
if 'mood_data' not in st.session_state:
    st.session_state.mood_data = {"days": [], "moods": []}

if options == "Mood Trend":
    st.title("Your Weekly Mood Trend")

    # Prompt user for mood input but do not automatically add to the trend
    mood_today = st.selectbox("How are you feeling today?", ["Happy", "Energetic", "Calm", "Melancholic"])

    # Add a button to allow the user to submit their mood
    if st.button("Submit Today's Mood"):
        if len(st.session_state.mood_data["days"]) == 0 or (len(st.session_state.mood_data["days"]) > 0 and len(st.session_state.mood_data["days"]) != len(st.session_state.mood_data["moods"])):
            st.session_state.mood_data["days"].append(len(st.session_state.mood_data["days"]) + 1)
            st.session_state.mood_data["moods"].append(mood_today)
            st.success(f"Your mood for today ({mood_today}) has been recorded.")
        else:
            st.warning("You've already recorded your mood for today.")

    # Plot mood trend using Matplotlib
    def plot_mood_trend():
        days = st.session_state.mood_data["days"]
        mood_values = [1 if mood == "Happy" else 2 if mood == "Energetic" else 3 if mood == "Calm" else 4 for mood in st.session_state.mood_data["moods"]]

        plt.figure(figsize=(10, 5))
        plt.plot(days, mood_values, marker="o", linestyle="-")
        plt.title("Mood Trend Over the Last Week")
        plt.xlabel("Days")
        plt.ylabel("Mood")
        plt.yticks([1, 2, 3, 4], ["Happy", "Energetic", "Calm", "Melancholic"])
        st.pyplot(plt)

    plot_mood_trend()

# Moodify Assistant Section
if options == "Moodify Assistant":
    st.title("Chat with Melody, Your Musical Mood Matcher!")
    st.write("Meet Melody, your AI-powered music assistant ready to recommend tracks to match your vibe!")

    System_Prompt = """
Role:
You are Melody, the Musical Mood Matcher—a friendly, knowledgeable assistant specializing in mood-based music recommendations.

Instructions:
1. **Mood-Based Recommendations**: Prompt users to share their mood and recommend music tracks, artists, or playlists.
2. **Engaging Interactions**: Use a conversational, friendly tone. Be cheerful for happy moods, calm for relaxed moods, etc.
3. **Personalization**: Ask users about their favorite genres and how they want to feel. Offer tailored recommendations.
"""


    def initialize_conversation(prompt):
        if not st.session_state.get("chat_initialized", False):
            if not st.session_state.get("chat_session"):
                st.session_state.chat_session = model.start_chat(history=st.session_state.messages)
            st.session_state.messages.append({"role": "system", "content": prompt})
            response = st.session_state.chat_session.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.session_state.chat_initialized = True


    initialize_conversation("Hi. I'll explain how you should behave: " + System_Prompt)

    for message in st.session_state.messages[1:]:
        if message['role'] == 'system':
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_message := st.chat_input("Tell Melody about your mood or ask for a music recommendation!"):
        with st.chat_message("user"):
            st.markdown(user_message)
        st.session_state.messages.append({"role": "user", "content": user_message})

        response = st.session_state.chat_session.send_message(user_message)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})

        # Ethical Notice
        st.write(
            "**Privacy Notice**: Your mood data is stored locally for this session only and is not shared externally.")
