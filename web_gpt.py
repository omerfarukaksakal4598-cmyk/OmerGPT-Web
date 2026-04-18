import streamlit as st
import google.generativeai as genai
from streamlit_webrtc import webrtc_streamer
import av # Görüntü işleme için lazım

# --- AYARLAR ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)

st.title("🤖 ÖmerGPT Web + Kamera")

# Kamera Bileşeni
ctx = webrtc_streamer(key="sample")

if ctx.video_receiver:
    # Kamera aktifse son kareyi al
    img = ctx.video_receiver.get_frame().to_ndarray(format="bgr24")
    if st.button("Şu anki kareyi analiz et"):
        # Burada görüntüyü Gemini'ye gönderen kod çalışır
        st.write("Görüntü analiz ediliyor...")

# Sohbet Kısmı
prompt = st.chat_input("Naber kanka?")
if prompt:
    st.write(f"Sen: {prompt}")
    # Gemini cevap kodu buraya...