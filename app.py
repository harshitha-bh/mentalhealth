import streamlit as st
import openai
import time

# ---------- Page Setup ----------
st.set_page_config(page_title="Solace AI", layout="centered")

# ---------- Embedded CSS Styling ----------
st.markdown("""
    <style>
    .title {
        color: #4CAF50;
        font-family: 'Segoe UI', sans-serif;
        text-align: center;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        font-style: italic;
        color: #666;
        margin-top: 0;
    }
    .message {
        padding: 12px 16px;
        border-radius: 12px;
        margin-bottom: 10px;
        max-width: 90%;
        font-size: 16px;
        line-height: 1.5;
    }
    .user {
        background-color: #d1f1d1;
        text-align: right;
        color: #0a3d62;
        margin-left: auto;
    }
    .bot {
        background-color: #e1eaff;
        text-align: left;
        color: #4a148c;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)


# ---------- Session State ----------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "users" not in st.session_state:
    st.session_state.users = {"demo": "demo123"}
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------- Login/Signup Forms ----------
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

# ---------- Show Auth Forms ----------
if not st.session_state.auth:
    st.sidebar.title("Account")
    st.session_state.mode = st.sidebar.radio("Choose", ["Login", "Sign Up"])
    if st.session_state.mode == "Login":
        login()
    else:
        signup()
    st.stop()

# ---------- OpenAI Key ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ---------- Chatbot Logic ----------
def get_smart_reply(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You're Solace AI, a friendly mental health chatbot who talks like a chill friend. "
                "Be casual and warm. Use emojis. If the user expresses stress, anxiety, or sadness, then give a short motivational quote, calming exercise, and reminder to rest. "
                "Otherwise, just chat casually like a close buddy."
            )
        },
        {"role": "user", "content": user_input}
    ]
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# ---------- Typing Animation ----------
def typing_effect(message):
    with st.empty():
        typed = ""
        for char in message:
            typed += char
            time.sleep(0.01)
            st.markdown(typed + "▌")
        st.markdown(typed)

# ---------- Chat UI ----------
st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your supportive mental health companion.</p>", unsafe_allow_html=True)

chat_placeholder = st.container()
with chat_placeholder:
    for role, msg in st.session_state.chat:
        css_class = "user" if role == "user" else "bot"
        st.markdown(f"<div class='message {css_class}'>{msg}</div>", unsafe_allow_html=True)

with st.form("chat_input_form", clear_on_submit=True):
    user_input = st.text_area("You:", height=80, key="chat_input")
    submitted = st.form_submit_button("Send")
    if submitted and user_input.strip():
        st.session_state.chat.append(("user", user_input))
        with st.spinner("Solace is typing..."):
            reply = get_smart_reply(user_input)
            st.session_state.chat.append(("bot", reply))
            st.rerun()  # Real-time chat experience
