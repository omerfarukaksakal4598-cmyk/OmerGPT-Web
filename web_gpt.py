import streamlit as st
import requests
import json
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & YENİ API ---
# Yeni OpenRouter anahtarını buraya tam olarak yerleştirdim knkk
API_KEY = "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"

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. DOSYA OKUMA FONKSİYONLARI ---
def pdf_oku(file):
    try:
        reader = pypdf.PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])
    except: return "PDF okuma hatası."

# --- 3. MODEL YANIT SİSTEMİ ---
def model_yanit_al(prompt, context_text=""):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501", 
            "X-Title": "OmerGPT"
        }
        # En garanti ücretsiz modelleri deniyoruz
        payload = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [
                {"role": "user", "content": f"{context_text}\n\nSoru: {prompt}"}
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if "choices" in res_data:
            return res_data['choices'][0]['message']['content']
        else:
            return f"🚨 Hata Mesajı: {res_data.get('error', {}).get('message', 'Bilinmeyen Hata')}"
            
    except Exception as e:
        return f"🚨 Bağlantı Hatası: {str(e)}"

# --- 4. TASARIM VE GİRİŞ SİSTEMİ ---
if "user" not in st.session_state: st.session_state.user = None
if "messages" not in st.session_state: st.session_state.messages = []

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #131314 !important; border-right: 1px solid #444746; }
    .nav-btn { 
        display: block; width: 100%; padding: 12px; margin: 8px 0; 
        background-color: #1e1f20; color: #8ab4f8 !important; 
        text-align: center; border-radius: 12px; text-decoration: none; 
        border: 1px solid #444746; font-weight: bold; font-size: 14px;
    }
    .nav-btn:hover { background-color: #282a2d; border-color: #8ab4f8; }
</style>
""", unsafe_allow_html=True)

# Üst Bar
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

# --- 5. YAN MENÜ (İSTEDİĞİN TÜM BUTONLAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("🚀 **Hızlı Araçlar**")
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-btn">🌐 Google\'da Ara</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-btn">📺 YouTube\'u Aç</a>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()
    st.caption("v2.9 Ultra - Aktif")

# --- 6. ANA EKRAN & DOSYA ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Bir PDF veya Resim yükle ve analiz et", type=["pdf", "png", "jpg", "jpeg"])
context_text = ""

if up:
    if up.type == "application/pdf":
        context_text = f"Döküman İçeriği: {pdf_oku(up)}"
        st.success("PDF Analize Hazır!")
    elif up.type.startswith("image"):
        st.image(Image.open(up), width=250)
        st.info("Görsel yüklendi. Görsel hakkında soru sorabilirsin.")

# Sohbet Akışı
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka, ne yapalım bugün?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT düşünüyor..."):
        cevap = model_yanit_al(prompt, context_text)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})