import streamlit as st
import google.generativeai as genai
import io
import sys
import re
import time
import json
import os
from contextlib import redirect_stdout
from gtts import gTTS
from PIL import Image, ImageEnhance

# Sayfa Yapılandırması
st.set_page_config(page_title="ÖmerGPT Pro", layout="wide")

# --- DOSYA TABANLI KALICI HAFIZA FONKSİYONLARI ---
def save_chats_to_file():
    try:
        data = {
            "omer_sessions": st.session_state.omer_sessions,
            "session_counter": st.session_state.session_counter,
            "current_session": st.session_state.current_session,
            "snippets": st.session_state.snippets
        }
        with open("sohbet_gecmisi.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        pass

def load_chats_from_file():
    if os.path.exists("sohbet_gecmisi.json"):
        try:
            with open("sohbet_gecmisi.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.omer_sessions = data.get("omer_sessions", {"sess_1": {"title": "Yeni Sohbet", "messages": []}})
                st.session_state.session_counter = data.get("session_counter", 1)
                st.session_state.current_session = data.get("current_session", "sess_1")
                st.session_state.snippets = data.get("snippets", [])
                return True
        except:
            return False
    return False

# --- HAFIZA KONTROLLERİNİ BAŞLATMA ---
if "ai_mode" not in st.session_state:
    st.session_state.ai_mode = "normal"

if "model_choice" not in st.session_state:
    st.session_state.model_choice = "flash"

if "show_code_runner" not in st.session_state:
    st.session_state.show_code_runner = False

if "app_theme" not in st.session_state:
    st.session_state.app_theme = "varsayilan"

if "retry_prompt" not in st.session_state:
    st.session_state.retry_prompt = None

if "omer_sessions" not in st.session_state:
    if not load_chats_from_file():
        st.session_state.omer_sessions = {"sess_1": {"title": "Yeni Sohbet", "messages": []}} 
        st.session_state.current_session = "sess_1" 
        st.session_state.session_counter = 1
        st.session_state.snippets = []

if "snippets" not in st.session_state:
    st.session_state.snippets = []

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
    if m and st.session_state.model_choice in m.lower():
        selected_model_name = m
        break
if not selected_model_name and st.session_state.model_list:
    selected_model_name = st.session_state.model_list[0]

system_prompt = None
if st.session_state.ai_mode == "kod_yazici":
    system_prompt = "Sen uzman bir bilgisayar mühendisi ve yazılımcısın. Kullanıcının isteklerine SADECE temiz, çalışır durumda ve kopyalanabilir kod blokları ile cevap ver. Gereksiz açıklamaları tamamen çıkar."

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel(selected_model_name, system_instruction=system_prompt)

active_session = st.session_state.omer_sessions[st.session_state.current_session]
active_chat = active_session["messages"]

trigger_prompt = None
bt = "`" * 3 

# --- SİDEBAR ---
with st.sidebar:
    st.header("📜 Sohbet Geçmişi")
    
    if st.button("➕ Yeni Sohbet Başlat", use_container_width=True):
        st.session_state.session_counter += 1
        new_sess_id = f"sess_{st.session_state.session_counter}"
        st.session_state.omer_sessions[new_sess_id] = {"title": "Yeni Sohbet", "messages": []}
        st.session_state.current_session = new_sess_id
        save_chats_to_file()
        st.rerun()
        
    st.write("---")
    
    st.subheader("📁 Eski Sohbetler")
    search_query = st.text_input("🔍 Sohbetlerde Ara...", key="chat_search")
    
    for sess_id, sess_data in reversed(list(st.session_state.omer_sessions.items())):
        baslik = sess_data["title"]
        if search_query and search_query.lower() not in baslik.lower():
            continue
        buton_yazisi = f"🟢 {baslik}" if sess_id == st.session_state.current_session else f"💬 {baslik}"
        if st.button(buton_yazisi, key=f"btn_{sess_id}", use_container_width=True):
            st.session_state.current_session = sess_id
            save_chats_to_file()
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

    # --- YENİ: 1. İnternet Arama Anahtarı ---
    st.subheader("🌐 Canlı Ağ Bağlantısı")
    use_web_search = st.checkbox("Canlı İnternet Aramasını Aktif Et", value=False, help="Güncel haberler, yeni güncellemeler veya dosya aramaları için Google'ı kullanır.")

    st.write("---")

    st.subheader("💾 Favori Kod Deposu")
    with st.expander("➕ Yeni Kod Parçası Ekle"):
        snip_title = st.text_input("Kod Başlığı:", key="new_snip_title")
        snip_content = st.text_area("Kod Bloğu:", key="new_snip_code", height=100)
        if st.button("Depoya Kaydet", use_container_width=True):
            if snip_title and snip_content:
                st.session_state.snippets.append({"title": snip_title, "code": snip_content})
                save_chats_to_file()
                st.success("Kod kaydedildi!")
                st.rerun()

    if st.session_state.snippets:
        for idx, snip in enumerate(st.session_state.snippets):
            with st.expander(f"📋 {snip['title']}"):
                st.code(snip['code'], language="python")
                if st.button("🗑️ Sil", key=f"del_snip_{idx}", use_container_width=True):
                    st.session_state.snippets.pop(idx)
                    save_chats_to_file()
                    st.rerun()

    st.write("---")
    
    if len(active_chat) > 0:
        chat_download_text = ""
        for message in active_chat:
            sender = "Ömer Faruk" if message["role"] == "user" else "ÖmerGPT"
            chat_download_text += f"[{sender}]: {message['content']}\n\n"
            
        st.download_button("💾 Sohbeti İndir", chat_download_text, f"{active_session['title']}.txt", "text/plain", use_container_width=True)
        if st.button("🗑️ Sohbeti Sil", use_container_width=True):
            if len(st.session_state.omer_sessions) > 1:
                del st.session_state.omer_sessions[st.session_state.current_session]
                st.session_state.current_session = list(st.session_state.omer_sessions.keys())[0]
            else:
                st.session_state.omer_sessions[st.session_state.current_session] = {"title": "Yeni Sohbet", "messages": []}
            save_chats_to_file()
            st.rerun()
            
        st.write("---")
    
    st.subheader("🐍 Python Araçları")
    runner_btn_label = "🔽 Çalıştırıcı Kapat" if st.session_state.show_code_runner else "▶️ Çalıştırıcı Aç"
    
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
# ANA EKRAN VE YENİ GİRİŞ SİSTEMLERİ
# =====================================================================

# --- YENİ: 3. Link Analiz Sistemi Eklendi ---
tab_upload, tab_camera, tab_link = st.tabs(["📁 Dosya/Resim Yükle", "📸 Canlı Kamera", "🔗 Web Linki Oku"])

with tab_upload:
    uploaded_file = st.file_uploader("Metin veya resim seç:", type=['txt', 'png', 'jpg', 'jpeg'], key=f"file_{st.session_state.current_session}")

with tab_camera:
    camera_file = st.camera_input("Kameraya göster:")
    brightness_val = st.slider("☀️ Karanlık Ortam Ayarı (Pozlama)", 1.0, 3.0, 1.3, step=0.1)

with tab_link:
    url_input = st.text_input("🔗 İnceletmek istediğin web sitesinin linkini buraya yapıştır:")

model_etiketi = "pro+" if st.session_state.model_choice == "pro" else "pro"

for message in active_chat:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.write("") 

# --- YENİ: 2. Minecraft Dedektifi Şablonu (4 Butonlu Düzen) ---
st.write("🎯 **Hızlı Şablonlar:**")
template_cols = st.columns(4)
with template_cols[0]:
    if st.button("🐛 Hatayı Düzelt", use_container_width=True):
        trigger_prompt = f"Aşağıdaki kodda yer alan hataları düzeltir misin?\n{bt}python\n# Kodu buraya yapıştır\n{bt}"
with template_cols[1]:
    if st.button("🐍 Python Projesi", use_container_width=True):
        trigger_prompt = "CustomTkinter ile yapabileceğim eğlenceli bir Python GUI proje fikri verir misin?"
with template_cols[2]:
    if st.button("📝 Ödev Özeti", use_container_width=True):
        trigger_prompt = "Aşağıdaki konuyu, tamamen doğal ve 6. sınıf düzeyine uygun, anlaşılır bir dille özetler misin?"
with template_cols[3]:
    if st.button("🧱 MC Crash Çöz", use_container_width=True):
        trigger_prompt = f"Aşağıdaki Minecraft 1.12.2 crash-report logunu inceleyip hangi modların çakıştığını (VanillaFix vb.) bulur musun? Çözümü anlayabileceğim basitlikte anlat:\n{bt}text\n# Logu buraya yapıştır\n{bt}"

if active_chat and active_chat[-1]["role"] == "assistant":
    st.write("---")
    last_msg_content = active_chat[-1]["content"]
    pattern_py = bt + "python(.*?)" + bt
    pattern_all = bt + "(.*?)" + bt
    
    code_blocks = re.findall(pattern_py, last_msg_content, re.DOTALL)
    if not code_blocks:
        code_blocks = re.findall(pattern_all, last_msg_content, re.DOTALL)
        
    extracted_code = "\n\n".join(code_blocks).strip() if code_blocks else None

    if extracted_code:
        action_cols = st.columns(2)
        with action_cols[0]:
            if st.button("🔊 Son Cevabı Seslendir", use_container_width=True):
                try:
                    clean_text_to_speak = last_msg_content.replace(f"{bt}python", "").replace(bt, "")
                    tts = gTTS(text=clean_text_to_speak, lang='tr')
                    sound_buffer = io.BytesIO()
                    tts.write_to_fp(sound_buffer)
                    sound_buffer.seek(0)
                    st.audio(sound_buffer, format='audio/mp3', autoplay=True)
                except Exception as e:
                    st.error(f"Seslendirme Hatası: {e}")
        with action_cols[1]:
            st.download_button("📥 Kodu .py Olarak İndir", extracted_code, "kod_projesi.py", "text/x-python", use_container_width=True)
    else:
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

if prompt or trigger_prompt or st.session_state.retry_prompt:
    if st.session_state.retry_prompt:
        final_prompt = st.session_state.retry_prompt
        st.session_state.retry_prompt = None
    else:
        final_prompt = prompt if prompt else trigger_prompt
    
    if len(active_chat) == 0:
        yeni_baslik = final_prompt if len(final_prompt) <= 25 else final_prompt[:25] + "..."
        active_session["title"] = yeni_baslik

    active_chat.append({"role": "user", "content": final_prompt})
    
    try:
        payload = None
        # İçerik Birleştirici
        if camera_file:
            img = Image.open(camera_file)
            if brightness_val != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(brightness_val)
            payload = [final_prompt, img]
        elif uploaded_file:
            if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                img = Image.open(uploaded_file)
                payload = [final_prompt, img]
            else:
                content = uploaded_file.read().decode('utf-8', errors='ignore')
                full_prompt = f"Dosya içeriği: {content} \n\n Soru: {final_prompt}"
                payload = full_prompt
        elif url_input:
            # Kullanıcı link girmişse sorunun içine web adresini göm
            payload = f"Aşağıdaki linkte bulunan içeriği incele ve sorumu buna göre yanıtla: {url_input}\n\nSoru: {final_prompt}"
        else:
            payload = final_prompt
        
        # İnternet Araması Aktif mi?
        kwargs = {}
        if use_web_search:
            kwargs["tools"] = "google_search_retrieval"
            
        response = model.generate_content(payload, **kwargs)
        active_chat.append({"role": "assistant", "content": response.text})
        save_chats_to_file() 
        
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "ResourceExhausted" in err_msg or "quota" in err_msg.lower():
            st.error("⚠️ Kullanım hakkın bitti! 1.5 saniye sonra diğer modele otomatik geçiliyor...")
            if active_chat and active_chat[-1]["role"] == "user":
                active_chat.pop()
            st.session_state.retry_prompt = final_prompt
            if st.session_state.model_choice == "pro":
                st.session_state.model_choice = "flash"
            else:
                st.session_state.model_choice = "pro"
            save_chats_to_file()
            time.sleep(1.5)
            st.rerun()
        else:
            active_chat.append({"role": "assistant", "content": f"Hata oluştu: {e}"})
            save_chats_to_file()
    
    st.rerun()