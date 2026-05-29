import streamlit as st
import google.generativeai as genai

# Streamlit secrets içinden anahtarı çeker
# Not: Streamlit Cloud -> Settings -> Secrets kısmına 
# GOOGLE_API_KEY = "AIza..." şeklinde eklemeyi unutma
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API Anahtarı bulunamadı! Lütfen 'Settings > Secrets' kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

# Gemini modelini ayarla (Flash modeli en hızlı ve en verimli olanıdır)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="ÖmerGPT", layout="centered")
st.title("ÖmerGPT Sohbet")

# Sohbet geçmişini sakla
if "messages" not in st.session_state:
    st.session_state.messages = []

# Geçmiş mesajları ekrana yazdır
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcıdan girdi al
if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Yanıtı
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")