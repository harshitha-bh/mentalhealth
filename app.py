import streamlit as st
import openai
import os
import json

# 🔐 Setup OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 📁 File where usernames/passwords are stored
USER_FILE = "users.json"

# Load & Save users
def load_users():
    return json.load(open(USER_FILE)) if os.path.exists(USER_FILE) else {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# 🌱 Session Initialization
for key, default in {
    "users": load_users(),
    "auth": False,
    "username": "",
    "page": "Login",
    "show_chatbot": False,
    "chat": [],
    "user_input_buffer": "",
    "clear_input_flag": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# 🌈 Styling
st.set_page_config(page_title="Solace AI", layout="centered")
st.markdown("""
<style>
.title { color: #6a1b9a; text-align: center; font-weight: bold; font-size: 2.4em; }
.subtitle { text-align: center; font-style: italic; color: #666; margin-bottom: 20px; }
.message {
    padding: 12px 16px; border-radius: 12px; margin: 8px 0;
    font-size: 15px; line-height: 1.5; max-width: 85%;
    box-shadow: 1px 2px 6px rgba(0,0,0,0.08); word-wrap: break-word;
}
.user { background: #fce4ec; color: #880e4f; margin-left: auto; text-align: right; }
.bot { background: #e3f2fd; color: #0d47a1; margin-right: auto; text-align: left; }
</style>
""", unsafe_allow_html=True)

# 💬 AI Reply Function
def get_chatbot_reply(user_input):
    messages = [
        {
            "role": "system",
            "content": (
                "You are Solace AI, a kind, casual mental health companion. "
                "If user shares sadness/anxiety/stress, give warm support 💗, a motivational quote 🧘, and calming tip 🌿. "
                "If user just chats casually, respond as a close friend with emojis."
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

# 🔐 Login Page
def login_page():
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
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials. Please sign up below.")

# 📝 Sign Up Page
def signup_page():
    st.title("📝 Sign Up for Solace AI")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if not new_user or not new_pass:
                st.warning("Both fields required.")
            elif new_user in st.session_state.users:
                st.error("Username already exists.")
            else:
                st.session_state.users[new_user] = new_pass
                save_users(st.session_state.users)
                st.success("Account created. Please log in.")
                st.session_state.page = "Login"
                st.rerun()

# 🏠 Dashboard
def dashboard():
    st.title(f"👋 Welcome, {st.session_state.username}")
    st.write("You're logged in to **Solace AI**, your friendly mental health companion 💬")
    if st.button("🧠 Start Chatbot"):
        st.session_state.show_chatbot = True
        st.rerun()

# 🤖 Chat Page
def chat_page():
    st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Chat with me anytime 💗</p>", unsafe_allow_html=True)

    # 🧾 Display message history
    for role, msg in st.session_state.chat:
        css = "user" if role == "user" else "bot"
        st.markdown(f"<div class='message {css}'>{msg}</div>", unsafe_allow_html=True)

    # 📥 Chat input
    user_input = st.text_input("Type your message", key="user_input_buffer", label_visibility="collapsed")

    if st.button("Send"):
        if user_input.strip():
            st.session_state.chat.append(("user", user_input))
            with st.spinner("Solace is typing..."):
                reply = get_chatbot_reply(user_input)
            st.session_state.chat.append(("bot", reply))
            st.session_state.clear_input_flag = True
            st.rerun()

    # ✅ Safe clear after rerun
    if st.session_state.clear_input_flag:
        st.session_state.user_input_buffer = ""
        st.session_state.clear_input_flag = False

    # 🔚 Logout sidebar
    st.sidebar.title("👤 Account")
    st.sidebar.write(f"Logged in as: `{st.session_state.username}`")
    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.username = ""
        st.session_state.chat = []
        st.session_state.page = "Login"
        st.session_state.show_chatbot = False
        st.rerun()

# 🔁 Page Controller
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
