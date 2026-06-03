import streamlit as st
import google.generativeai as genai
import io
import sys
import re  # Kod bloklarını ayıklamak için gerekli kütüphane
from contextlib import redirect_stdout
from gtts import gTTS

# Sayfa Yapılandırması
st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")

# --- HAFIZA KONTROLLERİNİ BAŞLATMA ---
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "normal"

if "model_choice" not in st.session_state:
    st.session_state.model_choice = "flash"

if "show_code_runner" not in st.session_state:
    st.session_state.show_code_runner = False

if "snippets" not in st.session_state:
    st.session_state.snippets = []

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "varsayilan"

# --- Kusursuz Nokta Atışı Temalar ---
def apply_theme(theme_name):
    if theme_name == "matrix":
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] {
                background-color: #050505 !important;
            }
            h1, h2, h3, h4, h5, h6, .stMarkdown p, label, .stCaption {
                color: #00ff66 !important;
                font-family: 'Consolas', monospace !important;
            }
            .stButton>button {
                background-color: #0a140a !important;
                color: #00ff66 !important;
                border: 1px solid #00ff66 !important;
                font-family: 'Consolas', monospace !important;
            }
            .stButton>button:hover {
                background-color: #00ff66 !important;
                color: #050505 !important;
            }
            </style>
        """, unsafe_allow_html=True)
    elif theme_name == "cyberpunk":
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"] {
                background-color: #0b0c10 !important;
            }
            h1, h2, h3, h4, h5, h6, .stMarkdown p, label, .stCaption {
                color: #00f0ff !important;
                font-family: 'Segoe UI', sans-serif !important;
            }
            .stButton>button {
                background-color: #1f2833 !important;
                color: #ff007f !important;
                border: 1px solid #ff007f !important;
                box-shadow: 0 0 5px #ff007f;
            }
            .stButton>button:hover {
                background-color: #ff007f !important;
                color: #ffffff !important;
            }
            </style>
        """, unsafe_allow_html=True)
    elif theme_name == "vscode":
        st.markdown("""
            <style>
            [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
                background-color: #1e1e1e !important;
            }
            [data-testid="stSidebar"] {
                background-color: #252526 !important;
            }
            h1, h2, h3, h4, h5, h6, .stMarkdown p, label, .stCaption {
                color: #d4d4d4 !important;
            }
            .stButton>button {
                background-color: #333333 !important;
                color: #007acc !important;
                border: 1px solid #3e3e3e !important;
            }
            .stButton>button:hover {
                background-color: #007acc !important;
                color: #ffffff !important;
            }
            </style>
        """, unsafe_allow_html=True)

apply_theme(st.session_state.app_theme)

st.title("ÖmerGPT Pro - Kişisel Asistan")

# --- API Ayarları ve Akıllı Model Seçimi ---
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("HATA: Streamlit Secrets içinde 'GOOGLE_API_KEY' bulunamadı.")
    st.stop()

if "model_list" not in st.session_state:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        st.session_state.model_list = models
    except Exception as e:
        st.error(f"API Bağlantı Hatası: {e}")
        st.stop()

selected_model_name = None
for m in st.session_state.model_list:
    if st.session_state.model_choice in m.lower():
        selected_model_name = m
        break
if not selected_model_name and st.session_state.model_list:
    selected_model_name = st.session_state.model_list[0]

system_prompt = None
if st.session_state.ai_mode == "kod_yazici":
    system_prompt = "Sen uzman bir bilgisayar mühendisi ve yazılımcısın. Kullanıcının isteklerine SADECE temiz, çalışır durumda ve kopyalanabilir kod blokları ile cevap ver. Gereksiz açıklamaları tamamen çıkar. Sadece kodu ve kod içi çok kısa yorum satırlarını yaz."

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(selected_model_name, system_instruction=system_prompt)

# --- SOHBET HAFIZASI ---
if "omer_sessions" not in st.session_state:
    st.session_state.omer_sessions = {"sess_1": {"title": "Yeni Sohbet", "messages": []}} 
    st.session_state.current_session = "sess_1" 
    st.session_state.session_counter = 1 

