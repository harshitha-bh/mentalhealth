import streamlit as st
import openai
import pyttsx3
import speech_recognition as sr
import streamlit_authenticator as stauth
import datetime
from io import BytesIO

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Solace AI - Mental Health Chatbot", page_icon="🧠", layout="centered")

# Load OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ------------------ LOGIN SYSTEM ------------------

# Pre-generated hashed password for: password123
hashed_passwords = [
    "$2b$12$kK4NOalRQMbzYMNzU3r5MueB9hk4S0ey44aCUvKJd0oxog4oHOqKS"
]

credentials = {
    'usernames': {
        'user1': {
            'name': 'User One',
            'password': hashed_passwords[0]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    'solace_cookie',
    'some_random_key',
    cookie_expiry_days=1
)

name, authentication_status, username = authenticator.login("Login", "main")

if auth_status == False:
    st.error("Incorrect username or password")
    st.stop()
elif auth_status is None:
    st.warning("Please enter your username and password")
    st.stop()
else:
    st.success(f"Welcome, {name} 👋")

# ------------------ GREETING FUNCTION ------------------

def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "☀️ Good Morning!"
    elif hour < 18:
        return "🌤️ Good Afternoon!"
    else:
        return "🌙 Good Evening!"

# ------------------ OPENAI REPLY FUNCTION ------------------

def get_mental_health_reply(user_input):
    messages = [
        {"role": "system", "content": "You are a kind and supportive mental health assistant."},
        {"role": "user", "content": f"""
A user said: "{user_input}"

Please respond with:
- A supportive and empathetic message.
- A motivational quote or affirmation.
- A simple mental exercise to help them feel better.
- Remind them gently to take rest or eat if needed.
"""}
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content

# ------------------ VOICE OUTPUT ------------------

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# ------------------ MAIN UI ------------------

st.title("🧘‍♀️ Solace AI - Mental Health Chatbot")
st.markdow
