import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import warnings
import google.generativeai as genai
from apikey import spotify_api_key, google_gemini_api_key, openai_api_key
from streamlit_option_menu import option_menu

# Ignore warnings
warnings.filterwarnings("ignore")

# Streamlit page configuration
st.set_page_config(page_title="Spotify Recommender: Discover Your Next Favorite Song!", page_icon="🎵", layout="wide")

# Set up initial session states
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_session' not in st.session_state:
    st.session_state.chat_session = None

# Configure the Google Gemini API
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
        ["Home", "Song Recommendations", "Top Charts", "Chatbot Assistant"],
        icons=['house', 'music-note', 'chart-bar', 'chat-dots'],
        menu_icon="music",
        default_index=0,
        styles={
            "icon": {"color": "#f0a500", "font-size": "20px"},
            "nav-link": {"font-size": "17px", "text-align": "left", "margin": "5px", "--hover-color": "#262730"},
            "nav-link-selected": {"background-color": "#262730"}
        }
    )

# Home Section
if options == "Home":
    st.title("Moodify: Tune into Your Emotions with Spotify 🎶😊")
    st.write("## Welcome to Moodify!")
    st.write("Explore music that matches your emotions and discover new tracks based on sentiment. Moodify lets you analyze your Spotify playlists, categorize tracks by mood, and create custom playlists to match your current vibe.")
    st.write( "Whether you’re looking to lift your spirits, focus, or relax, Moodify helps you find the perfect music for every mood.")
    st.write("### 1. Connect with Spotify")
    st.write("- Link your Spotify account to Moodify to analyze your playlists and track data.")
    st.write("- Get insights on the sentiment of each song in your playlists, including moods like:")
    st.write("  - **Happy**")
    st.write("  - **Calm**")
    st.write("  - **Energetic**")
    st.write("  - **Melancholic**")
    st.write("### 2. Discover Mood-Based Playlists")
    st.write("- Generate custom playlists based on your current mood or explore music that complements specific emotions.")
    st.write("- Find new tracks similar to your favorites, curated by sentiment analysis.")
    st.write("### 3. Analyze Your Music Taste")
    st.write("- Learn more about the emotional themes in your favorite songs.")
    st.write("- See breakdowns by genre, tempo, and energy levels, and discover how your music matches your mood.")
    st.write("### 4. Enjoy a Personalized Experience")
    st.write("With Moodify, music becomes more than just sound. It’s an emotional journey tailored to how you feel.")
    st.write("Simply click on “Connect Spotify” to start exploring a new way to engage with your playlists.")

# Song Recommendations Section
elif options == "Song Recommendations":
    st.title("Song Recommendations")
    # Add functionality for recommending songs based on Spotify API
    # e.g., based on top artists, genres, or user input

# Top Charts Section
elif options == "Top Charts":
    st.title("Top Charts")
    # Add visualization for top charts from Spotify

# Chatbot Assistant Section
elif options == "Chatbot Assistant":
    st.title("Chatbot Assistant")
    st.write("Ask our chatbot for music suggestions, artist info, or music trivia!")

    # Example system prompt configuration for the chatbot
    system_prompt = """
    You are Melody, a music-loving AI assistant. Help users with music recommendations, song insights, and fun music trivia.
    """


    def initialize_conversation(prompt):
        if not st.session_state.get("chat_initialized", False):
            if not st.session_state.get("chat_session"):
                st.session_state.chat_session = model.start_chat(history=st.session_state.messages)

            st.session_state.messages.append({"role": "system", "content": prompt})
            response = st.session_state.chat_session.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.session_state.chat_initialized = True


    initialize_conversation("Hi. I'll explain how you should behave: " + system_prompt)

    # Display chat history
    for message in st.session_state.messages[1:]:
        if message['role'] == 'system':
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if user_message := st.chat_input("Type your question here..."):
        with st.chat_message("user"):
            st.markdown(user_message)
        st.session_state.messages.append({"role": "user", "content": user_message})

        # Send user message to the model and get response
        response = st.session_state.chat_session.send_message(user_message)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
