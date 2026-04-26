import streamlit as st
import requests

# --- 1. AYARLAR ---
# Kanka buraya Groq'tan aldığın YENİ anahtarı yapıştır
GROQ_API_KEY = "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"

st.set_page_config(page_title="ÖmerGPT Ultra Pro", page_icon="🤖", layout="wide")

# --- 2. ÜST REKLAM BANNER (ÖMER STORE) ---
st.info("🚀 **Ömer Store Yayında!** Turnuva Oyunu, mBlock projeleri ve daha fazlasını indirmek için [Buraya Tıkla!](https://omer-store.streamlit.app)")

# --- 3. YAN MENÜ (ESKİ PROJELERİNİN RUHU) ---
with st.sidebar:
    st.title("🤖 Ömer Platform")
    st.write("Hızlı, ücretsiz ve güçlü.")
    st.markdown("---")
    
    # Hızlı Linkler (yapayzeka.py'deki 'k' komutu gibi)
    st.markdown("🔗 **Hızlı Erişim**")
    st.markdown('[🌐 Google\'da Ara](https://www.google.com)')
    st.markdown('[📺 YouTube\'u Aç](https://www.youtube.com)')
    
    st.markdown("---")
    st.warning("🎮 **Günün Oyunu:** Turnuva Oyunu v1.0")
    if st.button("🛍️ Markete Göz At"):
        st.toast("Ömer Store'a yönlendiriliyorsunuz...")

# --- 4. YAPAY ZEKA FONKSİYONU ---
def model_cevap(mesaj):
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
        data = {
            "model": "llama-3.1-70b-versatile", # En sağlam ücretsiz model
            "messages": [
                {"role": "system", "content": "Sen OmerGPT'sin. Ömer'in kankası gibi davran, samimi ol ama cevapların çok uzun olmasın."},
                {"role": "user", "content": mesaj}
            ]
        }
        res = requests.post(url, headers=headers, json=data)
        return res.json()['choices'][0]['message']['content']
    except:
        return "🚨 Kanka bir sorun çıktı. API anahtarını veya internetini kontrol et!"

# --- 5. SOHBET ARAYÜZÜ ---
st.title("🚀 ÖmerGPT Ultra Pro")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mesajları ekrana bas
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Kullanıcı girişi
if p := st.chat_input("Naber kanka, neyi çözelim?"):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"):
        st.markdown(p)
    
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            yanit = model_cevap(p)
            st.markdown(yanit)
            st.session_state.messages.append({"role": "assistant", "content": yanit})