import streamlit as st
import google.generativeai as genai
from PIL import Image
import webbrowser

# --- 1. AYARLAR ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Web", page_icon="🤖", layout="wide")

# --- 2. MODEL KURULUMU ---
def model_getir():
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        system_instruction="Senin adın OmerGPT. Kullanıcının kankasısın. Cevapların çok kısa, samimi ve net olsun. Asla emoji kullanma."
    )

# --- 3. ARAYÜZ VE STİL ---
st.title("🚀 ÖmerGPT Ultra Web")
st.subheader("Her şey tek ekranda!")

# Sohbet hafızası
if "messages" not in st.session_state:
    st.session_state.messages = []

# Yan Menü (PC Komutları ve Butonlar)
with st.sidebar:
    st.header("🛠️ Hızlı Komutlar")
    if st.button("🌐 Google'ı Aç"):
        st.write("Bilgisayarda olsaydık açardım ama buradan link verebilirim:")
        st.markdown("[Google'a Git](https://google.com)")
    
    if st.button("📺 YouTube'u Aç"):
        st.markdown("[YouTube'a Git](https://youtube.com)")
        
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

# --- 4. GÖRSEL ÖZELLİKLER (KAMERA VE DOSYA) ---
st.write("### 📸 Görsel Analiz")
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Bir fotoğraf yükle...", type=["jpg", "png", "jpeg"])
with col2:
    camera_file = st.camera_input("Veya fotoğraf çek!")

resim = camera_file if camera_file else uploaded_file

if resim:
    st.image(resim, caption="Analiz edilecek görsel", width=300)
    img_soru = st.text_input("Görselle ilgili sorun nedir?")
    if st.button("🤖 Görseli Yorumla"):
        with st.spinner("ÖmerGPT bakıyor..."):
            model = model_getir()
            img = Image.open(resim)
            response = model.generate_content([img_soru if img_soru else "Bu fotoğrafta ne var? Kısaca anlat.", img])
            st.success(f"ÖmerGPT: {response.text}")

st.markdown("---")

# --- 5. SOHBET AKIŞI ---
st.write("### 💬 Sohbet")

# Mesajları göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Yeni mesaj girişi
if prompt := st.chat_input("Naber kanka?"):
    # Kullanıcı mesajı
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Bot cevabı
    try:
        with st.spinner("Düşünüyorum..."):
            model = model_getir()
            # Hafızayı modele gönder (son 5 mesaj)
            chat = model.start_chat(history=[])
            response = chat.send_message(prompt)
            
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
    except Exception as e:
        st.error(f"Bir hata oldu knkk: {e}")