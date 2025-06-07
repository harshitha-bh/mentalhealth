import streamlit as st
import openai

# Load API key securely (either from Streamlit secrets or directly)
openai.api_key = st.secrets["OPENAI_API_KEY"] if "OPENAI_API_KEY" in st.secrets else "your-api-key-here"

# Function to generate mental health support reply
def get_mental_health_reply(user_input):
    messages = [
        {"role": "system", "content": "You are a kind and supportive mental health assistant."},
        {"role": "user", "content": f"""
A user said: "{user_input}"

Please respond with:
- A supportive and empathetic message.
- A motivational quote or affirmation.
- A simple mental exercise to help them feel better.
- Remind them gently to take rest or eat if needed.
"""}
    ]

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content

# Streamlit UI
st.set_page_config(page_title="Solace AI - Mental Health Chatbot", page_icon="🧠", layout="centered")
st.title("🧘‍♀️ Solace AI - Mental Health Support Chatbot")
st.markdown("Share how you feel. I’m here to help you feel a little better.")

user_input = st.text_area("How are you feeling today?", height=150)

if st.button("Get Support"):
    if user_input.strip():
        with st.spinner("Thinking warm thoughts..."):
            reply = get_mental_health_reply(user_input)
            st.success("Here's something that may help:")
            st.markdown(reply)
    else:
        st.warning("Please enter your feelings first.")
