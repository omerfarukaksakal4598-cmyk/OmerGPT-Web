import streamlit as st
import google.generativeai as genai
import io
import sys
from contextlib import redirect_stdout

# Sayfa Yapılandırması
st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")
st.title("ÖmerGPT Pro - Kişisel Asistan")

# --- 1. API Ayarları ve Akıllı Model Seçimi ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("HATA: Streamlit Secrets içinde 'GOOGLE_API_KEY' bulunamadı.")
    st.stop()

if "model_name" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not models:
            st.error("Kullanılabilecek model bulunamadı.")
            st.stop()
        st.session_state.model_name = models[0].name
    except Exception as e:
        st.error(f"API Bağlantı Hatası: {e}")
        st.stop()

# --- BUTTON VE MOD KONTROLLERİ İÇİN HAFIZA BAŞLATMA ---
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "normal"  # Varsayılan mod: Normal

if "show_code_runner" not in st.session_state:
    st.session_state.show_code_runner = False  # Kod çalıştırıcı varsayılan olarak kapalı

# Mod Seçimine Göre Yapay Zeka Talimatını Ayarlama
system_prompt = None
if st.session_state.ai_mode == "kod_yazici":
    system_prompt = "Sen uzman bir bilgisayar mühendisi ve yazılımcısın. Kullanıcının isteklerine SADECE temiz, çalışır durumda ve kopyalanabilir kod blokları ile cevap ver. Gereksiz açıklamaları, giriş ve sonuç cümlelerini tamamen çıkar. Sadece kodu ve kod içi çok kısa yorum satırlarını yaz."

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(st.session_state.model_name, system_instruction=system_prompt)

# --- 2. GELİŞMİŞ SOHBET HAFIZASI ---
if "omer_sessions" not in st.session_state:
    st.session_state.omer_sessions = {"sess_1": {"title": "Yeni Sohbet", "messages": []}} 
    st.session_state.current_session = "sess_1" 
    st.session_state.session_counter = 1 

active_session = st.session_state.omer_sessions[st.session_state.current_session]
active_chat = active_session["messages"]

# --- SİDEBAR: Sol Menü Tasarımı ---
with st.sidebar:
    st.header("📜 Sohbet Geçmişi")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.session_counter += 1
        new_sess_id = f"sess_{st.session_state.session_counter}"
        st.session_state.omer_sessions[new_sess_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_session = new_sess_id
        st.rerun()
        
    st.write("---")
    st.subheader("📁 Eski Sohbetler")
    
    for sess_id, sess_data in reversed(list(st.session_state.omer_sessions.items())):
        baslik = sess_data["title"]
        buton_yazisi = f"🟢 {baslik}" if sess_id == st.session_state.current_session else f"💬 {baslik}"
            
        if st.button(buton_yazisi, key=f"btn_{sess_id}", use_container_width=True):
            st.session_state.current_session = sess_id
            st.rerun()
            
    st.write("---")
    
    # İSTEDİĞİN GÜNCELLEME 1: Buton Şeklinde Yapay Zeka Modları
    st.subheader("🤖 Yapay Zeka Modu")
    
    normal_label = "🟢 Normal Mod Aktif" if st.session_state.ai_mode == "normal" else "⚪ Normal Mod"
    kod_yazici_label = "🟢 Kod Yazıcı Aktif" if st.session_state.ai_mode == "kod_yazici" else "💻 Kod Yazıcı Modu"
    
    if st.button(normal_label, use_container_width=True):
        st.session_state.ai_mode = "normal"
        st.rerun()
        
    if st.button(kod_yazici_label, use_container_width=True):
        st.session_state.ai_mode = "kod_yazici"
        st.rerun()
        
    st.write("---")
    
    # Sohbet İndirme Butonu (Eğer mesaj varsa görünür)
    if len(active_chat) > 0:
        chat_download_text = ""
        for message in active_chat:
            sender = "Ömer Faruk" if message["role"] == "user" else "ÖmerGPT"
            chat_download_text += f"[{sender}]: {message['content']}\n\n"
            
        st.download_button(
            label="💾 Bu Sohbeti İndir",
            data=chat_download_text,
            file_name=f"{active_session['title']}.txt",
            mime="text/plain",
            use_container_width=True
        )
        st.write("---")
    
    # İSTEDİĞİN GÜNCELLEME 2: Buton Şeklinde Açılıp Kapanan Kod Çalıştırıcı
    st.subheader("🐍 Python Araçları")
    runner_btn_label = "🔽 Kod Çalıştırıcıyı Kapat" if st.session_state.show_code_runner else "▶️ Kod Çalıştırıcıyı Aç"
    
    if st.button(runner_btn_label, use_container_width=True):
        st.session_state.show_code_runner = not st.session_state.show_code_runner
        st.rerun()
        
    if st.session_state.show_code_runner:
        code = st.text_area("Kod yazın:", "print('ÖmerGPT ile deneme')", height=150, key="sidebar_code")
        if st.button("Kodu Çalıştır", key="btn_sidebar_code", use_container_width=True):
            f = io.StringIO()
            try:
                with redirect_stdout(f):
                    exec(code)
                st.success("Çıktı:")
                st.code(f.getvalue())
            except Exception as e:
                st.error(f"Kod Hatası: {e}")

# =====================================================================
# ANA SOHBET EKRANI
# =====================================================================

# Dosya Yükleyici
uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key=f"file_{st.session_state.current_session}")

# Model Güç Etiketleri Ayarı
m_name = st.session_state.model_name.lower()
if "1.5-pro" in m_name or "2.5-pro" in m_name:
    model_etiketi = "pro+"
elif "flash" in m_name:
    model_etiketi = "pro"
else:
    model_etiketi = "poer"

# Mesaj Geçmişini Göster
for message in active_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("") # Alt boşluk

# Mod ve Model bilgisi chat_input kutusunun içinde dinamik birleşiyor
aktif_mod_tr = "Normal" if st.session_state.ai_mode == "normal" else "Kod Yazıcı"
giris_metni = f"Bir şeyler yaz... [Mod: {aktif_mod_tr}] [Model: {model_etiketi}]"

if prompt := st.chat_input(giris_metni, key="chat_input"):
    
    if len(active_chat) == 0:
        yeni_baslik = prompt if len(prompt) <= 25 else prompt[:25] + "..."
        active_session["title"] = yeni_baslik

    active_chat.append({"role": "user", "content": prompt})
    
    try:
        full_prompt = prompt
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            full_prompt = f"Dosya içeriği: {content} \n Soru: {prompt}"
        
        response = model.generate_content(full_prompt)
        active_chat.append({"role": "assistant", "content": response.text})
    except Exception as e:
        active_chat.append({"role": "assistant", "content": f"Hata oluştu: {e}"})
    
    st.rerun()