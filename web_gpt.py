import streamlit as st
import google.generativeai as genai
import io
import sys
import time
from contextlib import redirect_stdout

# Sayfa Yapılandırması
st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")
st.title("ÖmerGPT Pro - Kişisel Asistan")

# --- 1. API Ayarları ve Akıllı Model Seçimi ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("HATA: Streamlit Secrets içinde 'GOOGLE_API_KEY' bulunamadı.")
    st.stop()

# Model ismini hafızada tutalım
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

# Aktif modeli bağla
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(st.session_state.model_name)

# Session State Tanımlamaları
if "messages" not in st.session_state: st.session_state.messages = []
if "todo" not in st.session_state: st.session_state.todo = []

# --- SİDEBAR: Sol Menüye Eski Sohbet Geçmişi Eklendi ---
with st.sidebar:
    st.header("📜 Sohbet Odası")
    
    # Yeni Sohbet Başlatma Butonu
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    st.subheader("💬 Son Soruların")
    
    # Kullanıcının sorduğu soruları geçmiş olarak listele
    user_prompts = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    if user_prompts:
        for p in reversed(user_prompts[-10:]):  # Son 10 soruyu tersten gösterir
            kisa_soru = p if len(p) <= 25 else p[:25] + "..."
            st.text(f"• {kisa_soru}")
    else:
        st.caption("Henüz soru sorulmadı. Yazdıkça geçmiş burada birikecek.")

# --- Sekmeler ---
tab1, tab2, tab3 = st.tabs(["Sohbet & Analiz", "Kod Çalıştırıcı", "Görev Yöneticisi"])

with tab1:
    # Dosya Yükleyici
    uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key="file_tab1")
    
    # Eski mesajları ekrana bas
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    st.write("") # Küçük boşluk
    # AKTİF MODEL: İstediğin gibi tam soru sorma yerinin hemen üzerinde duruyor
    st.caption(f"⚡ **Aktif Model:** `{st.session_state.model_name}`")

    # Soru Sorma Girişi (st.rerun sayesinde artık asla yukarıda kalmaz)
    if prompt := st.chat_input("Bir şeyler yaz...", key="chat_input"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        try:
            full_prompt = prompt
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                full_prompt = f"Dosya içeriği: {content} \n Soru: {prompt}"
            
            response = model.generate_content(full_prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"Hata oluştu: {e}"})
        
        # Sayfayı anında yenileyerek kutuyu en alta kilitler!
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