import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# অ্যাপ পেজ সেটআপ
st.set_page_config(page_title="Siri Style AI Assistant", page_icon="🎙️", layout="centered")

# --- কাস্টম CSS ডিজাইন (সিরির মতো প্রিমিয়াম লুক) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    h1 {
        color: #00d2ff;
        text-align: center;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #161b22;
    }
</style>
""", unsafe_allow_html=True)

# --- সাইডবার ও সেটিংস ---
with st.sidebar:
    st.title("🎙️ Siri Settings")
    st.write("আপনার পার্সোনাল ভয়েস অ্যাসিস্ট্যান্ট")
    
    uploaded_file = st.file_uploader("ছবি বা ফাইল আপলোড করুন", type=["png", "jpg", "jpeg", "txt"])
    
    if uploaded_file and uploaded_file.type.startswith("image/"):
        st.image(Image.open(uploaded_file), caption="అప్లోড করা ছবি", use_container_width=True)

    st.markdown("---")
    
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "".join([f"{m['role']}: {m['content']}\n\n" for m in st.session_state.messages])
        st.download_button("📥 চ্যাট হিস্ট্রি ডাউনলোড", data=chat_text, file_name="siri_chat.txt", use_container_width=True)

    if st.button("🗑️ চ্যাট ক্লিয়ার করুন", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- মূল ইন্টারফেস ---
st.title("Siri 🍏 AI Assistant")
st.markdown("<p style='text-align: center; color: #8b949e;'>আপনার ব্যক্তিগত এআই, সিরির মতো স্মার্ট</p>", unsafe_allow_html=True)

# Gemini Client কনফিগারেশন
api_key = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজার ইনপুট
if prompt := st.chat_input("কী জানতে চান বলুন বা লিখুন..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            contents = [prompt]
            if uploaded_file:
                if uploaded_file.type.startswith("image/"):
                    contents.append(Image.open(uploaded_file))
                elif uploaded_file.type in ["text/plain", "text/markdown"]:
                    contents.append(uploaded_file.getvalue().decode("utf-8"))

            # সিরির মতো ব্যক্তিত্ব বা সিস্টেম প্রম্পট
            system_instruction = (
                "আপনি অ্যাপলের 'Siri'-এর মতো অত্যন্ত স্মার্ট, সংক্ষিপ্ত, মার্জিত এবং বন্ধুসুলভ একজন এআই অ্যাসিস্ট্যান্ট। "
                "ব্যবহারকারীর প্রশ্নের খুব নিখুঁত, সুন্দর এবং সাবলীল বাংলায় উত্তর দেবেন।"
            )

            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=contents,
                config=types.GenerateContentConfig(system_instruction=system_instruction)
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # সিরির মতো ভয়েস আউটপুট (Browser Speech Synthesis) দেওয়ার জাভাস্ক্রিপ্ট কোড
            tts_script = f"""
            <script>
                const text = `{response.text.replace("'", "").replace('"', '')}`;
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'bn-BD'; // বাংলা ভয়েস
                window.speechSynthesis.speak(utterance);
            </script>
            """
            st.markdown(tts_script, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"সার্ভারে সমস্যা হচ্ছে: {e}")
