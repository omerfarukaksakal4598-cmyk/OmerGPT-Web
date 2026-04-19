import streamlit as st
import requests

# --- 1. AYARLAR & API ---
# Anahtarın buraya tam olarak eklendi knkk
API_KEY = "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"

st.set_page_config(page_title="ÖmerGPT Ultra", page_icon="🤖")

# --- 2. MODEL BAĞLANTISI ---
def sohbet_et(mesaj):
    try:
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "meta-llama/llama-3.1-8b-instruct:free",
            "messages": [{"role": "user", "content": mesaj}]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"🚨 Bağlantı Hatası: {e}"

# --- 3. ARAYÜZ (SOL MENÜ) ---
with st.sidebar:
    st.title("🤖 ÖmerGPT")
    st.markdown("---")
    st.markdown('<a href="https://www.google.com" target="_blank" style="text-decoration:none; color:#8ab4f8; font-weight:bold;">🌐 Google\'da Ara</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://www.youtube.com" target="_blank" style="text-decoration:none; color:#8ab4f8; font-weight:bold;">📺 YouTube\'u Aç</a>', unsafe_allow_html=True)
    if st.button("🧹 Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

# --- 4. SOHBET EKRANI ---
st.title("🚀 ÖmerGPT Ultra Pro")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Naber kanka?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("ÖmerGPT cevap veriyor..."):
        cevap = sohbet_et(prompt)
        with st.chat_message("assistant"):
            st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})