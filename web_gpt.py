import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
import docx2txt

# --- 1. API ANAHTARI VE YAPILANDIRMA ---
# Yeni anahtarını buraya ekledim knkk
API_KEY = "AIzaSyBH-Kz3JArq8qTPcAx4sVFYLhjdocVk764"

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Sistem başlatılamadı: {e}")

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. MODEL BAĞLANTI SİSTEMİ ---
def model_yanit_al(prompt, contents=None):
    # En stabil modelleri sırayla deniyoruz
    modeller = ['gemini-1.5-flash', 'gemini-pro']
    
    for model_adi in modeller:
        try:
            model = genai.GenerativeModel(model_name=model_adi)
            if contents:
                response = model.generate_content([prompt] + contents)
            else:
                response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text
        except Exception as e:
            # Eğer anahtar kesinlikle bozuksa durur
            if "API_KEY_INVALID" in str(e):
                return "❌ API Anahtarı geçersiz! Lütfen anahtarını kontrol et."
            continue
            
    return "❌ Şu an bağlantı kurulamıyor. Lütfen sayfayı yenileyip tekrar dene."

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
        border: 1px solid #444746; font-weight: bold; transition: 0.3s;
    }
    .nav-btn:hover { background-color: #282a2d; border-color: #8ab4f8; transform: scale(1.02); }
    .stButton > button { border-radius: 20px !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. ÜST BAR VE GİRİŞ SİSTEMİ ---
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
    with st.expander("ÖmerGPT Hesabı", expanded=True):
        u_name = st.text_input("Kullanıcı Adı")
        if st.button("Giriş Yap"):
            st.session_state.user = u_name if u_name else "ÖmerGPT Kullanıcısı"
            st.session_state.show_login = False
            st.rerun()

# --- 5. YAN MENÜ (ISTEDIĞIN BUTONLAR) ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:white;'>🤖 ÖmerGPT</h2>", unsafe_allow_html=True)
    
    if st.button("➕ Yeni Sohbet"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.write("🚀 **Hızlı Araçlar**")
    
    # İstediğin Google ve YouTube butonları tam burada
    st.markdown('<a href="https://www.google.com" target="_blank" class="nav-btn">🌐 Google\'da Ara</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" class="nav-btn">📺 YouTube\'u Aç</a>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("🧹 Geçmişi Temizle"):
        st.session_state.messages = []
        st.rerun()
    
    st.caption("v2.9 Pro Edition - Aktif")

# --- 6. ANA EKRAN VE SOHBET ---
st.title("🚀 ÖmerGPT Ultra Pro")

# Dosya Yükleme Alanı
up = st.file_uploader("Bir PDF veya Resim yükle ve analiz et", type=["pdf", "png", "jpg", "jpeg"])
extra_content = []

if up:
    if up.type == "application/pdf":
        reader = pypdf.PdfReader(up)
        text = "".join([p.extract_text() for p in reader.pages])
        extra_content.append(f"Döküman İçeriği: {text}")
        st.success("PDF başarıyla okundu!")
    elif up.type.startswith("image"):
        img = Image.open(up)
        extra_content.append(img)
        st.image(img, width=250, caption="Yüklenen Görsel")

# Mesajları Görüntüle
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Giriş ve Yanıt
if prompt := st.chat_input("Naber kanka, ne yapalım bugün?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.spinner("ÖmerGPT cevap veriyor..."):
        cevap = model_yanit_al(prompt, extra_content if extra_content else None)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})