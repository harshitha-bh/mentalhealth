import streamlit as st
import openai
import os
import time

# ---------- Streamlit Setup ----------
st.set_page_config(page_title="Solace AI", layout="centered")

# ---------- Embedded CSS Styling ----------
st.markdown("""
    <style>
    .title {
        color: #4CAF50;
        font-family: 'Helvetica Neue', sans-serif;
        text-align: center;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        font-style: italic;
        color: #666;
        margin-top: 0;
    }
    .user-bubble {
        background-color: #d1e7dd;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 10px;
        text-align: right;
    }
    .bot-bubble {
        background-color: #e3e3f3;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 10px;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Mock User Database ----------
if "users" not in st.session_state:
    st.session_state.users = {"demo": "demo123"}

# ---------- Session State ----------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "mode" not in st.session_state:
    st.session_state.mode = "login"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ---------- Authentication Logic ----------
def login():
    st.title("🔐 Login to Solace AI")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login")
        if login_btn:
            if username in st.session_state.users and st.session_state.users[username] == password:
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
            if new_user in st.session_state.users:
                st.error("Username already exists.")
            elif not new_user or not new_pass:
                st.warning("All fields are required.")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Account created! Please log in.")
                st.session_state.mode = "login"

# ---------- Login/Signup Interface ----------
if not st.session_state.auth:
    st.sidebar.title("Account")
    st.session_state.mode = st.sidebar.radio("Choose Mode", ["Login", "Sign Up"])
    if st.session_state.mode == "Login":
        login()
    else:
        signup()
    st.stop()

# ---------- OpenAI Setup ----------
openai.api_key = st.secrets["OPENAI_API_KEY"]

def get_mental_health_reply(user_input):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You're Solace AI, a 20-year-old friendly and chill chatbot who supports users like a close friend. "
                    "Your tone is casual, supportive, and emotionally intelligent. "
                    "When users are just chatting casually, you respond like a human friend — light, informal, with emojis. "
                    "But if a user expresses sadness, stress, anxiety, or emotional distress, then and only then, you should:\n"
                    "- Give a short supportive message\n"
                    "- Include a non-cliché motivational quote\n"
                    "- Suggest a simple calming activity (like a breathing tip)\n"
                    "- Gently remind them to rest or eat if needed\n\n"
                    "Never sound robotic or overly formal. Always keep it natural, comforting, and adaptive to user tone. Use emojis where it feels human."
                )
            },
            {
                "role": "user",
                "content": user_input
            }
        ],
        temperature=0.8,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# ---------- Typing Animation ----------
def typing_effect(text):
    with st.empty():
        typed = ""
        for char in text:
            typed += char
            time.sleep(0.01)
            st.markdown(typed + "▌")
        st.markdown(typed)

# ---------- Main Interface ----------
st.markdown("<h1 class='title'>🌿 Solace AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your supportive mental health companion.</p>", unsafe_allow_html=True)

# ---------- Show Image (.jpeg supported) ----------
image_path = "therapy.jpeg"  # or therapy.jpg
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("### 💬 How are you feeling today?")
user_input = st.text_area("Your message", height=100)

if st.button("🧠 Get Support"):
    if user_input.strip():
        reply = get_mental_health_reply(user_input)
        st.success("Here's what Solace AI says:")
        typing_effect(reply)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("bot", reply))
    else:
        st.warning("Please enter how you're feeling.")

# ---------- Chat History ----------
st.markdown("### 🗒️ Your Conversation")
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='user-bubble'>🧍‍♀️ {msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>🤖 {msg}</div>", unsafe_allow_html=True)
