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

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Sistemin desteklediği modellerden sohbet yeteneği olanı bul
    def get_best_model():
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models:
            raise Exception("Kullanılabilecek model bulunamadı.")
        # İlk uygun modeli döndür
        return genai.GenerativeModel(models[0].name)

    model = get_best_model()
    st.sidebar.success(f"Aktif Model: {model._model_name}")

except Exception as e:
    st.error(f"API Bağlantı Hatası: {e}")
    st.stop()

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "todo" not in st.session_state: st.session_state.todo = []

# --- Sekmeler ---
tab1, tab2, tab3 = st.tabs(["Sohbet & Analiz", "Kod Çalıştırıcı", "Görev Yöneticisi"])

with tab1:
    uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key="file_tab1")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Bir şeyler yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                full_prompt = prompt
                if uploaded_file:
                    content = uploaded_file.read().decode('utf-8')
                    full_prompt = f"Dosya içeriği: {content} \n Soru: {prompt}"
                
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Yanıt alınamadı: {e}")

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