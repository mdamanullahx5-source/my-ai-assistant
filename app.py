import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

# অ্যাপ পেজ সেটআপ
st.set_page_config(page_title="Multimodal AI Assistant", page_icon="🤖", layout="centered")

# সাইডবার ডিজাইন ও ফাইল আপলোড অপশন
with st.sidebar:
    st.title("⚙️ সেটিংস ও ফাইল আপলোড")
    st.write("ছবি বা টেক্সট ফাইল আপলোড করুন")
    
    # ফাইল আপলোড করার উইজেট (ছবি বা টেক্সট ফাইল)
    uploaded_file = st.file_uploader(
        "একটি ছবি বা ফাইল বেছে নিন", 
        type=["png", "jpg", "jpeg", "txt", "md"]
    )
    
    if uploaded_file:
        st.success("ফাইল সফলভাবে আপলোড হয়েছে!")
        if uploaded_file.type.startswith("image/"):
            image_preview = Image.open(uploaded_file)
            st.image(image_preview, caption="আপলোড করা ছবি", use_container_width=True)

    st.markdown("---")
    
    # চ্যাট হিস্ট্রি মুছে ফেলার বাটন
    if st.button("🗑️ চ্যাট হিস্ট্রি মুছুন (Clear Chat)", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("🚀 **মডেল:** Gemini 3.8 Flash (Multimodal)")

# মূল চ্যাট ইন্টারফেস টাইটেল
st.title("🤖 Personal Multimodal AI Assistant")

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
if prompt := st.chat_input("ফাইল সম্পর্কে কিছু জানতে চান বা প্রশ্ন করুন..."):
    # ইউজারের মেসেজ হিস্টরিতে যোগ করা
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_file and uploaded_file.type.startswith("image/"):
            st.image(Image.open(uploaded_file), width=250)

    with st.chat_message("assistant"):
        try:
            # কন্টেন্ট লিস্ট তৈরি করা (প্রম্পট এবং ফাইল একসাথে পাঠানোর জন্য)
            contents = [prompt]
            
            if uploaded_file:
                if uploaded_file.type.startswith("image/"):
                    # ছবি হলে PIL Image অবজেক্ট যুক্ত করা
                    img = Image.open(uploaded_file)
                    contents.append(img)
                elif uploaded_file.type in ["text/plain", "text/markdown"]:
                    # টেক্সট ফাইল হলে তার ভেতরের লেখা পড়ে যুক্ত করা
                    text_data = uploaded_file.getvalue().decode("utf-8")
                    contents.append(f"\n\nDocument Content:\n{text_data}")

            # সিস্টেম প্রম্পট
            system_instruction = (
                "আপনি একজন অত্যন্ত দক্ষ মাল্টিমোডাল এআই অ্যাসিস্ট্যান্ট। "
                "ব্যবহারকারী কোনো ছবি বা ডকুমেন্ট দিলে তা গভীরভাবে বিশ্লেষণ করে খুব সুন্দর, "
                "সহজ এবং সাবলীল বাংলায় উত্তর দেবেন।"
            )

            # জেমিনি থেকে রেসপন্স আনা
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"এরর ঘটেছে: {e}")
