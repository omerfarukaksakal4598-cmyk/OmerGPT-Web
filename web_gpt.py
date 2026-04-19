import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyDH-Kz3JArq8qTPcAx4sVFYLhjdocVk764"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. AKILLI MODEL SEÇİCİ (404 HATASINI KESİN ÇÖZER) ---
def get_working_model():
    try:
        # Senin anahtarının izin verdiği tüm modelleri listele
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Varsa flash'ı seç, yoksa listedeki ilk çalışan modeli al
        for m in available_models:
            if '1.5-flash' in m: return m
        return available_models[0]
    except:
        return 'gemini-pro' # Liste alınamazsa klasik modele dön

def model_yanit_al(prompt, contents=None):
    try:
        active_model_name = get_working_model()
        model = genai.GenerativeModel(model_name=active_model_name)
        if contents:
            response = model.generate_content([prompt] + contents)
        else:
            response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"🚨 Bağlantı Kurulamadı: {str(e)}"

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
    with st.expander("Giriş Paneli", expanded=True):
        u = st.text_input("Kullanıcı Adı")
        if st.button("Sistemi Aç"):
            st.session_state.user = u if u else "Ömer Faruk"
            st.session_state.show_login = False
            st.rerun()

# --- 4. YAN MENÜ (İSTEDİĞİN BUTONLAR) ---
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
    if st.button("🧹 Geçmişi Sil"):
        st.session_state.messages = []
        st.rerun()

# --- 5. ANA EKRAN & DOSYA ANALİZİ ---
st.title("🚀 ÖmerGPT Ultra Pro")

up = st.file_uploader("Dosya/Resim Yükle", type=["pdf", "docx", "png", "jpg", "jpeg"])
extra = []

if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        extra.append(f"PDF İçeriği: {''.join([p.extract_text() for p in reader.pages])}")
        st.success("PDF Analizi Hazır!")
    elif up.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extra.append(f"Word İçeriği: {docx2txt.process(up)}")
        st.success("Word Analizi Hazır!")
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
    
    with st.spinner("ÖmerGPT en uygun modeli seçiyor ve yanıtlıyor..."):
        cevap = model_yanit_al(prompt, extra if extra else None)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})