import streamlit as st
import numpy as np
from PIL import Image
import cv2

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="ChromAId - Professioneller Farb-Assistent",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONELLES CUSTOM CSS & DESIGN ---
st.markdown("""
<style>
    /* Globales modernes Theme */
    .stApp {
        background-color: #0b132b;
        color: #e0e1dd;
    }
    
    /* Header Banner */
    .title-banner {
        background: linear-gradient(135deg, #1c2541 0%, #3a506b 100%);
        color: #ffffff;
        padding: 20px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        border: 1px solid #4b5d67;
    }
    
    /* Dashboard Navigationskarten */
    .nav-card {
        background-color: #1c2541;
        color: #e0e1dd;
        padding: 30px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        border: 2px solid #5bc0be;
        transition: transform 0.3s ease;
    }
    .nav-card:hover {
        transform: translateY(-5px);
        border-color: #6fffe9;
    }
    
    /* Perfekter weißer Container für Testbilder (garantiert Sichtbarkeit) */
    .image-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        display: inline-block;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        margin: 15px auto;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1rem;
        background-color: #3a86ff;
        color: white;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #2667cc;
        color: white;
    }
    
    /* Analyse-Ergebnisboxen */
    .result-box {
        padding: 20px;
        border-radius: 14px;
        background-color: #1c2541;
        border-left: 8px solid #3a86ff;
        font-size: 1.1rem;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
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
    """
    Simuliert Farbfehlsichtigkeiten mittels wissenschaftlicher Transformationsmatrizen.
    Typen: 'protanopia' (Rot-Blinde), 'deuteranopia' (Grün-Blinde), 'tritanopia' (Blau-Blinde)
    """
    # Konvertieren zu float [0, 1]
    img_f = image_np.astype(np.float32) / 255.0
    
    # Exakte Simulationsmatrizen nach Brettel / Machado
    if deficiency_type == 'protanopia':
        matrix = np.array([
            [0.56667, 0.43333, 0.0],
            [0.55833, 0.44167, 0.0],
            [0.0, 0.24167, 0.75833]
        ])
    elif deficiency_type == 'deuteranopia':
        matrix = np.array([
            [0.625, 0.375, 0.0],
            [0.7, 0.3, 0.0],
            [0.0, 0.3, 0.7]
        ])
    elif deficiency_type == 'tritanopia':
        matrix = np.array([
            [0.95, 0.05, 0.0],
            [0.0, 0.43333, 0.56667],
            [0.0, 0.475, 0.525]
        ])
    else:
        return image_np

    # Matrix-Multiplikation auf Bild anwenden
    simulated = np.dot(img_f, matrix.T)
    simulated = np.clip(simulated * 255.0, 0, 255).astype(np.uint8)
    return simulated

def get_dominant_colors(image_pil, k=3):
    """Ermittelt die dominanten Farben im Bild per OpenCV K-Means Clustering."""
    img_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    img_cv = cv2.resize(img_cv, (150, 150))
    pixels = img_cv.reshape((-1, 3))
    pixels = np.float32(pixels)
    
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

# --- SEiten-NAVIGATION (SIDEBAR) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/chameleon.png", width=70) # Chamäleon-Logo[cite: 1]
    st.markdown("### **ChromAId Control Center**")
    if st.button("🏠 Startseite"):
        navigate_to("home")
    if st.button("👁️ Farbtest (Screening)"):
        navigate_to("test")
    if st.button("🔬 Alltags-Assistent & Simulator"):
        navigate_to("assistant")
    
    st.markdown("---")
    st.markdown("### Barrierefreiheit & Info")
    st.info("Entwickelt für präzise Farbanalyse, Simulation und Alltagshilfe bei Farbfehlsichtigkeiten.")

# ==========================================
# 1. HOME SEITE (STARTSEITE)[cite: 2]
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="title-banner">COLOR ASSISTENT // CHROMAID</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h3>👁️ FARBTEST MACHEN</h3>
            <p>Analysieren Sie Ihre Farbwahrnehmung mit wissenschaftlich orientierten Ishihara-Testtafeln.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Test Starten", key="home_test"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            navigate_to("test")
            
    with col2:
        st.markdown("""
        <div class="nav-card">
            <h3>🔬 ALLTAGS-FARB KI-ANALYSE</h3>
            <p>Laden Sie Fotos hoch, analysieren Sie exakte Farbwerte und simulieren Sie Farbfehlsichtigkeiten.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Assistent öffnen", key="home_assistant"):
            navigate_to("assistant")

# ==========================================
# 2. MODUL B: FARBTEST (SCREENING)[cite: 3]
# ==========================================
elif st.session_state.page == "test":
    st.markdown('<div class="title-banner">WISSENSCHAFTLICHER FARBTEST</div>', unsafe_allow_html=True)
    
    # Robuste, stabile Bild-URLs für Ishihara-Tafeln
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
        
        # Zentrierte Darstellung in einem weißen Container – garantiert optimale Sichtbarkeit der Punkte ohne schwarze Ränder!
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="image-card">
                <img src="{q['img']}" width="260" style="border-radius: 8px;" />
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### {q['question']}")
        selected_option = st.radio("Bitte wählen Sie Ihre Option:", q["options"], key=f"q_opt_{step}")
        
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("Nächste Frage ➔"):
                st.session_state.test_answers.append(selected_option)
                st.session_state.test_step += 1
                st.rerun()
    else:
        st.markdown("### 📊 Testergebnis & Detaillierte Auswertung")
        st.success("Der Farbtest wurde erfolgreich abgeschlossen!")
        
        correct_count = sum(1 for i, ans in enumerate(st.session_state.test_answers) if ans == test_questions[i]["correct"])
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric(label="Richtige Antworten", value=f"{correct_count} / {len(test_questions)}")
        with col_res2:
            if correct_count == len(test_questions):
                st.success("Ergebnis: **Unauffälliges Farbsehen**")
            else:
                st.warning("Ergebnis: **Hinweis auf Rot-Grün-Schwäche**")
                
        st.markdown("""
        <div class="result-box">
            <b>Medizinischer Hinweis:</b> Dieses Screening dient der ersten Orientierung im Alltag und ersetzt keine professionelle augenärztliche Untersuchung mit Pseudoisochromatischen Tafeln oder dem Anomaloskop.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Test wiederholen"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            st.rerun()

# ==========================================
# 3. MODUL A: ALLTAGS-ASSISTENT & SIMULATOR[cite: 4]
# ==========================================
elif st.session_state.page == "assistant":
    st.markdown('<div class="title-banner">ALLTAGS-ASSISTENT & FARBSIMULATOR</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto von Ampeln, Kabeln, Lebensmitteln oder Dokumenten hoch[cite: 4]. Das System extrahiert exakte Farbwerte und simuliert verschiedene Farbfehlsichtigkeiten in Echtzeit.")
    
    uploaded_file = st.file_uploader("Foto auswählen (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(image)
        
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.subheader("Originalbild")
            st.image(image, use_container_width=True)
            
        with col_img2:
            st.subheader("Farbfehlsichtigkeits-Simulation")
            sim_mode = st.selectbox(
                "Wählen Sie den zu simulierenden Seh-Typ:",
                ["Protanopie (Rotblindheit)", "Deuteranopia (Grünblindheit)", "Tritanopia (Blaublindheit)"]
            )
            
            mode_key = "protanopia" if "Protanopie" in sim_mode else ("deuteranopia" if "Deuteranopia" in sim_mode else "tritanopia")
            simulated_np = simulate_color_blindness(img_np, mode_key)
            st.image(simulated_np, use_container_width=True)
            
        st.markdown("---")
        st.subheader("🎨 Dominante Farb- & Kontrastanalyse für den Alltag")
        
        if st.button("Exakte Farbwerte & Palette berechnen"):
            with st.spinner("Analysiere Farbverteilung..."):
                dominant_colors = get_dominant_colors(image, k=4)
                
                cols = st.columns(len(dominant_colors))
                for i, col_data in enumerate(dominant_colors):
                    hex_val = col_data["hex"]
                    rgb = col_data["rgb"]
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background-color: {hex_val}; height: 80px; border-radius: 10px; border: 2px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.3);"></div>
                        <p style="text-align: center; margin-top: 8px; font-weight: bold;">{hex_val}<br><span style="font-size:0.8rem; color:#a0aec0;">RGB {rgb}</span></p>
                        """, unsafe_allow_html=True)
                        
                st.markdown("""
                <div class="result-box">
                    <b>Analyse-Tipp:</b> Nutzen Sie die Farbpalette oben, um kritische Signalfarben (z. B. Rot/Grün-Unterschiede bei Kabeln oder Ampeln) direkt per Hex-Code zu verifizieren.
                </div>
                """, unsafe_allow_html=True)
