# Solace AI - Mental Health Chatbot (Full Combined Version)

import streamlit as st
import openai
import pyttsx3
import speech_recognition as sr
import streamlit_authenticator as stauth
import datetime
from io import BytesIO

# -------------- CONFIG SECTION ----------------
st.set_page_config(page_title="Solace AI - Mental Health Chatbot", page_icon="🧠", layout="centered")

# OpenAI Key
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "your-api-key-here"

# Authenticator Setup
hashed_passwords = stauth.Hasher(["password123"]).generate()
credentials = {
    'usernames': {
        'user1': {
            'name': 'User_One',
            'password': hashed_passwords[0]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    'solace_cookie',
    'random_key',
    1
)

name, auth_status, username = authenticator.login('Login', 'main')

if not auth_status:
    if auth_status is False:
        st.error("Incorrect username or password")
    elif auth_status is None:
        st.warning("Please enter your username and password")
    st.stop()

# -------------- FUNCTIONS ----------------
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "☀️ Good Morning!"
    elif 12 <= hour < 18:
        return "🌤️ Good Afternoon!"
    else:
        return "🌙 Good Evening!"

def get_mental_health_reply(user_input):
    messages = [
        {"role": "system", "content": "You are a kind and supportive mental health assistant."},
        {"role": "user", "content": f"""
A user said: \"{user_input}\"

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

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# -------------- MAIN UI ----------------

st.title("🧘‍♀️ Solace AI - Mental Health Chatbot")
st.markdown(f"**{greet_user()}** Welcome, {name}! I'm here for you. Share how you're feeling 💙")

# Voice Input
st.markdown("### 🎙️ Speak Your Feelings (Optional)")
audio_data = st.file_uploader("Upload a WAV audio note", type=["wav"])
user_input = ""

if audio_data is not None:
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_data)
    with audio_file as source:
        audio = recognizer.record(source)
    try:
        user_input = recognizer.recognize_google(audio)
        st.success(f"You said: {user_input}")
    except sr.UnknownValueError:
        st.error("Sorry, could not understand the audio.")

# Mood Input
st.markdown("**Or type your current feeling below:**")
mood = st.selectbox("Mood", ["😐 Neutral", "😞 Sad", "😡 Angry", "😰 Anxious", "😊 Happy", "😔 Lonely", "😭 Overwhelmed"], index=0)
text_input = st.text_area("💬 Tell me what's on your mind", height=150)

if text_input:
    user_input = f"{mood} - {text_input}" if mood != "😐 Neutral" else text_input

# Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Get Support Button
if st.button("💡 Get Support"):
    if user_input.strip():
        with st.spinner("Thinking warm thoughts..."):
            reply = get_mental_health_reply(user_input)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({"user": user_input, "bot": reply, "time": timestamp})
            st.success("Here's something that may help:")
            st.markdown(reply)
    else:
        st.warning("Please enter your feelings first.")

# Hear Response
if st.button("🔊 Hear the response"):
    if st.session_state.chat_history:
        speak_text(st.session_state.chat_history[-1]['bot'])

# Chat History Display
if st.session_state.chat_history:
    st.markdown("### 📝 Conversation History")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"**🧍‍♀️ You [{chat['time']}]:** {chat['user']}")
        st.markdown(f"**🤖 Solace AI:** {chat['bot']}")

# Download Report
if st.button("📄 Download My Session Report"):
    if st.session_state.chat_history:
        output_text = "🧘‍♀️ Solace AI - Session Report\n"
        output_text += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for chat in st.session_state.chat_history:
            output_text += f"🧍‍♀️ You ({chat['time']}): {chat['user']}\n🤖 Solace AI: {chat['bot']}\n\n"
        st.download_button("⬇️ Click to download", data=output_text, file_name="solace_session.txt")
    else:
        st.warning("No conversation yet to download.")
