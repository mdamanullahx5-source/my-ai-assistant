import streamlit as st
from google import genai

# অ্যাপ পেজ সেটআপ
st.set_page_config(page_title="My AI Assistant", page_icon="🤖", layout="centered")

# সাইডবার ডিজাইন ও ফিচার
with st.sidebar:
    st.title("⚙️ সেটিংস")
    st.write("আপনার পার্সোনাল এআই অ্যাসিস্ট্যান্ট")
    
    # চ্যাট হিস্ট্রি মুছে ফেলার বাটন
    if st.button("🗑️ চ্যাট হিস্ট্রি মুছুন (Clear Chat)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("🚀 **তৈরি করেছেন:** আপনি নিজে")
    st.markdown("💡 **মডেল:** Gemini Flash")

# মূল চ্যাট ইন্টারফেস টাইটেল
st.title("🤖 My Personal AI Assistant")

# Secrets অথবা Direct Key থেকে API Key গ্রহণ
api_key = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
client = genai.Client(api_key=api_key)

# চ্যাট হিস্ট্রি ইনিশিয়ালাইজেশন
if "messages" not in st.session_state:
    st.session_state.messages = []

# পূর্বের মেসেজগুলো ডিসপ্লে করা
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
                model='gemini-3.8-flash',
                contents=prompt
            )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"সার্ভারে এই মুহূর্তে অতিরিক্ত চাপ রয়েছে (503 Error)। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।")
