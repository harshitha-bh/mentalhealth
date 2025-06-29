import streamlit as st
import openai
import time
import os

st.set_page_config(page_title="Solace AI", layout="centered")

# Load CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Mock user database
users = {
    "harshitha": "test1234",
    "sai": "love123",
    "priya": "peace456"
}

if "auth" not in st.session_state:
    st.session_state.auth = False
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Auth system
def login():
    st.title("🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if username in users and users[username] == password:
                st.session_state.auth = True
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid username or password.")

def signup():
    st.title("📝 Sign Up for Solace AI")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        signup_btn = st.form_submit_button("Create Account")
        if signup_btn:
            if new_user in users:
                st.error("Username already exists.")
            elif not new_user or not new_pass:
                st.warning("All fields are required.")
            else:
                users[new_user] = new_pass
                st.success("Account created! Please log in.")
                st.session_state.mode = "login"

if not st.session_state.auth:
    st.sidebar.title("Account")
    st.sidebar.radio("Choose mode", ["Login", "Sign Up"], key="mode_switch")
    st.session_state.mode = st.session_state.mode_switch.lower()
    if st.session_state.mode == "login":
        login()
    else:
        signup()
    st.stop()

# API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Welcome UI
st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your supportive mental health companion.</p>", unsafe_allow_html=True)
if os.path.exists("assets/therapy.png"):
    st.image("assets/therapy.png", use_container_width=True)

# GPT reply
def get_reply(user_input):
    st.session_state.chat_history.append(("user", user_input))
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": (
                "You're a mental health companion who replies warmly like a close friend. "
                "Add kindness, one motivational quote, and one calming activity suggestion in each response."
            )},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )
    reply = response.choices[0].message.content.strip()
    st.session_state.chat_history.append(("bot", reply))
    return reply

# Typing effect
def render_typing(reply):
    with st.empty():
        typed = ""
        for char in reply:
            typed += char
            time.sleep(0.015)
            st.markdown(typed + "▌")
        st.markdown(typed)

# Input UI
st.markdown("### 💬 Share how you're feeling:")
user_input = st.text_area("Your message", height=100)

if st.button("🧠 Get Support"):
    if user_input.strip():
        reply = get_reply(user_input)
        st.success("Here's what Solace AI says:")
        render_typing(reply)
    else:
        st.warning("Please enter your feelings.")

# Chat history with avatars
st.markdown("### 🗒️ Conversation")
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='user-bubble'>🧍‍♀️ {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>🤖 {msg}</div>", unsafe_allow_html=True)
