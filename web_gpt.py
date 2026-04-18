import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import pypdf
import docx2txt

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. GOOGLE GEMINI STYLE CSS ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #444746; }
    .stButton > button { 
        background-color: #1e1f20 !important; color: #e3e3e3 !important; 
        border: 1px solid #444746 !important; border-radius: 24px !important; 
        width: 100%; transition: 0.3s; text-align: left; padding-left: 20px;
    }
    .stButton > button:hover { background-color: #333537 !important; border-color: #8ab4f8 !important; }
    .sidebar-title { color: #e3e3e3; font-family: 'Google Sans', sans-serif; font-weight: 500; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. DOSYA OKUMA FONKSİYONLARI ---
def pdf_oku(file):
    reader = pypdf.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def docx_oku(file):
    return docx2txt.process(file)

# --- 4. HAFIZA SİSTEMİ ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = "Yeni Sohbet"
if "messages" not in st.session_state: st.session_state.messages = []

# --- 5. MODEL FONKSİYONU ---
def model_yanit_al(prompt, content_list=None):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        if content_list:
            return model.generate_content([prompt] + content_list).text
        return model.generate_content(prompt).text
    except Exception as e: return f"Hata: {str(e)}"

# --- 6. KENAR ÇUBUĞU ---
with st.sidebar:
    st.markdown('<div class="sidebar-title" style="font-size:1.5rem;">🤖 ÖmerGPT</div>', unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.session_state.current_chat_id = f"Sohbet {datetime.datetime.now().strftime('%H:%M:%S')}"
        st.rerun()
    st.markdown("---")
    st.markdown('<div class="sidebar-title">📜 Geçmiş Sohbetler</div>', unsafe_allow_html=True)
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {chat_id}", key=chat_id):
            st.session_state.messages = st.session_state.all_chats[chat_id]
            st.session_state.current_chat_id = chat_id
            st.rerun()

# --- 7. ANA EKRAN ---
st.title(f"🚀 {st.session_state.current_chat_id}")

col1, col2 = st.columns([3, 1])
with col2:
    st.write("### 📂 Dosya Analizi")
    up = st.file_uploader("Dosya Yükle (PDF, DOCX, PNG, JPG)", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"])
    cam = st.camera_input("Kamera")

# Dosya İçeriğini Hazırlama
extra_content = []
if up:
    if up.type == "application/pdf":
        text = pdf_oku(up)
        extra_content.append(f"PDF İçeriği: {text}")
        st.success("PDF Okundu!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx_oku(up)
        extra_content.append(f"Word İçeriği: {text}")
        st.success("Word Okundu!")
    elif up.type in ["image/png", "image/jpeg"]:
        img = Image.open(up)
        extra_content.append(img)
        st.image(img, width=200)

if cam:
    img_cam = Image.open(cam)
    extra_content.append(img_cam)

# Sohbet Akışı
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Mesajını veya dosya ile ilgili sorunu yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("İşleniyor..."):
        cevap = model_yanit_al(prompt, extra_content if extra_content else None)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
    st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages