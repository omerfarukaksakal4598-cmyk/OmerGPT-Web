import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. MODEL HATASINI ÇÖZEN FONKSİYON ---
def model_yanit_al(prompt, contents=None):
    denenecek_modeller = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    last_error = ""
    for model_adi in denenecek_modeller:
        try:
            model = genai.GenerativeModel(model_name=model_adi)
            response = model.generate_content([prompt] + contents) if contents else model.generate_content(prompt)
            return response.text
        except:
            continue
    return "❌ Bağlantı hatası. Lütfen API anahtarını veya internetini kontrol et."

# --- 3. GİRİŞ DURUMU & CSS ---
if "user" not in st.session_state: st.session_state.user = None

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #444746; }
    .stButton > button { border-radius: 20px !important; width: 100%; text-align: left; padding-left: 15px; }
    .nav-link { color: #8ab4f8 !important; text-decoration: none; font-size: 16px; display: flex; align-items: center; gap: 10px; padding: 10px; }
    .nav-link:hover { background-color: #282a2d; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ÜST BAR - GİRİŞ
col_t1, col_t2 = st.columns([5, 1])
with col_t2:
    if st.session_state.user is None:
        if st.button("🔐 Giriş Yap"): st.session_state.show_login = True
    else:
        if st.button(f"👤 {st.session_state.user} (Çıkış)"): 
            st.session_state.user = None
            st.rerun()

if st.session_state.get("show_login", False) and st.session_state.user is None:
    with st.expander("Giriş Yap", expanded=True):
        u = st.text_input("E-posta")
        if st.button("Onayla"):
            st.session_state.user = u if u else "Kullanıcı"
            st.session_state.show_login = False
            st.rerun()

# --- 4. YAN MENÜ (ISTEDIĞIN BUTONLAR BURADA) ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("🚀 **Hızlı Komutlar**")
    
    # Geri getirdiğimiz linkler:
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-link">🌐 Google\'ı Aç</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-link">📺 YouTube\'u Aç</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    
    st.info("Hata düzeltme modu aktif.")

# --- 5. ANA EKRAN ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya/Resim Yükle", type=["pdf", "docx", "png", "jpg", "jpeg"])
extra = []
if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        txt = "".join([p.extract_text() for p in reader.pages])
        extra.append(f"Döküman: {txt}")
        st.success("PDF Hazır!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra.append(img)
        st.image(img, width=200)

# Sohbet
if "messages" not in st.session_state: st.session_state.messages = []
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Düşünüyorum..."):
        yanit = model_yanit_al(prompt, extra if extra else None)
        with st.chat_message("assistant"): st.markdown(yanit)
        st.session_state.messages.append({"role": "assistant", "content": yanit})