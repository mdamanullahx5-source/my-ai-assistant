import streamlit as st
from google import genai

# অ্যাপের টাইটেল ও পেজ সেটআপ
st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 My Personal AI Assistant")

# Gemini Client কনফিগারেশন (আপনার API Key দিন)
API_KEY = "YOUR_GEMINI_API_KEY_HERE"
client = genai.Client(api_key=API_KEY)

# চ্যাট হিস্ট্রি ধরে রাখার মেমোরি
if "messages" not in st.session_state:
    st.session_state.messages = []

# পূর্বের মেসেজগুলো ডিসপ্লে করা
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ব্যবহারকারীর ইনপুট নেওয়া
if prompt := st.chat_input("কী জানতে চান লিখুন..."):
    # ইউজার মেসেজ দেখান
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini থেকে উত্তর আনা
    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})