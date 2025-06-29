import streamlit as st
import openai
import json
import os

# Constants
USER_FILE = "users.json"
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load and Save user data
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Session defaults
if "users" not in st.session_state:
    st.session_state.users = load_users()
if "auth" not in st.session_state:
    st.session_state.auth = False
if "chat" not in st.session_state:
    st.session_state.chat = []
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "Login"

# UI Style
st.set_page_config(page_title="Solace AI", layout="centered")
st.markdown("""
    <style>
    body { background-color: #fefefe; font-family: 'Segoe UI', sans-serif; }
    .title { color: #6a1b9a; text-align: center; font-weight: bold; font-size: 2.2em; }
    .subtitle { text-align: center; font-style: italic; color: #999; margin-bottom: 30px; }
    .message { padding: 14px 18px; border-radius: 15px; margin: 8px 0;
        max-width: 90%; font-size: 15.8px; line-height: 1.5;
        box-shadow: 1px 2px 6px rgba(0,0,0,0.06); word-wrap: break-word; }
    .user { background: #fce4ec; text-align: right; color: #ad1457; margin-left: auto; }
    .bot { background: #e3f2fd; text-align: left; color: #0d47a1; margin-right: auto; }
    </style>
""", unsafe_allow_html=True)

# Chatbot reply
def get_chatbot_reply(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You are Solace AI, a friendly mental health companion. "
                "Respond casually and like a best friend. If the user shares emotional stress or sadness, "
                "offer an empathetic message, a motivational quote, and a calming exercise. "
                "Otherwise, just chat casually with emojis and supportive tone."
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
def login_page():
    st.title("🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            users = st.session_state.users
            if username in users and users[username] == password:
                st.session_state.auth = True
                st.session_state.username = username
                st.success(f"Welcome back, {username} 😊")
                st.session_state.page = "Chat"
            else:
                st.error("Invalid credentials. Please sign up if you're new.")

# Signup
def signup_page():
    st.title("📝 Create your Solace AI account")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        submit = st.form_submit_button("Sign Up")
        if submit:
            if not new_user or not new_pass:
                st.warning("Please fill out both fields.")
            elif new_user in st.session_state.users:
                st.error("Username already exists. Choose another.")
            else:
                st.session_state.users[new_user] = new_pass
                save_users(st.session_state.users)
                st.success("Account created! Please login.")
                st.session_state.page = "Login"

# Chat Page
def chat_page():
    st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your personal mental health buddy 💬</p>", unsafe_allow_html=True)

    for role, msg in st.session_state.chat:
        css = "user" if role == "user" else "bot"
        st.markdown(f"<div class='message {css}'>{msg}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("You:", height=80)
        submit = st.form_submit_button("Send")
        if submit and user_input.strip():
            st.session_state.chat.append(("user", user_input))
            with st.spinner("Solace is typing..."):
                reply = get_chatbot_reply(user_input)
            st.session_state.chat.append(("bot", reply))

    st.sidebar.title("👤 Account")
    st.sidebar.write(f"Logged in as: `{st.session_state.username}`")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.username = ""
        st.session_state.page = "Login"
        st.session_state.chat = []

# Page Routing
if not st.session_state.auth:
    st.sidebar.title("🔒 Account")
    st.session_state.page = st.sidebar.radio("Choose an option:", ["Login", "Sign Up"])
    if st.session_state.page == "Login":
        login_page()
    else:
        signup_page()
else:
    chat_page()
