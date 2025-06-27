import streamlit as st
import openai
import streamlit_authenticator as stauth

# Load API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# User credentials
names = ['Harshitha']
usernames = ['harshitha']
hashed_passwords = st.secrets["credentials"]["passwords"]

# Authenticator
authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    "mentalhealth_chat", "abcdef", cookie_expiry_days=1
)

# Login
name, authentication_status, username = authenticator.login("Login", location="main")

st.set_page_config(page_title="Mental Health Chatbot", layout="centered")

# Chatbot response
def get_mental_health_reply(user_input):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a supportive mental health assistant."},
            {"role": "user", "content": f"""
                A user said: '{user_input}'.
                Please reply with:
                1. A kind and empathetic message.
                2. A motivational quote.
                3. A simple calming exercise.
                4. A reminder to rest or eat if needed.
            """}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content

# Interface
if authentication_status:
    st.markdown("<h1 style='color:#5cdb95;'>🌿 Mental Health Support</h1>", unsafe_allow_html=True)
    st.markdown("Welcome, **{}**! Share your thoughts below:".format(name))

    user_input = st.text_area("How are you feeling today?", height=150)

    if st.button("💬 Get Support"):
        if user_input.strip() == "":
            st.warning("Please enter your thoughts.")
        else:
            with st.spinner("Thinking..."):
                reply = get_mental_health_reply(user_input)
                st.success("Here's something for you:")
                st.write(reply)

    authenticator.logout("Logout", "sidebar")

elif authentication_status is False:
    st.error("Username or password is incorrect.")
elif authentication_status is None:
    st.warning("Please enter your credentials.")
