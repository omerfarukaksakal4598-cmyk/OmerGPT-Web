import streamlit as st
import requests
import json
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & OPENROUTER API ---
OPENROUTER_API_KEY = "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"

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. AKILLI YANIT SİSTEMİ (ENDPOINT HATASI ÇÖZÜCÜ) ---
def model_yanit_al(prompt, context_text=""):
    # OpenRouter'ın kabul ettiği en stabil Gemini isimlerini sırayla dene
    model_listesi = [
        "google/gemini-flash-1.5-8b", 
        "google/gemini-pro-1.5",
        "google/gemini-flash-1.5"
    ]
    
    for model_id in model_listesi:
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8501",
                    "X-Title": "OmerGPT"
                },
                data=json.dumps({
                    "model": model_id,
                    "messages": [
                        {"role": "user", "content": f"{context_text}\n\nSoru: {prompt}"}
                    ]
                })
            )
            
            result = response.json()
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            # Eğer endpoint hatası alırsak döngü devam eder, bir sonraki modeli dener
            continue 
        except:
            continue
            
    return "❌ Hiçbir model yanıt vermedi. Lütfen OpenRouter anahtarını veya internetini kontrol et kanka."

# --- 3. TASARIM VE GİRİŞ SİSTEMİ ---
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
        if st.button("Sistemi Aç"):
            st.session_state.user = u if u else "ÖmerGPT Dostu"
            st.session_state.show_login = False
            st.rerun()

# --- 4. YAN MENÜ (BUTONLAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.write("🔗 **Hızlı Erişim**")
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-btn">🌐 Google</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-btn">📺 YouTube</a>', unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🧹 Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()

# --- 5. ANA EKRAN ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya Yükle", type=["pdf", "docx", "png", "jpg", "jpeg"])
context_text = ""

if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        context_text = f"Döküman Metni: {''.join([p.extract_text() for p in reader.pages])}"
        st.success("PDF Hazır!")
    elif up.type.startswith("image"):
        st.image(Image.open(up), width=200)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Mesajını yaz kanka..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT (OpenRouter) bağlanıyor..."):
        cevap = model_yanit_al(prompt, context_text)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})