import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. AYARLAR ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Web", page_icon="🤖", layout="wide")

# --- 2. MODELİ OTOMATİK BULMA ---
def en_uygun_modeli_bul(gorsel_mi=False):
    # Sistemdeki modelleri tara ve uygun olanı seç
    try:
        modeller = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if gorsel_mi:
            # Önce 1.5 flash dene, yoksa vision dene
            for m in modeller:
                if 'gemini-1.5-flash' in m: return m
                if 'vision' in m: return m
        else:
            for m in modeller:
                if 'gemini-1.5-flash' in m: return m
                if 'gemini-pro' in m and 'vision' not in m: return m
        return modeller[0] # Hiçbiri tutmazsa ilkini ver
    except:
        return 'gemini-pro' # Hata olursa en garanti model

def model_yanit_al(prompt, img=None):
    try:
        model_adi = en_uygun_modeli_bul(gorsel_mi=True if img else False)
        model = genai.GenerativeModel(model_adi)
        if img:
            res = model.generate_content([prompt, img])
        else:
            res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 3. ARAYÜZ ---
st.title("🚀 ÖmerGPT Ultra Web")

if "messages" not in st.session_state:
    st.session_state.messages = []

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
    soru = st.text_input("Görsel hakkında sorun:", value="Bu fotoğrafta ne görüyorsun? Tahmin et.")
    if st.button("🤖 Görseli Analiz Et"):
        with st.spinner("ÖmerGPT bakıyor..."):
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