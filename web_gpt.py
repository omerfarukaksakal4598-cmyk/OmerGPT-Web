import streamlit as st
import google.generativeai as genai
import io
import sys
from contextlib import redirect_stdout

# 1. API Ayarları
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"API Hatası: {e}")
    st.stop()

st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")
st.title("ÖmerGPT Pro - Kişisel Asistan")

# Session State
if "messages" not in st.session_state: st.session_state.messages = []
if "todo" not in st.session_state: st.session_state.todo = []

# Sekmeler
tab1, tab2, tab3 = st.tabs(["Sohbet & Analiz", "Kod Çalıştırıcı", "Görev Yöneticisi"])

with tab1:
    # Key değerini benzersiz ve uzun tuttuk
    uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key="unique_file_uploader_tab1")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Bir şeyler yaz..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            full_prompt = prompt
            if uploaded_file:
                content = uploaded_file.read().decode('utf-8')
                full_prompt = f"Dosya içeriği: {content} \n Soru: {prompt}"
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

with tab2:
    st.subheader("Python Kod Çalıştırıcı")
    # Kod alanına da key verdik ki çakışma olmasın
    code = st.text_area("Buraya kod yazın:", "print('ÖmerGPT ile kod denemesi')", height=200, key="code_input_area")
    
    if st.button("Kodu Çalıştır", key="run_code_button"):
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
    gorev = st.text_input("Yapılacak bir iş ekle:", key="todo_input")
    if st.button("Ekle", key="add_todo_button"):
        if gorev: st.session_state.todo.append(gorev)
    for i, item in enumerate(st.session_state.todo):
        st.write(f"✅ {i+1}. {item}")