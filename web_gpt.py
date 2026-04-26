import streamlit as st
from groq import Groq

# Sayfa Ayarları
st.set_page_config(page_title="ÖmerGPT", page_icon="🤖")

# --- MARKET REKLAMI (Yeni Linkinle Güncellendi) ---
st.success(f"🛒 **Ömer Software Market Açıldı!** Oyunlarımı ve projelerimi indirmek için [BURAYA TIKLA](https://marketpy-akyxsyken6phqmkmj685r2.streamlit.app/)")

st.title("🤖 ÖmerGPT Yapay Zeka")

# API Anahtarı (Senin verdiğin gsk_... anahtarını buraya yapıştır)
client = Groq(api_key="BURAYA_GROQ_API_ANAHTARINI_YAPISTIR")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("ÖmerGPT'ye bir şey sor..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})