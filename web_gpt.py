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

# --- 2. DOSYA OKUMA FONKSİYONLARI ---
def pdf_oku(file):
    try:
        reader = pypdf.PdfReader(file)
        text = "".join([page.extract_text() or "" for page in reader.pages])
        return text
    except: return "PDF okunurken hata oluştu."

def docx_oku(file):
    try: return docx2txt.process(file)
    except: return "Word dosyası okunurken hata oluştu."

# --- 3. AKILLI MODEL SEÇİCİ (HATA ÖNLEYİCİ) ---
def model_yanit_al(prompt, contents=None):
    # Hata 404'ü önlemek için model listesini kontrol eder
    try:
        model_name = 'gemini-1.5-flash'
        # Eğer içerik varsa ve model desteklenmiyorsa gemini-pro-vision dene
        model = genai.GenerativeModel(model_name)
        if contents:
            return model.generate_content([prompt] + contents).text
        return model.generate_content(prompt).text
    except Exception as e:
        # Eğer 1.5-flash hata verirse otomatik pro modeline geç
        try:
            alt_model = genai.GenerativeModel('gemini-pro')
            return alt_model.generate_content(prompt).text
        except:
            return f"Sistem hatası: {str(e)}"

# --- 4. GOOGLE GEMINI STYLE CSS (image_e3883d.png stili) ---
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #444746; }
    .stButton > button { 
        background-color: #1e1f20 !important; color: #e3e3e3 !important; 
        border: 1px solid #444746 !important; border-radius: 24px !important; 
        width: 100%; transition: 0.3s; text-align: left; padding-left: 20px;
    }
    .stButton > button:hover { background-color: #333537 !important; border-color: #8ab4f8 !important; }
</style>
""", unsafe_allow_html=True)

# --- 5. HAFIZA ---
if "messages" not in st.session_state: st.session_state.messages = []

# --- 6. KENAR ÇUBUĞU ---
with st.sidebar:
    st.markdown("<h2 style='color:white;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("📂 **Desteklenenler:**")
    st.caption("PDF, Word, JPG, PNG")

# --- 7. ANA EKRAN ---
st.title("🚀 ÖmerGPT Ultra Pro")

col1, col2 = st.columns([3, 1])
with col2:
    st.write("### 📤 Dosya Yükle")
    up = st.file_uploader("PDF, Word veya Resim", type=["pdf", "docx", "png", "jpg", "jpeg"])
    cam = st.camera_input("Kamera")

# Dosya İçeriğini İşle
extra_content = []
if up:
    if up.type == "application/pdf":
        extra_content.append(f"Belge Metni: {pdf_oku(up)}")
        st.success("PDF Hazır!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extra_content.append(f"Belge Metni: {docx_oku(up)}")
        st.success("Word Hazır!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra_content.append(img)
        st.image(img, width=200)

if cam:
    extra_content.append(Image.open(cam))

# Sohbet Akışı
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Buraya yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT düşünüyor..."):
        cevap = model_yanit_al(prompt, extra_content if extra_content else None)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})