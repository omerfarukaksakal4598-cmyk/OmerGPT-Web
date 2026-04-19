import streamlit as st
import requests

# YENİ ANAHTARIN BURADA KALSIN
API_KEY = "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"

st.set_page_config(page_title="ÖmerGPT Ultra", page_icon="🤖")

def mesaj_gonder(text):
    try:
        res = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={
                "model": "meta-llama/llama-3.1-8b-instruct:free",
                "messages": [{"role": "user", "content": text}]
            }
        )
        data = res.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"🚨 Hata: {data.get('error', {}).get('message', 'Bilinmeyen hata')}"
    except Exception as e:
        return f"🚨 Bağlantı koptu: {e}"

# --- ARAYÜZ ---
st.title("🚀 ÖmerGPT Ultra Pro")

# Yan Menü (Senin istediğin linkler)
with st.sidebar:
    st.header("🤖 Menü")
    st.markdown('[🌐 Google\'da Ara](https://www.google.com)')
    st.markdown('[📺 YouTube\'u Aç](https://www.youtube.com)')
    if st.button("🧹 Temizle"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Yaz bakalım kanka..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.spinner("..."):
        cevap = mesaj_gonder(p)
        with st.chat_message("assistant"): st.markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})