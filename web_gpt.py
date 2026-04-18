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

# --- 2. GİRİŞ SİSTEMİ (LOGIN) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login_ekrani():
    st.markdown("""
        <style>
        .login-box {
            background-color: #1e1f20;
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #444746;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🔐 ÖmerGPT'ye Hoş Geldin")
    
    tab1, tab2 = st.tabs(["📧 E-Posta ile Giriş", "🚀 Google ile Devam Et"])
    
    with tab1:
        email = st.text_input("E-Posta")
        sifre = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap / Kaydol"):
            if email and sifre: # Buraya ileride Firebase bağlayabiliriz
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Lütfen alanları doldur!")

    with tab2:
        st.info("Google entegrasyonu için yönlendiriliyorsunuz...")
        if st.button("Google Hesabı ile Bağlan"):
            st.session_state.authenticated = True
            st.session_state.user_email = "google_user@gmail.com"
            st.rerun()

# --- 3. ANA UYGULAMA DÖNGÜSÜ ---
if not st.session_state.authenticated:
    login_ekrani()
else:
    # --- 4. MODEL HATA ÇÖZÜCÜ (O 404 HATASI İÇİN) ---
    def model_yanit_al(prompt, contents=None):
        try:
            # Önce en yeni sürümü dene
            model = genai.GenerativeModel('gemini-1.5-flash')
            if contents:
                return model.generate_content([prompt] + contents).text
            return model.generate_content(prompt).text
        except Exception:
            try:
                # 404 verirse garanti modele (gemini-pro) geç
                model = genai.GenerativeModel('gemini-pro')
                return model.generate_content(prompt).text
            except Exception as e:
                return f"Model Hatası: {str(e)}"

    # --- 5. KENAR ÇUBUĞU (GOOGLE STİLİ) ---
    with st.sidebar:
        st.markdown(f"👤 **Hesap:** {st.session_state.user_email}")
        if st.button("🚪 Çıkış Yap"):
            st.session_state.authenticated = False
            st.rerun()
        st.markdown("---")
        st.markdown("### 📜 Sohbet Geçmişi")
        st.button("💬 Minecraft Projesi")
        st.button("💬 Python Ödev Yardımı")
        st.markdown("---")
        st.caption("v2.5 Enterprise Edition")

    # --- 6. ANA EKRAN ---
    st.title("🤖 ÖmerGPT Pro")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        st.write("### 📂 Dosya/Görsel")
        up = st.file_uploader("Yükle", type=["pdf", "docx", "png", "jpg"])
        cam = st.camera_input("Kamera")

    # Dosya İşleme (PDF/Word)
    content_list = []
    if up:
        if up.type == "application/pdf":
            reader = pypdf.PdfReader(up)
            text = "".join([p.extract_text() for p in reader.pages])
            content_list.append(f"Belge: {text}")
        elif up.type.startswith("image"):
            content_list.append(Image.open(up))

    # Sohbet
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("Mesajını yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.spinner("ÖmerGPT işliyor..."):
            cevap = model_yanit_al(prompt, content_list if content_list else None)
            with st.chat_message("assistant"): st.markdown(cevap)
            st.session_state.messages.append({"role": "assistant", "content": cevap})