import streamlit as st
import google.generativeai as genai

# Streamlit secrets içinden API anahtarını alıyoruz
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ Hata: API Anahtarı bulunamadı! Lütfen 'Settings > Secrets' kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

# Model ayarları (En kararlı ve hızlı çalışan sürüm)
# gemini-pro veya gemini-1.5-flash modellerinden birini kullanabilirsin.
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="ÖmerGPT", layout="centered")
st.title("ÖmerGPT Sohbet Paneli")

# Sohbet geçmişini tutan yapı
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları ekrana yansıt
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gemini Yanıtı
    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            full_response = response.text
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")