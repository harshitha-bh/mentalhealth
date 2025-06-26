import streamlit as st
import openai
import pyttsx3
import speech_recognition as sr
import streamlit_authenticator as stauth
import datetime
from io import BytesIO

# -------------- CONFIG ----------------
st.set_page_config(page_title="Solace AI - Mental Health Chatbot", page_icon="🧠", layout="centered")

# Load API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------- AUTHENTICATION ----------------
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

if auth_status is False:
    st.error("Incorrect username or password")
    st.stop()
elif auth_status is None:
    st.warning("Please enter your username and password")
    st.stop()

# -------------- FUNCTIONS ----------------
def greet_user():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "☀️ Good Morning!"
    elif hour < 18:
        return "🌤️ Good Afternoon!"
    else:
        return "🌙 Good Evening!"

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

def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.say(text)
    engine.runAndWait()

# -------------- UI ----------------
st.title("🧘‍♀️ Solace AI - Mental Health Chatbot")
st.markdown(f"**{greet_user()}** Welcome to Solace AI. Share your feelings and let me help you feel better. 💙")

# Mood
mood = st.selectbox("Choose your current mood (optional):", ["😐 Neutral", "😞 Sad", "😡 Angry", "😰 Anxious", "😊 Happy", "😔 Lonely", "😵 Confused", "😭 Overwhelmed"], index=0)

# Voice input
st.markdown("### 🎙️ Speak your feelings (optional)")
audio_data = st.file_uploader("Upload a WAV voice note", type=["wav"])

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

# Text fallback
text_input = st.text_area("💬 Or type your thoughts here:", height=150)
if text_input.strip():
    user_input = text_input

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Support response
if st.button("💡 Get Support"):
    if user_input.strip():
        full_input = f"{mood} - {user_input}" if mood != "😐 Neutral" else user_input
        with st.spinner("Thinking warm thoughts..."):
            reply = get_mental_health_reply(full_input)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            st.session_state.chat_history.append({
                "user": user_input,
                "bot": reply,
                "time": timestamp
            })
    else:
        st.warning("Please enter or speak your feelings first.")

# Display chat history
if st.session_state.chat_history:
    st.markdown("### 📝 Conversation History")
    for chat in reversed(st.session_state.chat_history):
        st.markdown(f"""
        <div style="background-color:#e0f2f1; padding:1rem; border-radius:10px; margin:0.5rem 0;">
        <b>🧍‍♀️ You [{chat['time']}]:</b><br>{chat['user']}</div>
        <div style="background-color:#f1f8e9; padding:1rem; border-radius:10px; margin-bottom:1rem;">
        <b>🤖 Solace AI:</b><br>{chat['bot']}</div>
        """, unsafe_allow_html=True)

# Voice output
if st.button("🔊 Hear the response"):
    if st.session_state.chat_history:
        speak_text(st.session_state.chat_history[-1]["bot"])

# Download report
if st.button("📄 Download My Session Report"):
    if st.session_state.chat_history:
        output_text = "🧘‍♀️ Solace AI - Session Report\n"
        output_text += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        for chat in st.session_state.chat_history:
            output_text += f"🧍‍♀️ You ({chat['time']}): {chat['user']}\n🤖 Solace AI: {chat['bot']}\n\n"
        st.download_button("⬇️ Click to download", data=output_text, file_name="solace_session.txt")
    else:
        st.warning("No conversation yet to download.")
