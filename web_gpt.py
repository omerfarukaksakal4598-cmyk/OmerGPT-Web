import streamlit as st
import requests

# --- AYARLAR ---
GROQ_API_KEY = "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" # Buraya yeni anahtarı yaz kanka

st.set_page_config(page_title="ÖmerGPT Ultra", page_icon="🤖")

# Market Reklamı (En Üstte)
st.success("🛒 **Ömer Store:** Diğer tüm projelerimi ve oyunlarımı [BURADAN İNDİR!](https://omer-store.streamlit.app)")

def sohbet_et(mesaj):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        data = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": mesaj}]
        }
        res = requests.post(url, headers=headers, json=data)
        return res.json()['choices'][0]['message']['content']
    except:
        return "🚨 Hata! Anahtarı kontrol et veya sonra dene kanka."

st.title("🚀 ÖmerGPT Ultra Pro")

# Yan Menü (yapayzeka.py'deki gibi hızlı linkler)
with st.sidebar:
    st.header("🔗 Hızlı Linkler")
    st.markdown("[🌐 Google](https://google.com)") #
    st.markdown("[📺 YouTube](https://youtube.com)")
    st.divider()
    st.info("💡 Ömer Store'da yeni projeler var!")

# Chat sistemi
if "msgs" not in st.session_state: st.session_state.msgs = []
for m in st.session_state.msgs:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Sor bakalım..."):
    st.session_state.msgs.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        cevap = sohbet_et(p)
        st.markdown(cevap)
        st.session_state.msgs.append({"role": "assistant", "content": cevap})