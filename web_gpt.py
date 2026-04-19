import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & YENİ API ---
API_KEY = "AIzaSyBH-Kz3JArq8qTPcAx4sVFYLhjdocVk764"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. DOSYA OKUMA FONKSİYONLARI ---
def pdf_oku(file):
    try:
        reader = pypdf.PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])
    except: return "PDF okuma hatası."

def docx_oku(file):
    try: return docx2txt.process(file)
    except: return "Word okuma hatası."

# --- 3. MODEL YANIT SİSTEMİ ---
def model_yanit_al(prompt, contents=None):
    try:
        # En güncel flash modelini kullanıyoruz
        model = genai.GenerativeModel('gemini-1.5-flash')
        if contents:
            return model.generate_content([prompt] + contents).text
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Bağlantı hatası oluştu: {str(e)}"

# --- 4. TASARIM (CSS) ---
if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #444746; }
    .nav-btn { 
        display: block; width: 100%; padding: 12px; margin: 8px 0; 
        background-color: #1e1f20; color: #8ab4f8 !important; 
        text-align: center; border-radius: 12px; text-decoration: none; 
        border: 1px solid #444746; font-weight: bold; transition: 0.2s;
    }
    .nav-btn:hover { background-color: #282a2d; border-color: #8ab4f8; }
    .stButton > button { border-radius: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. ÜST BAR & GİRİŞ SİSTEMİ ---
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
        u_name = st.text_input("Kullanıcı Adı")
        if st.button("Onayla"):
            st.session_state.user = u_name if u_name else "ÖmerGPT Kullanıcısı"
            st.session_state.show_login = False
            st.rerun()

# --- 6. YAN MENÜ (ISTEDIĞIN TÜM BUTONLAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("🚀 **Hızlı Araçlar**")
    
    # Google ve YouTube butonların burada kanka
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-btn">🌐 Google\'da Ara</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-btn">📺 YouTube\'u Aç</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    
    st.caption("v2.9 Pro - Kesintisiz Erişim")

# --- 7. ANA EKRAN & DOSYA İŞLEME ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya Analizi (PDF, Word, Resim)", type=["pdf", "docx", "png", "jpg", "jpeg"])
extra_content = []

if up:
    if up.type == "application/pdf":
        text = pdf_oku(up)
        extra_content.append(f"PDF İçeriği: {text}")
        st.success("PDF Hazır!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx_oku(up)
        extra_content.append(f"Word İçeriği: {text}")
        st.success("Word Dosyası Hazır!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra_content.append(img)
        st.image(img, width=200)

# Sohbet Akışı
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT düşünüyor..."):
        cevap = model_yanit_al(prompt, extra_content if extra_content else None)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})