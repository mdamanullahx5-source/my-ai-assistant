import streamlit as st
from google import genai

# অ্যাপ পেজ সেটআপ
st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Personal AI Assistant")

# Secrets অথবা Direct Key থেকে API Key গ্রহণ
api_key = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
client = genai.Client(api_key=api_key)

# চ্যাট হিস্ট্রি
if "messages" not in st.session_state:
    st.session_state.messages = []

# মেসেজ দেখান
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজার ইনপুট ও উত্তর জেনারেট
if prompt := st.chat_input("কী জানতে চান লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error occurred: {e}")
