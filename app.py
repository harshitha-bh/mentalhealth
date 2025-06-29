import streamlit as st
import openai
import json
import os

# Constants
USER_FILE = "users.json"
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Load/Save users
def load_users():
    return json.load(open(USER_FILE)) if os.path.exists(USER_FILE) else {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# Initialize session state
if "users" not in st.session_state:
    st.session_state.users = load_users()
if "auth" not in st.session_state:
    st.session_state.auth = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat" not in st.session_state:
    st.session_state.chat = []
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "show_chatbot" not in st.session_state:
    st.session_state.show_chatbot = False
if "user_input_buffer" not in st.session_state:
    st.session_state.user_input_buffer = ""

# UI Styling
st.set_page_config(page_title="Solace AI", layout="centered")
st.markdown("""
    <style>
    .title { color: #6a1b9a; text-align: center; font-weight: bold; font-size: 2.2em; }
    .subtitle { text-align: center; font-style: italic; color: #666; margin-bottom: 20px; }
    .message {
        padding: 12px 16px; border-radius: 15px; margin: 8px 0;
        font-size: 15px; line-height: 1.5; max-width: 85%;
        box-shadow: 1px 2px 6px rgba(0,0,0,0.06); word-wrap: break-word;
    }
    .user { background: #fce4ec; color: #880e4f; margin-left: auto; text-align: right; }
    .bot { background: #e3f2fd; color: #0d47a1; margin-right: auto; text-align: left; }
    </style>
""", unsafe_allow_html=True)

# Chatbot logic
def get_chatbot_reply(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You are Solace AI, a warm and friendly mental health companion. "
                "Reply casually like a best friend. If the user expresses sadness, anxiety, or stress, "
                "offer empathy 💗, a motivational quote 🧘, and a calming exercise 🌿. "
                "If it's a normal conversation, just chat like a friendly buddy with emojis."
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

# Login Page
def login_page():
    st.title("🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            users = st.session_state.users
            if username in users and users[username] == password:
                st.session_state.auth = True
                st.session_state.username = username
                st.session_state.page = "Dashboard"
                st.success(f"Welcome back, {username} 👋")
            else:
                st.error("Invalid credentials. Please sign up.")

# Signup Page
def signup_page():
    st.title("📝 Sign Up for Solace AI")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        signup_btn = st.form_submit_button("Sign Up")
        if signup_btn:
            if not new_user or not new_pass:
                st.warning("Both fields are required.")
            elif new_user in st.session_state.users:
                st.error("Username already exists.")
            else:
                st.session_state.users[new_user] = new_pass
                save_users(st.session_state.users)
                st.success("Account created! Please login.")
                st.session_state.page = "Login"

# Dashboard Page
def dashboard():
    st.title(f"👋 Hello, {st.session_state.username}!")
    st.write("Welcome to **Solace AI**, your personal mental health support companion 💬")
    if st.button("🧠 Start Chatbot"):
        st.session_state.show_chatbot = True

# Chatbot Page
def chat_page():
    st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your mental health buddy is here 💗</p>", unsafe_allow_html=True)

    # Display chat history
    for role, msg in st.session_state.chat:
        css = "user" if role == "user" else "bot"
        st.markdown(f"<div class='message {css}'>{msg}</div>", unsafe_allow_html=True)

    # Input and Send
    user_input = st.text_input("You:", key="user_input_buffer", label_visibility="collapsed")
    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat.append(("user", user_input))
            with st.spinner("Solace is typing..."):
                reply = get_chatbot_reply(user_input)
            st.session_state.chat.append(("bot", reply))
            st.session_state.user_input_buffer = ""  # Safe reset
            st.experimental_rerun()

    # Sidebar
    st.sidebar.title("👤 Account")
    st.sidebar.write(f"Logged in as: `{st.session_state.username}`")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.username = ""
        st.session_state.chat = []
        st.session_state.page = "Login"
        st.session_state.show_chatbot = False
        st.experimental_rerun()

# Page Controller
if not st.session_state.auth:
    st.sidebar.title("🔐 Access")
    st.session_state.page = st.sidebar.radio("Choose page", ["Login", "Sign Up"])
    if st.session_state.page == "Login":
        login_page()
    else:
        signup_page()
elif st.session_state.show_chatbot:
    chat_page()
else:
    dashboard()
