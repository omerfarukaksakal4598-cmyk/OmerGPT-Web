import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & API (KONTROL NOKTASI) ---
# Eğer hata devam ederse yeni bir API Key alıp buraya yapıştırman gerekebilir.
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"API Yapılandırma Hatası: {e}")

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. AKILLI MODEL BAĞLANTI SİSTEMİ ---
def model_yanit_al(prompt, contents=None):
    # En stabil çalışan modelleri sırayla zorla
    modeller = ['gemini-1.5-flash', 'gemini-pro']
    
    for model_adi in modeller:
        try:
            model = genai.GenerativeModel(model_name=model_adi)
            # Zaman aşımı (timeout) riskine karşı basit bir çağrı
            if contents:
                response = model.generate_content([prompt] + contents)
            else:
                response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text
        except Exception as e:
            error_msg = str(e)
            # Eğer API Key hatasıysa direkt kullanıcıya söyle
            if "API_KEY_INVALID" in error_msg or "403" in error_msg:
                return "❌ HATA: API Anahtarın geçersiz veya süresi dolmuş. Lütfen Google AI Studio'dan yeni bir anahtar al."
            continue # Diğer modeli dene
            
    return "❌ Bağlantı kurulamadı. İnternetini kontrol et veya 1 dakika sonra tekrar dene."

# --- 3. ARAYÜZ AYARLARI ---
if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; }
    .nav-link { color: #8ab4f8 !important; text-decoration: none; display: block; padding: 10px; border-radius: 10px; }
    .nav-link:hover { background-color: #282a2d; }
</style>
""", unsafe_allow_html=True)

# --- 4. ÜST BAR & GİRİŞ ---
c_t1, c_t2 = st.columns([5, 1])
with c_t2:
    if st.session_state.user is None:
        if st.button("🔐 Giriş Yap"): st.session_state.show_login = True
    else:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Çıkış"):
            st.session_state.user = None
            st.rerun()

if st.session_state.get("show_login", False):
    with st.expander("Giriş Yap", expanded=True):
        u = st.text_input("Kullanıcı Adı")
        if st.button("Sisteme Gir"):
            st.session_state.user = u if u else "ÖmerGPT Dostu"
            st.session_state.show_login = False
            st.rerun()

# --- 5. YAN MENÜ ---
with st.sidebar:
    st.title("🤖 ÖmerGPT")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("🔗 **Hızlı Erişim**")
    st.markdown('<a href="https://google.com" target="_blank" class="nav-link">🌐 Google</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://youtube.com" target="_blank" class="nav-link">📺 YouTube</a>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🧹 Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

# --- 6. ANA EKRAN ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya/Resim Seç", type=["pdf", "png", "jpg", "jpeg"])
extra = []
if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        txt = "".join([p.extract_text() for p in reader.pages])
        extra.append(f"Döküman Metni: {txt}")
        st.success("PDF Analize Hazır!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra.append(img)
        st.image(img, width=200)

# Sohbet Görüntüleme
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Bağlantı kuruluyor..."):
        yanit = model_yanit_al(prompt, extra if extra else None)
        with st.chat_message("assistant"): st.markdown(yanit)
        st.session_state.messages.append({"role": "assistant", "content": yanit})