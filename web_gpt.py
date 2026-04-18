import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt
import datetime

# --- AYARLAR ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- FONKSİYONLAR ---
def pdf_oku(file):
    text = ""
    reader = pypdf.PdfReader(file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def docx_oku(file):
    return docx2txt.process(file)

def model_yanit_al(prompt, contents):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content([prompt] + contents).text
    except Exception as e: return f"Hata: {str(e)}"

# --- ARYÜZ VE SOHBET ---
if "messages" not in st.session_state: st.session_state.messages = []

with st.sidebar:
    st.title("🤖 ÖmerGPT")
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("📂 **Desteklenenler:** PDF, Word, Fotoğraf")

st.title("🚀 ÖmerGPT Pro Dosya Analizi")

# Dosya ve Kamera
col1, col2 = st.columns([2,1])
with col1:
    up = st.file_uploader("Dosya Seç (PDF, Word veya Fotoğraf)", type=["pdf", "docx", "png", "jpg", "jpeg"])
with col2:
    cam = st.camera_input("Kamera")

content_list = []
if up:
    if up.type == "application/pdf":
        content_list.append(f"PDF Metni: {pdf_oku(up)}")
        st.info("PDF yüklendi!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        content_list.append(f"Word Metni: {docx_oku(up)}")
        st.info("Word dosyası yüklendi!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        content_list.append(img)
        st.image(img, width=200)

if cam:
    content_list.append(Image.open(cam))

# Sohbet Ekranı
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Yüklediğin dosya hakkında bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("İşleniyor..."):
        cevap = model_yanit_al(prompt, content_list)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})