import streamlit as st
import google.generativeai as genai

# 1. API Anahtarını al
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("API Anahtarı bulunamadı! Lütfen Secrets kısmına GOOGLE_API_KEY ekleyin.")
    st.stop()

# 2. HATA ÖNLEYİCİ: Kullanılabilir modelleri otomatik bul
def get_best_model():
    # Mevcut tüm modelleri listele ve 'gemini' ile başlayan en uygun olanı seç
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods and 'gemini' in m.name:
            return m.name
    return 'gemini-1.5-flash' # Bulamazsa varsayılanı dene

model_name = get_best_model()
model = genai.GenerativeModel(model_name)

st.set_page_config(page_title="ÖmerGPT", layout="centered")
st.title(f"ÖmerGPT ({model_name} ile çalışıyor)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Mesajınızı yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = model.generate_content(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Sistem Hatası: {e}")