active_session = st.session_state.omer_sessions[st.session_state.current_session]
active_chat = active_session["messages"]

trigger_prompt = None

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

    st.subheader("⚡ Model Seçici")
    flash_btn_label = "🚀 Gemini Flash Aktif" if st.session_state.model_choice == "flash" else "⚡ Gemini Flash (Hızlı)"
    pro_btn_label = "🧠 Gemini Pro Aktif" if st.session_state.model_choice == "pro" else "💪 Gemini Pro (Güçlü)"

    if st.button(flash_btn_label, use_container_width=True):
        st.session_state.model_choice = "flash"
        st.rerun()
    if st.button(pro_btn_label, use_container_width=True):
        st.session_state.model_choice = "pro"
        st.rerun()

    st.write("---")

    st.subheader("🎨 Arayüz Teması")
    t_cols = st.columns(2)
    with t_cols[0]:
        if st.button("⚪ Standart", use_container_width=True):
            st.session_state.app_theme = "varsayilan"
            st.rerun()
        if st.button("🟣 Siberpunk", use_container_width=True):
            st.session_state.app_theme = "cyberpunk"
            st.rerun()
    with t_cols[1]:
        if st.button("🟢 Matrix", use_container_width=True):
            st.session_state.app_theme = "matrix"
            st.rerun()
        if st.button("🔵 VS Code", use_container_width=True):
            st.session_state.app_theme = "vscode"
            st.rerun()

    st.write("---")

    # Favori Kod Deposu
    st.subheader("💾 Favori Kod Deposu")
    with st.expander("➕ Yeni Kod Parçası Ekle"):
        snip_title = st.text_input("Kod Başlığı:", key="new_snip_title")
        snip_content = st.text_area("Kod Bloğu:", key="new_snip_code", height=100)
        if st.button("Depoya Kaydet", use_container_width=True):
            if snip_title and snip_content:
                st.session_state.snippets.append({"title": snip_title, "code": snip_content})
                st.success("Kod kaydedildi!")
                st.rerun()

    if st.session_state.snippets:
        for idx, snip in enumerate(st.session_state.snippets):
            with st.expander(f"📋 {snip['title']}"):
                st.code(snip['code'], language="python")
                if st.button("🗑️ Sil", key=f"del_snip_{idx}", use_container_width=True):
                    st.session_state.snippets.pop(idx)
                    st.rerun()

    st.write("---")
    
    # İndirme ve Silme Araçları
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
        
        if st.button("🗑️ Bu Sohbeti Sil", use_container_width=True):
            if len(st.session_state.omer_sessions) > 1:
                del st.session_state.omer_sessions[st.session_state.current_session]
                st.session_state.current_session = list(st.session_state.omer_sessions.keys())[0]
            else:
                st.session_state.omer_sessions[st.session_state.current_session] = {"title": "Yeni Sohbet", "messages": []}
            st.rerun()
            
        st.write("---")
    
    # Kod Çalıştırıcı Butonu
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

    # Küçük Yazılarla İstatistik Paneli
    st.write("---")
    total_msg = len(active_chat)
    user_msg = len([m for m in active_chat if m["role"] == "user"])
    assistant_msg = total_msg - user_msg
    total_words = sum(len(m["content"].split()) for m in active_chat if m["role"] == "assistant")

    st.caption("📊 **Sohbet İstatistikleri**")
    st.caption(f"• Toplam Mesaj: {total_msg}")
    st.caption(f"• Gönderilen Soru: {user_msg}")
    st.caption(f"• Alınan Cevap: {assistant_msg}")
    st.caption(f"• Üretilen Kelime: {total_words}")

# =====================================================================
# ANA SOHBET EKRANI
# =====================================================================

uploaded_file = st.file_uploader("Dosya Analizi için PDF/Metin yükle", type=['pdf', 'txt'], key=f"file_{st.session_state.current_session}")

model_etiketi = "pro+" if st.session_state.model_choice == "pro" else "pro"

for message in active_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("") 

