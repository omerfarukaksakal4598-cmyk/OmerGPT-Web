import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)
st.set_page_config(page_title="ÖmerGPT Pro", page_icon="🤖", layout="wide")

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
    .chat-history-item { 
        padding: 10px; border-radius: 8px; cursor: pointer; color: #e3e3e3; 
        font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .chat-history-item:hover { background-color: #282a2d; }
    .sidebar-title { color: #e3e3e3; font-family: 'Google Sans', sans-serif; font-weight: 500; padding: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. HAFIZA SİSTEMİ ---
if "all_chats" not in st.session_state: st.session_state.all_chats = {}
if "current_chat_id" not in st.session_state: st.session_state.current_chat_id = "Yeni Sohbet"
if "messages" not in st.session_state: st.session_state.messages = []

# --- 4. MODEL FONKSİYONU ---
def model_yanit_al(prompt, img=None):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content([prompt, img]).text if img else model.generate_content(prompt).text
    except Exception as e: return f"Hata: {str(e)}"

# --- 5. KENAR ÇUBUĞU (GOOGLE DÜZENİ) ---
with st.sidebar:
    st.markdown('<div class="sidebar-title" style="font-size:1.5rem;">🤖 ÖmerGPT</div>', unsafe_allow_html=True)
    
    if st.button("➕ Yeni Sohbet"):
        if st.session_state.messages: # Mevcut sohbeti kaydet
            st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages
        st.session_state.messages = []
        st.session_state.current_chat_id = f"Sohbet {datetime.datetime.now().strftime('%H:%M:%S')}"
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="sidebar-title">📜 Yakın Zamandaki Sohbetler</div>', unsafe_allow_html=True)
    
    # Eski sohbetleri listele
    for chat_id in list(st.session_state.all_chats.keys()):
        if st.button(f"💬 {chat_id}", key=chat_id):
            st.session_state.messages = st.session_state.all_chats[chat_id]
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.markdown("---")
    st.markdown('🌐 [Google](https://google.com) | 📺 [YouTube](https://youtube.com)')

# --- 6. ANA EKRAN ---
st.title(f"🚀 {st.session_state.current_chat_id}")

col1, col2 = st.columns([3, 1])
with col2:
    cam = st.camera_input("Fotoğraf Çek")
    up = st.file_uploader("Dosya Yükle", type=["jpg", "png", "jpeg"])

resim = cam if cam else up
if resim:
    img = Image.open(resim)
    st.image(img, width=250)
    if st.button("🔍 Görseli Analiz Et"):
        st.info(model_yanit_al("Bu fotoğrafta ne var?", img))

# Mesajları Görüntüle
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Giriş Alanı
if prompt := st.chat_input("Mesajını buraya yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("Düşünüyorum..."):
        cevap = model_yanit_al(prompt)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
    
    # Her mesajda otomatik kaydet
    st.session_state.all_chats[st.session_state.current_chat_id] = st.session_state.messages