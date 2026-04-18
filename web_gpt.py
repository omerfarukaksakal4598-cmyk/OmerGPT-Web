import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. AYARLAR & API ---
API_KEY = "AIzaSyDH0RWc4G2mU4ImwWx748GFd-oC80bJl3g"
genai.configure(api_key=API_KEY)

# Sayfa Genişletme ve Başlık
st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. GOOGLE TARZI ÖZEL CSS (image_8.png'den esinlenildi) ---
st.markdown("""
<style>
    /* Ana Kenar Çubuğu Arka Planı */
    [data-testid="stSidebar"] {
        background-color: #1a1b1e !important; /* Çok Koyu Gri/Siyah */
        color: #e3e3e3 !important;
        border-right: 1px solid #3c4043;
    }

    /* Menü Başlıkları (Öğelerim, Not Defterleri vb.) */
    .st-emotion-cache-10o5uor {
        color: #e3e3e3 !important;
        font-family: 'Google Sans', Roboto, Arial, sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.1rem !important;
        opacity: 0.9;
    }

    /* Buton Tarzı (Sohbeti Sıfırla) */
    div.stButton > button {
        background-color: transparent !important;
        color: #e3e3e3 !important;
        border: 1px solid #5f6368 !important;
        border-radius: 20px !important; /* Oval köşeler */
        padding: 8px 20px !important;
        font-family: 'Google Sans', Roboto, sans-serif !important;
        transition: background-color 0.3s, border-color 0.3s;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #303134 !important;
        border-color: #8ab4f8 !important; /* Google Mavisi hover */
    }

    /* Link Tarzı (Google, YouTube) */
    .stMarkdown a {
        color: #8ab4f8 !important; /* Açık Mavi Linkler */
        text-decoration: none !important;
        font-family: 'Google Sans', Roboto, sans-serif !important;
        font-weight: 400;
        opacity: 0.9;
    }
    .stMarkdown a:hover {
        text-decoration: underline !important;
        opacity: 1;
    }
    
    /* Simge ve Yazı Hizalama */
    .side-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. MODEL VE FONKSİYONLAR ---
# (Önceki hatasız model fonksiyonlarını koruyoruz)
def en_uygun_modeli_bul(gorsel_mi=False):
    try:
        modeller = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if gorsel_mi:
            for m in modeller:
                if 'gemini-1.5-flash' in m: return m
                if 'vision' in m: return m
        else:
            for m in modeller:
                if 'gemini-1.5-flash' in m: return m
                if 'gemini-pro' in m and 'vision' not in m: return m
        return modeller[0]
    except:
        return 'gemini-pro'

def model_yanit_al(prompt, img=None):
    try:
        model_adi = en_uygun_modeli_bul(gorsel_mi=True if img else False)
        model = genai.GenerativeModel(model_adi)
        if img:
            res = model.generate_content([prompt, img])
        else:
            res = model.generate_content(prompt)
        return res.text
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 4. YAN MENÜ (image_8.png Düzeni) ---
with st.sidebar:
    # Google Tarzı Menü Başlığı
    st.markdown('<div class="side-item"><span style="font-size:1.5rem;">🛠️</span> <span style="font-size:1.2rem; font-weight:500;">Menü</span></div>', unsafe_allow_html=True)
    st.markdown("---") # Ayırıcı Çizgi

    # Buton Bölümü (Sohbeti Sıfırla)
    st.markdown("### Kontroller")
    if st.button("🧹 Sohbeti Sıfırla"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")

    # Linkler Bölümü (image_8.png'deki "Öğelerim" düzeni gibi)
    st.markdown("### Hızlı Linkler")
    
    # Google Linki (Simge + Yazı)
    st.markdown(f"""
    <div class="side-item">
        <img src="https://www.google.com/images/branding/product/ico/googleg_lodp.ico" width="20">
        <a href="https://google.com" target="_blank">Google'ı Aç</a>
    </div>
    """, unsafe_allow_html=True)

    # YouTube Linki (Simge + Yazı)
    st.markdown(f"""
    <div class="side-item">
        <img src="https://www.youtube.com/s/desktop/28b67e7a/img/favicon_32x32.png" width="20">
        <a href="https://youtube.com" target="_blank">YouTube'u Aç</a>
    </div>
    """, unsafe_allow_html=True)

# --- 5. ANA İÇERİK (Metin ve Görsel Analiz) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🤖 ÖmerGPT Ultra Pro")
st.write("Google arayüzlü, tam özellikli yapay zeka.")

# (Ana içerik kısmı öncekiyle aynı kalıyor, sadece görsel analizi buraya koyuyoruz)
st.write("### 📸 Görsel Analiz")
col1, col2 = st.columns(2)
with col1:
    up = st.file_uploader("Fotoğraf Yükle", type=["jpg", "png", "jpeg"])
with col2:
    cam = st.camera_input("Fotoğraf Çek")

secilen_resim = cam if cam else up

if secilen_resim:
    img = Image.open(secilen_resim)
    st.image(img, width=300)
    soru = st.text_input("Görsel hakkında sorun:", value="Bu fotoğrafta ne görüyorsun? Tahmin et.")
    if st.button("🤖 Görseli Analiz Et"):
        with st.spinner("ÖmerGPT bakıyor..."):
            cevap = model_yanit_al(soru, img)
            st.success(f"ÖmerGPT: {cevap}")

st.markdown("---")

# Sohbet Bölümü
st.write("### 💬 Sohbet")
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("Düşünüyorum..."):
        cevap = model_yanit_al(prompt)
        with st.chat_message("assistant"):
            st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})