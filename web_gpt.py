import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt
import datetime

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. MODEL DEDEKTİFİ (404 HATASINI ÇÖZER) ---
def en_iyi_modeli_bul():
    try:
        modeller = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Tercih sırası: 1.5 Flash -> 1.0 Pro -> Herhangi biri
        for m in modeller:
            if '1.5-flash' in m: return m
        for m in modeller:
            if 'gemini-pro' in m: return m
        return modeller[0]
    except:
        return 'gemini-pro' # En kötü ihtimalle bunu dene

def model_yanit_al(prompt, contents=None):
    try:
        model_adi = en_iyi_modeli_bul()
        model = genai.GenerativeModel(model_adi)
        if contents:
            return model.generate_content([prompt] + contents).text
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Sistem bir hata yakaladı: {str(e)}"

# --- 3. GİRİŞ DURUMU & ARAYÜZ CSS ---
if "user" not in st.session_state:
    st.session_state.user = None

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; }
    .stButton > button { border-radius: 20px !important; }
    .user-info { padding: 10px; background: #1e1f20; border-radius: 10px; border: 1px solid #444746; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 4. ÜST BAR (GİRİŞ KISMI) ---
col_t1, col_t2 = st.columns([5, 1])
with col_t2:
    if st.session_state.user is None:
        if st.button("🔐 Giriş Yap"):
            st.session_state.show_login = True
    else:
        st.write(f"✅ {st.session_state.user}")
        if st.button("Çıkış"):
            st.session_state.user = None
            st.rerun()

# Giriş Penceresi (Pop-up gibi çalışır)
if st.session_state.get("show_login", False) and st.session_state.user is None:
    with st.expander("Giriş Paneli", expanded=True):
        email = st.text_input("E-posta veya Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        c1, c2 = st.columns(2)
        if c1.button("Onayla"):
            st.session_state.user = email if email else "Misafir"
            st.session_state.show_login = False
            st.rerun()
        if c2.button("Google ile Giriş"):
            st.session_state.user = "Google_Kullanicisi"
            st.rerun()

# --- 5. KENAR ÇUBUĞU ---
with st.sidebar:
    st.title("🤖 ÖmerGPT")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("📂 **Dosya Analizi Aktif**")
    st.caption("PDF, Word ve Görsel yükleyebilirsin.")

# --- 6. ANA EKRAN VE DOSYA İŞLEME ---
st.title("🚀 ÖmerGPT Ultra Pro")

col1, col2 = st.columns([3, 1])
with col2:
    up = st.file_uploader("Dosya Analizi", type=["pdf", "docx", "png", "jpg"])
    cam = st.camera_input("Hızlı Foto")

extra = []
if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        txt = "".join([p.extract_text() for p in reader.pages])
        extra.append(f"Döküman İçeriği: {txt}")
        st.success("PDF Hazır!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra.append(img)
        st.image(img, width=150)

# Sohbet Sistemi
if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT yanıtlıyor..."):
        yanit = model_yanit_al(prompt, extra if extra else None)
        with st.chat_message("assistant"): st.markdown(yanit)
        st.session_state.messages.append({"role": "assistant", "content": yanit})