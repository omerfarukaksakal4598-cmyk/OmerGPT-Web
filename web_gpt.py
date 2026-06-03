import streamlit as st
import google.generativeai as genai
import io
import sys
from contextlib import redirect_stdout

# Sayfa Yapılandırması
st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")
st.title("ÖmerGPT Pro - Kişisel Asistan")

# --- 1. API Ayarları ve Akıllı Model Seçimi ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("HATA: Streamlit Secrets içinde 'GOOGLE_API_KEY' bulunamadı.")
    st.stop()

# Model ismini hafızada tut
if "model_name" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models:
            st.error("Kullanılabilecek model bulunamadı.")
            st.stop()
        st.session_state.model_name = models[0].name
    except Exception as e:
        st.error(f"API Bağlantı Hatası: {e}")
        st.stop()

# Modeli bağla
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(st.session_state.model_name)

# --- 2. GELİŞMİŞ HAFIZA: Sohbet Odaları ---
if "sessions" not in st.session_state:
    st.session_state.sessions = {"Sohbet 1": []} # Tüm sohbetleri tutan sözlük
    st.session_state.current_session = "Sohbet 1" # Şu an aktif olan sohbet
    st.session_state.session_counter = 1 # Sohbet numaralandırıcısı
if "todo" not in st.session_state: 
    st.session_state.todo = []

# --- SİDEBAR: Gerçek Sohbet Geçmişi Yönetimi ---
with st.sidebar:
    st.header("📜 Sohbet Geçmişi")
    
    # Yeni Sohbet Açma
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.session_counter += 1
        new_session_name = f"Sohbet {st.session_state.session_counter}"
        st.session_state.sessions[new_session_name] = []
        st.session_state.current_session = new_session_name
        st.rerun()
        
    st.write("---")
    st.subheader("📁 Eski Sohbetler")
    
    # Eski sohbetleri buton olarak listele (En yenisi en üstte)
    for session_name in reversed(list(st.session_state.sessions.keys())):
        # Eğer buton aktif sohbetse farklı bir ikon/yazı gösterebiliriz
        if session_name == st.session_state.current_session:
            buton_yazisi = f"🟢 {session_name} (Aktif)"
        else:
            buton_yazisi = f"💬 {session_name}"
            
        # Butona tıklandığında o sohbete geçiş yap
        if st.button(buton_yazisi, key=f"btn_{session_name}", use_container_width=True):
            st.session_state.current_session = session_name
            st.rerun()

# --- Ana Ekran Sekmeleri ---
tab1, tab2, tab3 = st.tabs(["Sohbet & Analiz", "Kod Çalıştırıcı", "Görev Yöneticisi"])

with tab1:
    # Dosya Yükleyici
    uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key=f"file_{st.session_state.current_session}")
    
    # AKTİF SOHBETİN mesajlarını çek ve ekrana bas
    active_chat = st.session_state.sessions[st.session_state.current_session]
    
    for message in active_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.write("")
    st.caption(f"⚡ **Aktif Model:** `{st.session_state.model_name}` | **Oda:** `{st.session_state.current_session}`")

    # Soru Sorma Girişi
    if prompt := st.chat_input("Bir şeyler yaz...", key="chat_input"):
        # Mesajı aktif sohbete kaydet
        active_chat.append({"role": "user", "content": prompt})
        
        try:
            full_prompt = prompt
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                full_prompt = f"Dosya içeriği: {content} \n Soru: {prompt}"
            
            response = model.generate_content(full_prompt)
            active_chat.append({"role": "assistant", "content": response.text})
        except Exception as e:
            active_chat.append({"role": "assistant", "content": f"Hata oluştu: {e}"})
        
        st.rerun()

with tab2:
    st.subheader("Python Kod Çalıştırıcı")
    code = st.text_area("Kod yazın:", "print('ÖmerGPT ile deneme')", height=200, key="code_tab2")
    if st.button("Kodu Çalıştır", key="btn_tab2"):
        f = io.StringIO()
        try:
            with redirect_stdout(f):
                exec(code)
            st.success("Çıktı:")
            st.code(f.getvalue())
        except Exception as e:
            st.error(f"Kod Hatası: {e}")

with tab3:
    st.subheader("Görev Yöneticisi")
    gorev = st.text_input("Yapılacak bir iş ekle:", key="input_tab3")
    if st.button("Ekle", key="btn_add_tab3"):
        if gorev: st.session_state.todo.append(gorev)
    for i, item in enumerate(st.session_state.todo):
        st.write(f"✅ {i+1}. {item}")