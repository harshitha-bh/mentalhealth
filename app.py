import streamlit as st
import openai
import time
import pyttsx3
import speech_recognition as sr
import os

# === Page Settings ===
st.set_page_config(page_title="Solace AI", layout="centered")

# === Session State Setup ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Load API Key from Secrets ===
openai.api_key = st.secrets["OPENAI_API_KEY"]

# === Custom Login System ===
def login():
    st.markdown("## 🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "harshitha" and password == "test1234":
                st.session_state["logged_in"] = True
            else:
                st.error("❌ Invalid credentials.")
login()
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.stop()

# === Welcome UI ===
st.markdown("<h1 style='color:#4CAF50;'>🌿 Welcome to Solace AI</h1>", unsafe_allow_html=True)
st.markdown("Your personal mental health support companion.")

# ✅ FIXED: Show image if it exists
if os.path.exists("assets/therapy.png"):
    st.image("assets/therapy.png", use_container_width=True)
else:
    st.info("💡 Add a calming image in `assets/therapy.png` for better visuals.")

# === Voice Input ===
def voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Listening... Please speak clearly.")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        return "Sorry, I couldn't hear you properly."

# === Text-to-Speech ===
def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 170)
    engine.say(text)
    engine.runAndWait()

# === Get GPT Response ===
def get_reply(user_input):
    st.session_state.chat_history.append(("You", user_input))
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a kind and supportive mental health companion. "
                    "Talk like a best friend using warm, friendly tone. "
                    "Include a motivational quote, calming suggestion, and reminder for self-care."
                ),
            },
            {"role": "user", "content": user_input}
        ],
        temperature=0.7,
        max_tokens=500
    )
    reply = response.choices[0].message.content.strip()
    st.session_state.chat_history.append(("Solace AI", reply))
    return reply

# === Typing Effect ===
def render_typing(reply):
    with st.empty():
        typed = ""
        for char in reply:
            typed += char
            time.sleep(0.015)
            st.markdown(typed + "▌")
        st.markdown(typed)

# === Input UI ===
st.markdown("### 💬 How are you feeling today?")
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_area("Type your feelings here...", key="input", height=150)
with col2:
    if st.button("🎙️"):
        user_input = voice_input()
        st.session_state.input = user_input
        st.experimental_rerun()

if st.button("🧠 Get Support"):
    if not user_input.strip():
        st.warning("Please type or speak how you’re feeling.")
    else:
        reply = get_reply(user_input)
        st.success("Here's something for you:")
        render_typing(reply)
        st.button("🔈 Read Out Loud", on_click=lambda: speak(reply))

# Optional: Show chat history
with st.expander("🗒️ Chat History"):
    for role, msg in st.session_state.chat_history:
        st.markdown(f"**{role}**: {msg}")
