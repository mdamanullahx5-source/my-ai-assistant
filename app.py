import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import os

# অ্যাপ পেজ কনফিগারেশন
st.set_page_config(
    page_title="Ultimate Siri AI Assistant", 
    page_icon="🍏", 
    layout="centered"
)

# --- কাস্টম CSS ডিজাইন (সিরির মতো প্রিমিয়াম ডার্ক লুক) ---
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
    .stChatMessage {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- সাইডবার কন্ট্রোল সেন্টার ---
with st.sidebar:
    st.title("⚙️ Siri Control Center")
    st.write("আপনার অল-ইন-ওয়ান পার্সোনাল এআই")
    
    st.markdown("---")
    st.subheader("📁 ফাইল বা ছবি আপলোড")
    uploaded_file = st.file_uploader(
        "ছবি বা টেক্সট ফাইল বেছে নিন", 
        type=["png", "jpg", "jpeg", "txt", "md"]
    )
    
    if uploaded_file and uploaded_file.type.startswith("image/"):
        st.image(Image.open(uploaded_file), caption="আপলোড করা প্রিভিউ", use_container_width=True)

    st.markdown("---")
    st.subheader("🎛️ মডেল সেটিংস")
    # ক্রিয়েটিভিটি বা টেম্পারেচার কন্ট্রোল স্লাইডার
    temperature = st.slider(
        "ক্রিয়েটিভিটি (Temperature)", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.7, 
        step=0.1,
        help="কম হলে সঠিক ও নিখুঁত উত্তর দেবে, বেশি হলে ক্রিয়েটিভ ও ভিন্নধর্মী উত্তর দেবে।"
    )

    st.markdown("---")
    # চ্যাট হিস্ট্রি ডাউনলোড বাটন
    if "messages" in st.session_state and st.session_state.messages:
        chat_text = "".join([f"{m['role'].upper()}: {m['content']}\n\n" for m in st.session_state.messages])
        st.download_button(
            "📥 চ্যাট হিস্ট্রি ডাউনলোড",
            data=chat_text,
            file_name="ultimate_siri_chat.txt",
            mime="text/plain",
            use_container_width=True
        )

    # চ্যাট ক্লিয়ার বাটন
    if st.button("🗑️ চ্যাট ক্লিয়ার করুন", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    st.markdown("🚀 **মডেল:** Gemini 3.8 Flash")

# --- মূল চ্যাট ইন্টারফেস ---
st.title("Siri 🍏 AI Assistant")
st.markdown("<p style='text-align: center; color: #8b949e;'>মুখে বলুন, ছবি দেখান কিংবা লিখে চ্যাট করুন</p>", unsafe_allow_html=True)

# --- ভয়েস ইনপুট (Microphone Recorder) ---
st.markdown("### 🎙️ ভয়েস কমান্ড")
audio_data = mic_recorder(
    start_prompt="🎙️ কথা বলতে এখানে ক্লিক করুন",
    stop_prompt="⏹️ বলা শেষ (Stop)",
    key='ultimate_mic'
)

# Gemini Client কনফিগারেশন
api_key = st.secrets.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
client = genai.Client(api_key=api_key)

# চ্যাট হিস্ট্রি স্টেট ইনিশিয়ালাইজেশন
if "messages" not in st.session_state:
    st.session_state.messages = []

# পূর্বের মেসেজগুলো রেন্ডার করা
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ইউজার ইনপুট (টেক্সট অথবা ভয়েস)
prompt = st.chat_input("কী জানতে চান লিখুন...")

voice_audio_bytes = None
if audio_data:
    voice_audio_bytes = audio_data['bytes']
    prompt = "দয়া করে এই ভয়েস নোটটি শুনুন এবং এর সঠিক উত্তর বাংলায় দিন।"

if prompt or voice_audio_bytes:
    display_prompt = prompt if prompt and not voice_audio_bytes else "🎤 [ভয়েস মেসেজ]"
    st.session_state.messages.append({"role": "user", "content": display_prompt})
    
    with st.chat_message("user"):
        st.markdown(display_prompt)

    with st.chat_message("assistant"):
        try:
            contents = []
            
            # যদি ভয়েস অডিও রেকর্ড করা হয়
            if voice_audio_bytes:
                contents.append(
                    types.Part.from_bytes(
                        data=voice_audio_bytes,
                        mime_type="audio/wav",
                    )
                )
                contents.append("এই ভয়েস মেসেজটিতে কী বলা হয়েছে বা কী প্রশ্ন করা হয়েছে, তার সঠিক উত্তর বাংলায় দিন।")
            else:
                contents.append(prompt)

            # যদি ছবি বা ফাইল আপলোড করা হয়
            if uploaded_file:
                if uploaded_file.type.startswith("image/"):
                    contents.append(Image.open(uploaded_file))
                elif uploaded_file.type in ["text/plain", "text/markdown"]:
                    contents.append(uploaded_file.getvalue().decode("utf-8"))

            # সিরির মতো পার্সোনাল সিস্টেম প্রম্পট
            system_instruction = (
                "আপনি অ্যাপলের 'Siri'-এর মতো অত্যন্ত স্মার্ট, সংক্ষিপ্ত, মার্জিত এবং বন্ধুসুলভ একজন এআই অ্যাসিস্ট্যান্ট। "
                "ব্যবহারকারীর প্রশ্নের খুব নিখুঁত, সুন্দর এবং সাবলীল বাংলায় উত্তর দেবেন।"
            )

            # জেমিনি এপিআই কল (কনফিগারেশন ও টেম্পারেচারসহ)
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=temperature
                )
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # gTTS দিয়ে বাংলায় ভয়েস আউটপুট তৈরি এবং প্লে করা
            try:
                tts = gTTS(text=response.text, lang='bn', slow=False)
                audio_file = "response_audio.mp3"
                tts.save(audio_file)
                st.audio(audio_file, format="audio/mp3", autoplay=True)
            except Exception as voice_err:
                st.info("ভয়েস আউটপুট তৈরি করতে সমস্যা হয়েছে, তবে টেক্সট উত্তর সফলভাবে পাওয়া গেছে।")
            
        except Exception as e:
            st.error(f"সার্ভারে সমস্যা হচ্ছে: {e}")
