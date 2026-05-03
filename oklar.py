import streamlit as st
import random

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Ömer Ok Temizleme - Labirent", page_icon="🎯")

# --- OYUN HAFIZASI ---
if 'level' not in st.session_state:
    st.session_state.level = 1
    st.session_state.puan = 0

YONLER = {"yukari": "↑", "asagi": "↓", "sol": "←", "sag": "→"}

if st.session_state.level <= 3:
    GRID_BOYUTU = 3
else:
    GRID_BOYUTU = 4

def ok_uctu_mu(tahta, r, c):
    yon = tahta[r][c]
    if yon is None: return False
    if yon == "yukari":
        for i in range(r - 1, -1, -1):
            if tahta[i][c] is not None: return False
    elif yon == "asagi":
        for i in range(r + 1, GRID_BOYUTU):
            if tahta[i][c] is not None: return False
    elif yon == "sol":
        for j in range(c - 1, -1, -1):
            if tahta[r][j] is not None: return False
    elif yon == "sag":
        for j in range(c + 1, GRID_BOYUTU):
            if tahta[r][j] is not None: return False
    return True

def hamle_var_mi(tahta):
    for r in range(GRID_BOYUTU):
        for c in range(GRID_BOYUTU):
            if tahta[r][c] is not None and ok_uctu_mu(tahta, r, c):
                return True
    return False

def yeni_tahta_olustur():
    while True:
        yeni = [[random.choice(list(YONLER.keys())) for _ in range(GRID_BOYUTU)] for _ in range(GRID_BOYUTU)]
        if hamle_var_mi(yeni): return yeni

if 'tahta' not in st.session_state:
    st.session_state.tahta = yeni_tahta_olustur()

# --- TASARIM (FOTODAKİ LABİRENT STİLİ) ---
st.markdown("""
    <style>
    /* Arka planı bembeyaz yap */
    .stApp {
        background-color: white;
    }
    /* Butonları labirent duvarı gibi yap */
    div.stButton > button {
        font-size: 40px !important;
        color: #1a1a2e !important;
        background-color: white !important;
        border: 5px solid #1a1a2e !important; /* Kalın siyah duvarlar */
        height: 100px !important;
        width: 100% !important;
        border-radius: 0px !important; /* Köşeleri keskin yap (Fotoğraftaki gibi) */
        transition: 0.3s;
    }
    /* Üzerine gelince fotoğraftaki gibi koyulaşsın */
    div.stButton > button:hover {
        background-color: #1a1a2e !important;
        color: white !important;
    }
    /* Boşlukları labirent yolu gibi göster */
    .ok-yolu {
        height: 100px;
        border: 1px solid #eeeeee;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- EKRAN ---
st.markdown(f"<h1 style='text-align: center; color: #1a1a2e;'>🎯 LABİRENT: BÖLÜM {st.session_state.level}</h1>", unsafe_allow_html=True)

ok_sayisi = sum(row.count(x) for row in st.session_state.tahta for x in YONLER.keys() if x is not None)

if ok_sayisi == 0:
    st.success("LABİRENT TEMİZLENDİ!")
    if st.button("SONRAKİ BÖLÜM ➔"):
        st.session_state.level += 1
        st.session_state.tahta = yeni_tahta_olustur()
        st.rerun()
else:
    # Izgarayı çiz
    for r in range(GRID_BOYUTU):
        cols = st.columns(GRID_BOYUTU)
        for c in range(GRID_BOYUTU):
            yon = st.session_state.tahta[r][c]
            if yon:
                if cols[c].button(YONLER[yon], key=f"lab-{r}-{c}-{st.session_state.level}"):
                    if ok_uctu_mu(st.session_state.tahta, r, c):
                        st.session_state.tahta[r][c] = None
                        st.session_state.puan += 10
                        st.rerun()
                    else:
                        st.toast("Duvara çarptın!", icon="🧱")
            else:
                cols[c].markdown("<div class='ok-yolu'> </div>", unsafe_allow_html=True)

st.write(f"**Skor:** {st.session_state.puan}")