import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyBH-Kz3JArq8qTPcAx4sVFYLhjdocVk764"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. HATA ÖNLEYİCİ MODEL ÇAĞIRICI ---
def model_yanit_al(prompt, contents=None):
    # Google'ın kabul edebileceği tüm model isim varyasyonlarını sırayla dene
    varyasyonlar = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro', 'models/gemini-pro']
    
    last_error = ""
    for model_adi in varyasyonlar:
        try:
            model = genai.GenerativeModel(model_name=model_adi)
            if contents:
                response = model.generate_content([prompt] + contents)
            else:
                response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = str(e)
            continue # Bu isim çalışmadıysa sonrakine geç
            
    return f"❌ Tüm bağlantı yolları denendi ama sonuç alınamadı. Hata: {last_error}"

# --- 3. TASARIM VE GİRİŞ ---
if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #444746; }
    .nav-btn { 
        display: block; width: 100%; padding: 12px; margin: 8px 0; 
        background-color: #1e1f20; color: #8ab4f8 !important; 
        text-align: center; border-radius: 12px; text-decoration: none; 
        border: 1px solid #444746; font-weight: bold;
    }
    .nav-btn:hover { background-color: #282a2d; border-color: #8ab4f8; }
</style>
""", unsafe_allow_html=True)

# ÜST BAR
c1, c2 = st.columns([5, 1])
with c2:
    if st.session_state.user is None:
        if st.button("🔐 Giriş Yap"): st.session_state.show_login = True
    else:
        st.write(f"👤 {st.session_state.user}")
        if st.button("Çıkış"):
            st.session_state.user = None
            st.rerun()

if st.session_state.get("show_login") and not st.session_state.user:
    with st.expander("Giriş Yap", expanded=True):
        u = st.text_input("Kullanıcı Adı")
        if st.button("Onayla"):
            st.session_state.user = u if u else "ÖmerGPT"
            st.session_state.show_login = False
            st.rerun()

# --- 4. YAN MENÜ (ISTEDIĞIN TÜM ÖZELLİKLER) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("🚀 **Hızlı Linkler**")
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-btn">🌐 Google\'da Ara</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-btn">📺 YouTube\'u Aç</a>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🧹 Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

# --- 5. ANA EKRAN & ANALİZ ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya Analizi", type=["pdf", "docx", "png", "jpg", "jpeg"])
extra = []

if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        extra.append(f"PDF Metni: {''.join([p.extract_text() for p in reader.pages])}")
        st.success("PDF Yüklendi!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extra.append(f"Word Metni: {docx2txt.process(up)}")
        st.success("Word Yüklendi!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra.append(img)
        st.image(img, width=200)

# SOHBET AKIŞI
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT en iyi bağlantıyı arıyor..."):
        cevap = model_yanit_al(prompt, extra if extra else None)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})