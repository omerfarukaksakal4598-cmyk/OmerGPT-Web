import streamlit as st

st.set_page_config(page_title="Ömer Store", page_icon="🚀", layout="wide")

st.title("🛡️ Ömer Software Market")
st.markdown("Kendi geliştirdiğim tüm yazılım ve oyun projeleri tek bir yerde!")

# --- BÖLÜM 1: OYUNLAR ---
st.header("🎮 Oyunlar ve Eğlence")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Ömer'in Turnuva Oyunu")
    st.write("Özel ses efektleri ve turnuva kayıt sistemiyle tam sürüm.")
    st.link_button("Oyunu İndir (ZIP)", "https://github.com/KULLANICI_ADIN/REPO/raw/main/Omer_Game.zip")

# --- BÖLÜM 2: MBLOCK & SCRATCH ---
st.header("🧩 Blok Kodlama Projeleri")
c1, c2, c3 = st.columns(3)

with c1:
    st.write("📊 mBlocky")
    st.link_button("Dosyayı İndir", "https://github.com/KULLANICI_ADIN/REPO/raw/main/mblocky.mblock")
with c2:
    st.write("🚀 ÖMERf Proje")
    st.link_button("Dosyayı İndir", "https://github.com/KULLANICI_ADIN/REPO/raw/main/ÖMERf.mblock")
with c3:
    st.write("🎮 Scratch Oyunu")
    st.link_button("sb3 İndir", "https://github.com/KULLANICI_ADIN/REPO/raw/main/mblocky%20-%20Kopya.sb3")

# --- BÖLÜM 3: PYTHON KODLARI ---
st.header("🐍 Python Yazılımları")
p1, p2 = st.columns(2)

with p1:
    st.subheader("ÖmerGPT Klasik")
    st.write("Kamera ve sesli yanıt özellikli masaüstü sürümü.")
    st.link_button("Kodu Görüntüle", "https://github.com/KULLANICI_ADIN/REPO/raw/main/yapayzeka.py")
with p2:
    st.subheader("Akıllı Chatbot")
    st.write("Hesaplama yapabilen arayüzlü chatbot.")
    st.link_button("Kodu Görüntüle", "https://github.com/KULLANICI_ADIN/REPO/raw/main/chatbot_gui.py")