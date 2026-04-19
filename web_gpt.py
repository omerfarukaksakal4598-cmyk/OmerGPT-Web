import streamlit as st
import requests
import json
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & OPENROUTER API ---
# Yeni OpenRouter anahtarını buraya ekledim kanka
OPENROUTER_API_KEY = "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"

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. OPENROUTER YANIT FONKSİYONU ---
def model_yanit_al(prompt, context_text=""):
    try:
        # OpenRouter üzerinden Gemini 1.5 Flash modelini çağırıyoruz
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemini-flash-1.5", # En hızlı ve stabil model
                "messages": [
                    {"role": "user", "content": f"{context_text}\n\nSoru: {prompt}"}
                ]
            })
        )
        
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        else:
            return f"🚨 API Hatası: {result.get('error', {}).get('message', 'Bilinmeyen hata')}"
    except Exception as e:
        return f"🚨 Bağlantı Hatası: {str(e)}"

# --- 3. TASARIM (CSS) ---
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

# --- 4. ÜST BAR & GİRİŞ ---
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
    with st.expander("Hesap Girişi", expanded=True):
        u = st.text_input("Kullanıcı Adı")
        if st.button("Sistemi Başlat"):
            st.session_state.user = u if u else "Ömer"
            st.session_state.show_login = False
            st.rerun()

# --- 5. YAN MENÜ (ISTEDIĞIN TÜM BUTONLAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("🔗 **Hızlı Erişim**")
    # İstediğin linkler burada kanka
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-btn">🌐 Google</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-btn">📺 YouTube</a>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🧹 Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

# --- 6. ANA EKRAN & DOSYA ANALİZİ ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya Analizi (PDF, Word, Resim)", type=["pdf", "docx", "png", "jpg", "jpeg"])
context_text = ""

if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        context_text = f"Döküman İçeriği: {''.join([p.extract_text() for p in reader.pages])}"
        st.success("PDF Analize Hazır!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        context_text = f"Word İçeriği: {docx2txt.process(up)}"
        st.success("Word Analize Hazır!")
    elif up.type.startswith("image"):
        st.warning("Not: OpenRouter üzerinden görsel analizi için model ayarı gerekebilir, şu an metin desteği aktif.")

# SOHBET AKIŞI
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT (OpenRouter) yanıtlıyor..."):
        cevap = model_yanit_al(prompt, context_text)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})