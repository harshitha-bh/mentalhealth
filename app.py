import streamlit as st
import openai
import json
import os
import time

# Load API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Constants
USER_FILE = "users.json"

# Functions to handle persistent user data
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Load users on app start
if "users" not in st.session_state:
    st.session_state.users = load_users()
if "auth" not in st.session_state:
    st.session_state.auth = False
if "mode" not in st.session_state:
    st.session_state.mode = "Login"
if "chat" not in st.session_state:
    st.session_state.chat = []

# UI Styling
st.set_page_config(page_title="Solace AI", layout="centered")
st.markdown("""
    <style>
    body { background-color: #fefefe; font-family: 'Segoe UI', sans-serif; }
    .title { color: #6a1b9a; text-align: center; font-weight: bold; font-size: 2.2em; }
    .subtitle { text-align: center; font-style: italic; color: #999; margin-bottom: 30px; }
    .message { padding: 14px 18px; border-radius: 15px; margin: 8px 0;
        max-width: 90%; font-size: 15.8px; line-height: 1.5;
        box-shadow: 1px 2px 6px rgba(0,0,0,0.06); word-wrap: break-word; }
    .user { background: #ffe0f0; text-align: right; color: #880e4f; margin-left: auto; }
    .bot { background: #e3f2fd; text-align: left; color: #0d47a1; margin-right: auto; }
    .typing { font-style: italic; color: #999; padding: 8px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# Chatbot logic
def get_smart_reply(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You are Solace AI, a warm, friendly mental health chatbot who talks like a best friend. "
                "Your replies are casual, supportive, and human-like with emojis. "
                "If the user expresses stress, sadness, or emotional overwhelm, reply with:\n"
                "- A caring, empathetic tone\n"
                "- One motivational quote\n"
                "- A calming exercise (e.g., breathing)\n"
                "- A gentle reminder to rest or eat\n"
                "Else, just reply in a casual, friendly tone like a buddy chatting on WhatsApp."
            )
        },
        {"role": "user", "content": user_input}
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.8,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# Login
def login():
    st.title("🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            users = st.session_state.users
            if username in users and users[username] == password:
                st.session_state.auth = True
                st.session_state.username = username
                st.session_state.just_logged_in = True  # New flag
            else:
                st.error("Invalid username or password. Please sign up if you're new.")

# Safe rerun after successful login
if st.session_state.get("just_logged_in", False):
    st.session_state.just_logged_in = False
    st.experimental_rerun()

# Signup
def signup():
    st.title("📝 Sign Up for Solace AI")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if not new_user or not new_pass:
                st.warning("Both fields are required.")
            elif new_user in st.session_state.users:
                st.error("Username already exists. Try a different one.")
            else:
                st.session_state.users[new_user] = new_pass
                save_users(st.session_state.users)
                st.success("Account created successfully! Please login.")
                st.session_state.mode = "Login"

# Account handling
if not st.session_state.auth:
    st.sidebar.title("🔒 Account Access")
    st.session_state.mode = st.sidebar.radio("Choose:", ["Login", "Sign Up"])
    if st.session_state.mode == "Login":
        login()
    else:
        signup()
    st.stop()

# Main Chat UI
st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your personal mental health companion 💬</p>", unsafe_allow_html=True)

# Display chat history
for role, msg in st.session_state.chat:
    css = "user" if role == "user" else "bot"
    st.markdown(f"<div class='message {css}'>{msg}</div>", unsafe_allow_html=True)

# Input form
with st.form("chat_input", clear_on_submit=True):
    user_input = st.text_area("You:", height=80)
    send = st.form_submit_button("Send")
    if send and user_input.strip():
        st.session_state.chat.append(("user", user_input))
        with st.spinner("💬 Solace is typing..."):
            reply = get_smart_reply(user_input)
            st.session_state.chat.append(("bot", reply))
        st.experimental_rerun()
