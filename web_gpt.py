import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. AYARLAR ---
# Kendi API Key'ini buraya yapıştır
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Web", page_icon="🤖", layout="wide")

# --- 2. MODEL ÇAĞIRMA FONKSİYONU ---
def model_yanit_al(prompt, img=None):
    try:
        if img:
            # Görsel varsa görsel modelini kullan
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content([prompt, img])
        else:
            # Sadece metin varsa metin modelini kullan
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 3. ARAYÜZ ---
st.title("🚀 ÖmerGPT Ultra Web")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Yan Menü
with st.sidebar:
    st.header("🛠️ Menü")
    if st.button("🧹 Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("[🌐 Google](https://google.com)")
    st.markdown("[📺 YouTube](https://youtube.com)")

# --- 4. GÖRSEL BÖLÜMÜ ---
st.write("### 📸 Görsel Analiz")
col1, col2 = st.columns(2)
with col1:
    up = st.file_uploader("Fotoğraf Yükle", type=["jpg", "png", "jpeg"])
with col2:
    cam = st.camera_input("Fotoğraf Çek")

secilen_resim = cam if cam else up

if secilen_resim:
    img = Image.open(secilen_resim)
    st.image(img, width=300)
    soru = st.text_input("Görsel hakkında sorun:", value="Bu fotoğrafta ne var?")
    if st.button("🤖 Görseli Analiz Et"):
        with st.spinner("Bakıyorum..."):
            cevap = model_yanit_al(soru, img)
            st.success(f"ÖmerGPT: {cevap}")

st.markdown("---")

# --- 5. SOHBET BÖLÜMÜ ---
st.write("### 💬 Sohbet")
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Düşünüyorum..."):
        cevap = model_yanit_al(prompt)
        with st.chat_message("assistant"):
            st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})