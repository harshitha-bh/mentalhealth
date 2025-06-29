import streamlit as st
import openai
import time

# Page Setup
st.set_page_config(page_title="Solace AI", layout="centered")

# Embedded CSS: Therapy Pastel Theme + Mobile-Friendly
st.markdown("""
    <style>
    body {
        background-color: #fdfdfd;
        font-family: 'Segoe UI', sans-serif;
    }

    .title {
        color: #6a1b9a;
        text-align: center;
        font-weight: bold;
        font-size: 2.2em;
        margin-bottom: 0.1em;
    }

    .subtitle {
        text-align: center;
        font-style: italic;
        color: #888;
        margin-bottom: 30px;
        font-size: 1em;
    }

    .message {
        padding: 14px 18px;
        border-radius: 15px;
        margin: 8px 0;
        max-width: 90%;
        font-size: 15.8px;
        line-height: 1.5;
        box-shadow: 1px 2px 6px rgba(0,0,0,0.06);
        word-wrap: break-word;
    }

    .user {
        background: #ffe0f0;
        text-align: right;
        color: #880e4f;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }

    .bot {
        background: #e3f2fd;
        text-align: left;
        color: #0d47a1;
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }

    .typing {
        font-style: italic;
        color: #999;
        padding: 8px;
        font-size: 14px;
    }

    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-thumb {
        background-color: #bbb;
        border-radius: 10px;
    }

    @media screen and (max-width: 600px) {
        .message {
            font-size: 15px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Session State Defaults
if "auth" not in st.session_state:
    st.session_state.auth = False
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "users" not in st.session_state:
    st.session_state.users = {"demo": "demo123"}
if "chat" not in st.session_state:
    st.session_state.chat = []

# Login Form
def login():
    st.title("🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.auth = True
                st.success(f"Welcome back, {username}!")
            else:
                st.error("User not found or incorrect password. Please Sign Up if you don't have an account.")

# Signup Form
def signup():
    st.title("📝 Sign Up for Solace AI")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if not new_user or not new_pass:
                st.warning("All fields are required.")
            elif new_user in st.session_state.users:
                st.error("Username already exists. Please choose another.")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Account created! Please log in.")
                st.session_state.mode = "login"

# Login or Signup
if not st.session_state.auth:
    st.sidebar.title("Account")
    st.session_state.mode = st.sidebar.radio("Choose", ["Login", "Sign Up"])
    if st.session_state.mode == "Login":
        login()
    else:
        signup()
    st.stop()

# OpenAI API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Smart Chatbot Reply
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

# Typing Effect (Optional Visual Feel)
def typing_effect(message):
    with st.empty():
        typed = ""
        for char in message:
            typed += char
            time.sleep(0.01)
            st.markdown(typed + "▌")
        st.markdown(typed)

# UI Title
st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your personal mental health companion 💬</p>", unsafe_allow_html=True)

# Show Chat History
chat_placeholder = st.container()
with chat_placeholder:
    for role, msg in st.session_state.chat:
        css_class = "user" if role == "user" else "bot"
        st.markdown(f"<div class='message {css_class}'>{msg}</div>", unsafe_allow_html=True)

# Input Form
with st.form("chat_input_form", clear_on_submit=True):
    user_input = st.text_area("You:", height=80, key="chat_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        st.session_state.chat.append(("user", user_input))
        with st.spinner("💬 Solace is typing..."):
            reply = get_smart_reply(user_input)
            st.session_state.chat.append(("bot", reply))
            st.rerun()  # Real-time flow
