import streamlit as st
import numpy as np
from PIL import Image
import cv2

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="ChromAId - Color Assistent",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 1:1 EXAKTES DESIGN MIT ISHIHARA-PUNKT-HINTERGRUND ---
st.markdown("""
<style>
    /* Exakter Hintergrund mit querverstreuten Rot-Grün-Gelb-Blauen Ishihara-Punkten nach Vorlage */
    .stApp {
        background-color: #0d1b2a;
        background-image: 
            radial-gradient(#e63946 14px, transparent 15px),
            radial-gradient(#2a9d8f 10px, transparent 11px),
            radial-gradient(#e9c46a 8px, transparent 9px),
            radial-gradient(#52b788 16px, transparent 17px),
            radial-gradient(#e76f51 12px, transparent 13px),
            radial-gradient(#a8dadc 14px, transparent 15px),
            radial-gradient(#f4a261 9px, transparent 10px),
            radial-gradient(#457b9d 20px, transparent 21px),
            radial-gradient(#e0533c 11px, transparent 12px),
            radial-gradient(#8ab17d 15px, transparent 16px);
        background-size: 220px 220px, 160px 160px, 130px 130px, 260px 260px, 190px 190px, 230px 230px, 170px 170px, 310px 310px, 140px 140px, 200px 200px;
        background-position: 0 0, 35px 55px, 85px 25px, 125px 145px, 55px 185px, 165px 85px, 205px 45px, 105px 225px, 15px 115px, 90px 150px;
        background-attachment: fixed;
        color: #e0e1dd;
    }
    
    /* Der charakteristische Pinselstrich-Banner für Überschriften */
    .brush-banner {
        background: #f8f9fa;
        color: #1b263b;
        padding: 18px 25px;
        border-radius: 18px;
        text-align: center;
        font-weight: 900;
        font-size: 2.2rem;
        letter-spacing: 1.5px;
        margin: 10px auto 30px auto;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border: 4px solid #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-transform: uppercase;
    }
    
    /* Startkarten im originalen Mint-Ton (wie in Skizze 2) */
    .sketch-card {
        background-color: #e0f1ed;
        color: #0d1b2a;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        margin-bottom: 25px;
        border: 3px solid #2a9d8f;
    }
    .sketch-card h3 {
        color: #0d1b2a;
        font-weight: 800;
        font-size: 1.4rem;
        margin-bottom: 10px;
    }
    .sketch-card p {
        color: #1b263b;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    /* Weißer Container für Ishihara-Testbilder (garantiert perfekte Sichtbarkeit) */
    .image-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        display: inline-block;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        margin: 15px auto;
        border: 4px solid #ffffff;
    }
    
    /* Streamlit Buttons an das Design anpassen */
    .stButton>button {
        width: 100%;
        border-radius: 14px;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1rem;
        background-color: #3b82f6;
        color: white;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
    }
    
    /* Ergebnis- und Info-Boxen */
    .result-box {
        padding: 22px;
        border-radius: 16px;
        background-color: #1b263b;
        border-left: 8px solid #2a9d8f;
        font-size: 1.1rem;
        margin-top: 20px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.3);
        color: #e0e1dd;
        border: 1px solid #415a77;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALISIERUNG ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "test_step" not in st.session_state:
    st.session_state.test_step = 0
if "test_answers" not in st.session_state:
    st.session_state.test_answers = []

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- FARBSIMULATIONS- & ANALYSE-ALGORITHMEN ---
def simulate_color_blindness(image_np, deficiency_type):
    img_f = image_np.astype(np.float32) / 255.0
    if deficiency_type == 'protanopia':
        matrix = np.array([[0.56667, 0.43333, 0.0], [0.55833, 0.44167, 0.0], [0.0, 0.24167, 0.75833]])
    elif deficiency_type == 'deuteranopia':
        matrix = np.array([[0.625, 0.375, 0.0], [0.7, 0.3, 0.0], [0.0, 0.3, 0.7]])
    else:
        matrix = np.array([[0.95, 0.05, 0.0], [0.0, 0.43333, 0.56667], [0.0, 0.475, 0.525]])
    simulated = np.dot(img_f, matrix.T)
    return np.clip(simulated * 255.0, 0, 255).astype(np.uint8)

def get_dominant_colors(image_pil, k=4):
    img_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    img_cv = cv2.resize(img_cv, (150, 150))
    pixels = np.float32(img_cv.reshape((-1, 3)))
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    counts = np.bincount(labels.flatten())
    sorted_indices = np.argsort(counts)[::-1]
    
    dominant = []
    for idx in sorted_indices:
        b, g, r = centers[idx]
        hex_val = f"#{r:02x}{g:02x}{b:02x}"
        dominant.append({"rgb": (int(r), int(g), int(b)), "hex": hex_val})
    return dominant

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/chameleon.png", width=70) # Chamäleon-Logo[cite: 1]
    st.markdown("### **ChromAId Navigation**")
    if st.button("🏠 Startseite"):
        navigate_to("home")
    if st.button("👁️ Farbtest (Screening)"):
        navigate_to("test")
    if st.button("🔬 Alltagshilfe & KI"):
        navigate_to("assistant")
    
    st.markdown("---")
    st.markdown("### Info")
    st.info("Barrierefreie Farbunterstützung & Screening nach Designvorgabe.")

# ==========================================
# 1. SEITE: HOME (STARTSEITE)[cite: 2]
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="brush-banner">COLOR ASSISTENT</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sketch-card">
        <h3>👁️ FARBTEST MACHEN</h3>
        <p>Analysieren Sie Ihre Farbwahrnehmung und erhalten Sie strukturierte Ergebnisse.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Starten", key="btn_home_test"):
        st.session_state.test_step = 0
        st.session_state.test_answers = []
        navigate_to("test")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="sketch-card">
        <h3>📸 ALLTAGS-FARB KI-ANALYSE</h3>
        <p>Ein Bild hochladen und KI Farben & Zustände (z. B. Ampeln) bestimmen lassen[cite: 4].</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Bild hochladen", key="btn_home_assistant"):
        navigate_to("assistant")

# ==========================================
# 2. SEITE: MODUL B - FARBTEST[cite: 3]
# ==========================================
elif st.session_state.page == "test":
    st.markdown('<div class="brush-banner">FARBTEST</div>', unsafe_allow_html=True)
    
    test_questions = [
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Ishihara_9.png/300px-Ishihara_9.png",
            "question": "Welche Zahl oder Form erkennen Sie in diesem Punktmuster?",
            "options": ["5", "6", "7", "Keine Zahl erkennbar"],
            "correct": "7"
        },
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Ishihara_1.png/300px-Ishihara_1.png",
            "question": "Welche Zahl sehen Sie auf dieser Testtafel?",
            "options": ["12", "74", "3", "Keine Zahl erkennbar"],
            "correct": "12"
        },
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/Ishihara_3.png/300px-Ishihara_3.png",
            "question": "Welche Zahl ist hier versteckt?",
            "options": ["6", "29", "45", "Keine Zahl erkennbar"],
            "correct": "6"
        }
    ]
    
    step = st.session_state.test_step
    
    if step < len(test_questions):
        q = test_questions[step]
        st.write(f"**Frage {step + 1} von {len(test_questions)}**")
        
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="image-card">
                <img src="{q['img']}" width="250" style="border-radius: 12px;" />
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### {q['question']}")
        selected_option = st.radio("Bitte wählen Sie Ihre Option:", q["options"], key=f"q_opt_{step}")
        
        if st.button("Nächste Frage ➔"):
            st.session_state.test_answers.append(selected_option)
            st.session_state.test_step += 1
            st.rerun()
    else:
        st.markdown("### 📊 Testergebnis & Auswertung")
        st.success("Der Farbtest wurde erfolgreich abgeschlossen!")
        
        correct_count = sum(1 for i, ans in enumerate(st.session_state.test_answers) if ans == test_questions[i]["correct"])
        
        if correct_count == len(test_questions):
            st.info("Ergebnis-Tendenz: **Unauffälliges Farbsehen**.")
        else:
            st.warning("Ergebnis-Tendenz: **Mögliche Rot-Grün-Schwäche** erkannt.")
            
        st.markdown("""
        <div class="result-box">
            <b>Medizinischer Hinweis:</b> Dieses Screening dient der ersten Orientierung und ersetzt keine professionelle augenärztliche Diagnose.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Test wiederholen"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            st.rerun()

# ==========================================
# 3. SEITE: MODUL A - ALLTAGSHILFE[cite: 4]
# ==========================================
elif st.session_state.page == "assistant":
    st.markdown('<div class="brush-banner">ALLTAGSHILFE</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto von Ampeln, Kabeln oder Lebensmitteln hoch, um Farbwerte zu prüfen und Seh-Simulationen zu starten[cite: 4].")
    
    uploaded_file = st.file_uploader("Foto auswählen (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(image)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Originalbild")
            st.image(image, use_container_width=True)
            
        with col2:
            st.subheader("Farb-Simulation")
            sim_mode = st.selectbox("Seh-Typ wählen:", ["Protanopie (Rotblind)", "Deuteranopia (Grünblind)", "Tritanopia (Blaublind)"])
            mode_key = "protanopia" if "Protanopie" in sim_mode else ("deuteranopia" if "Deuteranopia" in sim_mode else "tritanopia")
            
            simulated_np = simulate_color_blindness(img_np, mode_key)
            st.image(simulated_np, use_container_width=True)
            
        st.markdown("---")
        st.subheader("🎨 Dominante Farbwerte (Hex & RGB)")
        
        if st.button("Farben analysieren"):
            dominant_colors = get_dominant_colors(image, k=4)
            cols = st.columns(len(dominant_colors))
            for i, col_data in enumerate(dominant_colors):
                hex_val = col_data["hex"]
                rgb = col_data["rgb"]
                with cols[i]:
                    st.markdown(f"""
                    <div style="background-color: {hex_val}; height: 70px; border-radius: 12px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.3);"></div>
                    <p style="text-align: center; margin-top: 6px; font-weight: bold; font-size: 0.9rem;">{hex_val}<br><span style="font-size:0.75rem; color:#a0aec0;">RGB {rgb}</span></p>
                    """, unsafe_allow_html=True)
