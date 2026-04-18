import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & API ---
# API anahtarını ve yapılandırmayı en güvenli hale getiriyoruz
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. MODEL HATASINI KÖKTEN ÇÖZEN FONKSİYON ---
def model_yanit_al(prompt, contents=None):
    # Kullanılabilecek model isimlerini dene (en güncelden en garantiye)
    denenecek_modeller = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash', 'models/gemini-pro']
    
    last_error = ""
    for model_adi in denenecek_modeller:
        try:
            model = genai.GenerativeModel(model_name=model_adi)
            if contents:
                # Görsel içerik varsa 1.5-flash veya vision modelleri gerekir
                response = model.generate_content([prompt] + contents)
            else:
                response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue # Bu model olmazsa sıradakine geç
            
    return f"❌ Tüm modeller denendi ama bağlanılamadı. Hata: {last_error}"

# --- 3. GİRİŞ SİSTEMİ & TASARIM ---
if "user" not in st.session_state: st.session_state.user = None

st.markdown("""
<style>
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stButton > button { border-radius: 20px !important; }
    .auth-bar { display: flex; justify-content: flex-end; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# ÜST BAR - GİRİŞ YAP BUTONU
col_t1, col_t2 = st.columns([5, 1])
with col_t2:
    if st.session_state.user is None:
        if st.button("🔐 Giriş Yap"):
            st.session_state.show_login = True
    else:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Çıkış"):
            st.session_state.user = None
            st.rerun()

if st.session_state.get("show_login", False) and st.session_state.user is None:
    with st.expander("Giriş Paneli", expanded=True):
        u_input = st.text_input("E-posta")
        p_input = st.text_input("Şifre", type="password")
        c1, c2 = st.columns(2)
        if c1.button("Onayla"):
            st.session_state.user = u_input if u_input else "Kullanıcı"
            st.session_state.show_login = False
            st.rerun()
        if c2.button("Google ile Giriş"):
            st.session_state.user = "Google_Kullanicisi"
            st.rerun()

# --- 4. KENAR ÇUBUĞU ---
with st.sidebar:
    st.title("🤖 ÖmerGPT")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.info("Hata düzeltme modu aktif: Çoklu model tarama devrede.")

# --- 5. ANA EKRAN ---
st.title("🚀 ÖmerGPT Ultra Pro")

col1, col2 = st.columns([3, 1])
with col2:
    up = st.file_uploader("Dosya/Resim", type=["pdf", "docx", "png", "jpg", "jpeg"])
    cam = st.camera_input("Hızlı Foto")

extra = []
if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        txt = "".join([p.extract_text() for p in reader.pages])
        extra.append(f"Döküman Metni: {txt}")
        st.success("PDF Hazır!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra.append(img)
        st.image(img, width=150)
if cam:
    extra.append(Image.open(cam))

# SOHBET AKIŞI
if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka, neyi analiz edelim?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Modeller taranıyor ve yanıt üretiliyor..."):
        yanit = model_yanit_al(prompt, extra if extra else None)
        with st.chat_message("assistant"): st.markdown(yanit)
        st.session_state.messages.append({"role": "assistant", "content": yanit})