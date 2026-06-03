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

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(st.session_state.model_name)

# --- 2. GELİŞMİŞ HAFIZA: Çakışmayı Önleyen Yeni Hafıza Alanı ---
if "omer_sessions" not in st.session_state:
    # Anahtar adını 'omer_sessions' yaptık ki eski liste verileriyle çakışmasın
    st.session_state.omer_sessions = {"sess_1": {"title": "Yeni Sohbet", "messages": []}} 
    st.session_state.current_session = "sess_1" 
    st.session_state.session_counter = 1 
if "todo" not in st.session_state: 
    st.session_state.todo = []

# --- SİDEBAR: Akıllı Sohbet Geçmişi ---
with st.sidebar:
    st.header("📜 Sohbet Geçmişi")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_counter += 1
        new_sess_id = f"sess_{st.session_state.session_counter}"
        st.session_state.omer_sessions[new_sess_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_session = new_sess_id
        st.rerun()
        
    st.write("---")
    st.subheader("📁 Eski Sohbetler")
    
    for sess_id, sess_data in reversed(list(st.session_state.omer_sessions.items())):
        baslik = sess_data["title"]
        buton_yazisi = f"🟢 {baslik}" if sess_id == st.session_state.current_session else f"💬 {baslik}"
            
        if st.button(buton_yazisi, key=f"btn_{sess_id}", use_container_width=True):
            st.session_state.current_session = sess_id
            st.rerun()

# =====================================================================
# ANA EKRAN TASARIMI
# =====================================================================

# --- ÜST BÖLÜM: SOHBETİN ÜSTÜNDEKİ ARAÇLAR ---
col1, col2 = st.columns(2)

with col1:
    with st.expander("🐍 Python Kod Çalıştırıcı", expanded=False):
        code = st.text_area("Kod yazın:", "print('ÖmerGPT ile deneme')", height=150, key="code_tab2")
        if st.button("Kodu Çalıştır", key="btn_tab2"):
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    exec(code)
                st.success("Çıktı:")
                st.code(f.getvalue())
            except Exception as e:
                st.error(f"Kod Hatası: {e}")

with col2:
    with st.expander("✅ Görev Yöneticisi", expanded=False):
        gorev = st.text_input("Yapılacak bir iş ekle:", key="input_tab3")
        if st.button("Ekle", key="btn_add_tab3"):
            if gorev: st.session_state.todo.append(gorev)
        for i, item in enumerate(st.session_state.todo):
            st.write(f"✅ {i+1}. {item}")

st.divider() # Ayrım Çizgisi

# --- ALT BÖLÜM: SOHBET ALANI ---
uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key=f"file_{st.session_state.current_session}")

# Model Güç Etiketleri Ayarı
m_name = st.session_state.model_name.lower()
if "1.5-pro" in m_name or "2.5-pro" in m_name:
    model_etiketi = "pro+"
elif "flash" in m_name:
    model_etiketi = "pro"
else:
    model_etiketi = "poer"

# Aktif Model Bilgisi Giriş Kutusunun Üstünde Duruyor
st.caption(f"⚡ **Aktif Model:** `{model_etiketi}`")

active_session = st.session_state.omer_sessions[st.session_state.current_session]
active_chat = active_session["messages"]

# Mesaj Geçmişini Göster
for message in active_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("") # Boşluk

# Soru Sorma Girişi (Her Zaman En Altta Sabit kalır)
if prompt := st.chat_input("Bir şeyler yaz...", key="chat_input"):
    
    # Eğer ilk mesajsa sohbetin adını konuya göre değiştir
    if len(active_chat) == 0:
        yeni_baslik = prompt if len(prompt) <= 25 else prompt[:25] + "..."
        active_session["title"] = yeni_baslik

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