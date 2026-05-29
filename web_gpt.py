import streamlit as st
import google.generativeai as genai
from io import StringIO
import sys

# 1. API Ayarları
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("API Anahtarı bulunamadı!")
    st.stop()

st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")
st.title("ÖmerGPT Pro - Kişisel Asistan")

# Sekmeler
tab1, tab2, tab3 = st.tabs(["Sohbet & Analiz", "Kod Çalıştırıcı", "Görev Yöneticisi"])

# Sohbet geçmişini sakla
if "messages" not in st.session_state:
    st.session_state.messages = []
if "todo" not in st.session_state:
    st.session_state.todo = []

with tab1:
    # Dosya Yükleme (Özellik 1)
    uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'])
    
    # Eski mesajları göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Yeni mesaj girişi
    if prompt := st.chat_input("Bir şeyler yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            full_prompt = prompt
            if uploaded_file:
                # Basit metin dosyası okuma
                content = uploaded_file.read().decode('utf-8')
                full_prompt = f"Dosya içeriği: {content} \n Soru: {prompt}"
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

with tab2:
    st.subheader("Python Kod Çalıştırıcı (Özellik 5)")
    code = st.text_area("Buraya kod yazın:", "print('ÖmerGPT ile kod denemesi')")
    if st.button("Kodu Çalıştır"):
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()
        try:
            exec(code)
            sys.stdout = old_stdout
            st.code(mystdout.getvalue())
        except Exception as e:
            sys.stdout = old_stdout
            st.error(f"Hata: {e}")

with tab3:
    st.subheader("Görev Yöneticisi (Özellik 6)")
    gorev = st.text_input("Yapılacak bir iş ekle:")
    if st.button("Ekle"):
        st.session_state.todo.append(gorev)
    for i, item in enumerate(st.session_state.todo):
        st.write(f"✅ {i+1}. {item}")