# Hızlı Şablon Butonları
st.write("🎯 **Hızlı Şablonlar:**")
template_cols = st.columns(3)
with template_cols[0]:
    if st.button("🐛 Hatayı Düzelt", use_container_width=True):
        trigger_prompt = "Aşağıdaki kod bloğunda yer alan hataları bulup düzeltebilir misin?\n```python\n# Kodunu buraya yapıştır\n```"
with template_cols[1]:
    if st.button("🐍 Yeni Python Projesi", use_container_width=True):
        trigger_prompt = "CustomTkinter kütüphanesini kullanarak yapabileceğim eğlenceli ve kendimi geliştirebileceğim bir Python GUI proje fikri verir misin?"
with template_cols[2]:
    if st.button("📝 Ödev Özeti Çıkar", use_container_width=True):
        trigger_prompt = "İstediğim bir okul konusunu öğretmenlerimin yapay zeka olduğunu anlamayacağı, tamamen doğal ve 6. sınıf düzeyine uygun bir dille özetler misin?"

# --- ÖZELLİK 2 GÜNCELLEME: Seslendirme ve Dinamik .py Dosyası İndirme Paneli ---
if active_chat and active_chat[-1]["role"] == "assistant":
    st.write("---")
    
    # Son mesajın içindeki kod bloklarını düzenli ifadelerle tespit etme
    last_msg_content = active_chat[-1]["content"]
    code_blocks = re.findall(r"```python(.*?)
```", last_msg_content, re.DOTALL)
    if not code_blocks:
        code_blocks = re.findall(r"```(.*?)```", last_msg_content, re.DOTALL)
        
    extracted_code = "\n\n".join(code_blocks).strip() if code_blocks else None

    # Eğer kod tespit edildiyse butonları yan yana (2 sütun) göster
    if extracted_code:
        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("🔊 Son Cevabı Seslendir", use_container_width=True):
                try:
                    clean_text_to_speak = last_msg_content.replace("```python", "").replace("
```", "")
                    tts = gTTS(text=clean_text_to_speak, lang='tr')
                    sound_buffer = io.BytesIO()
                    tts.write_to_fp(sound_buffer)
                    sound_buffer.seek(0)
                    st.audio(sound_buffer, format='audio/mp3', autoplay=True)
                except Exception as e:
                    st.error(f"Seslendirme Hatası: {e}")
        with action_cols[1]:
            st.download_button(
                label="📥 Üretilen Kodu .py Olarak İndir",
                data=extracted_code,
                file_name="kod_projesi.py",
                mime="text/x-python",
                use_container_width=True
            )
    else:
        # Eğer kod bloğu yoksa sadece tek bir geniş Seslendirme butonu göster
        if st.button("🔊 Son Cevabı Seslendir", use_container_width=True):
            try:
                tts = gTTS(text=last_msg_content, lang='tr')
                sound_buffer = io.BytesIO()
                tts.write_to_fp(sound_buffer)
                sound_buffer.seek(0)
                st.audio(sound_buffer, format='audio/mp3', autoplay=True)
            except Exception as e:
                st.error(f"Seslendirme Hatası: {e}")

mod_isimleri = {"normal": "Normal", "kod_yazici": "Kod Yazıcı"}
aktif_mod_tr = mod_isimleri.get(st.session_state.ai_mode, "Normal")
giris_metni = f"Bir şeyler yaz... [Mod: {aktif_mod_tr}] [Model: {model_etiketi}]"

prompt = st.chat_input(giris_metni, key="chat_input")

if prompt or trigger_prompt:
    final_prompt = prompt if prompt else trigger_prompt
    
    if len(active_chat) == 0:
        yeni_baslik = final_prompt if len(final_prompt) <= 25 else final_prompt[:25] + "..."
        active_session["title"] = yeni_baslik

    active_chat.append({"role": "user", "content": final_prompt})
    
    try:
        full_prompt = final_prompt
        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            full_prompt = f"Dosya içeriği: {content} \n Soru: {final_prompt}"
        
        response = model.generate_content(full_prompt)
        active_chat.append({"role": "assistant", "content": response.text})
    except Exception as e:
        active_chat.append({"role": "assistant", "content": f"Hata oluştu: {e}"})
    
    st.rerun()