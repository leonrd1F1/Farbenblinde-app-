import streamlit as st
import numpy as np
from PIL import Image
import cv2
import base64

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="ChromAId - Color Assistent",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- EXAKTER DESIGN-HINTERGRUND ALS SVG IM CODE ---
svg_bg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000">
  <rect width="1000" height="1000" fill="#0d1b2a"/>
  <!-- Cluster 1: Coral / Pink oben links -->
  <g fill="#e63946" opacity="0.85">
    <circle cx="100" cy="100" r="22"/><circle cx="135" cy="80" r="14"/><circle cx="80" cy="140" r="18"/>
    <circle cx="150" cy="120" r="12"/><circle cx="110" cy="170" r="25"/><circle cx="175" cy="95" r="16"/>
    <circle cx="60" cy="90" r="15"/><circle cx="130" cy="200" r="19"/><circle cx="90" cy="230" r="14"/>
    <circle cx="190" cy="150" r="20"/><circle cx="210" cy="110" r="13"/><circle cx="165" cy="190" r="17"/>
  </g>
  <g fill="#f15bb5" opacity="0.7">
    <circle cx="70" cy="180" r="10"/><circle cx="150" cy="60" r="12"/><circle cx="200" cy="80" r="9"/>
  </g>

  <!-- Cluster 2: Mint / Grün in der Mitte -->
  <g fill="#2a9d8f" opacity="0.9">
    <circle cx="350" cy="300" r="28"/><circle cx="400" cy="270" r="18"/><circle cx="310" cy="340" r="22"/>
    <circle cx="430" cy="320" r="15"/><circle cx="370" cy="370" r="24"/><circle cx="420" cy="380" r="19"/>
    <circle cx="300" cy="280" r="16"/><circle cx="350" cy="420" r="20"/><circle cx="460" cy="350" r="14"/>
    <circle cx="480" cy="290" r="22"/><circle cx="380" cy="230" r="17"/><circle cx="330" cy="390" r="15"/>
  </g>
  <g fill="#52b788" opacity="0.8">
    <circle cx="450" cy="250" r="12"/><circle cx="290" cy="330" r="11"/><circle cx="390" cy="430" r="13"/>
  </g>

  <!-- Cluster 3: Gelb / Orange unten rechts -->
  <g fill="#e9c46a" opacity="0.9">
    <circle cx="750" cy="750" r="30"/><circle cx="820" cy="720" r="20"/><circle cx="700" cy="800" r="25"/>
    <circle cx="850" cy="780" r="16"/><circle cx="780" cy="830" r="22"/><circle cx="830" cy="850" r="18"/>
    <circle cx="680" cy="740" r="15"/><circle cx="740" cy="880" r="19"/><circle cx="880" cy="810" r="14"/>
    <circle cx="910" cy="740" r="24"/><circle cx="800" cy="680" r="17"/><circle cx="720" cy="850" r="16"/>
  </g>
  <g fill="#f4a261" opacity="0.85">
    <circle cx="870" cy="690" r="13"/><circle cx="670" cy="790" r="12"/><circle cx="770" cy="910" r="15"/>
  </g>

  <!-- Cluster 4: Violett / Blau in der Mitte rechts -->
  <g fill="#a8dadc" opacity="0.85">
    <circle cx="600" cy="400" r="20"/><circle cx="650" cy="370" r="15"/><circle cx="560" cy="440" r="18"/>
    <circle cx="680" cy="420" r="12"/><circle cx="620" cy="470" r="22"/><circle cx="580" cy="360" r="14"/>
  </g>
  <g fill="#457b9d" opacity="0.85">
    <circle cx="700" cy="460" r="16"/><circle cx="640" cy="510" r="19"/><circle cx="550" cy="400" r="13"/>
  </g>

  <!-- Kleine Ishihara-Testteller -->
  <g stroke="#ffffff" stroke-width="1.5" stroke-dasharray="3,3" fill="#1b263b">
    <circle cx="150" cy="350" r="25"/><circle cx="650" cy="200" r="25"/>
    <circle cx="300" cy="650" r="25"/><circle cx="800" cy="550" r="25"/>
    <circle cx="500" cy="750" r="25"/><circle cx="200" cy="850" r="25"/>
  </g>
</svg>'''

svg_base64 = base64.b64encode(svg_bg.encode('utf-8')).decode('utf-8')

# --- STYLING & DESIGN ---
st.markdown(f"""
<style>
    .stApp {{
        background-image: url("data:image/svg+xml;base64,{svg_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Pinselstrich-Banner für Überschriften */
    .brush-banner {{
        background: #f8f9fa;
        color: #1b263b;
        padding: 18px 25px;
        border-radius: 18px;
        text-align: center;
        font-weight: 900;
        font-size: 2.2rem;
        letter-spacing: 1.5px;
        margin: 10px auto 30px auto;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        border: 4px solid #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-transform: uppercase;
    }}
    
    /* Startkarten im Mint-Ton */
    .sketch-card {{
        background-color: rgba(224, 241, 237, 0.95);
        color: #0d1b2a;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        margin-bottom: 25px;
        border: 3px solid #2a9d8f;
        backdrop-filter: blur(5px);
    }}
    .sketch-card h3 {{
        color: #0d1b2a;
        font-weight: 800;
        font-size: 1.4rem;
        margin-bottom: 10px;
    }}
    .sketch-card p {{
        color: #1b263b;
        font-size: 1rem;
        margin-bottom: 20px;
    }}
    
    /* Buttons */
    .stButton>button {{
        width: 100%;
        border-radius: 14px;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1rem;
        background-color: #3b82f6;
        color: white;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
    }}
    .stButton>button:hover {{
        background-color: #2563eb;
        transform: translateY(-2px);
    }}
    
    /* Ergebnis- und Info-Boxen */
    .result-box {{
        padding: 22px;
        border-radius: 16px;
        background-color: rgba(27, 38, 59, 0.95);
        border-left: 8px solid #2a9d8f;
        font-size: 1.1rem;
        margin-top: 20px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.4);
        color: #e0e1dd;
        border-top: 1px solid #415a77;
        border-right: 1px solid #415a77;
        border-bottom: 1px solid #415a77;
        backdrop-filter: blur(5px);
    }}
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

# --- ALGORITHMEN ---
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
    st.image("https://img.icons8.com/color/96/chameleon.png", width=70)
    st.markdown("### **ChromAId Navigation**")
    if st.button("🏠 Startseite"):
        navigate_to("home")
    if st.button("👁️ Farbtest (Screening)"):
        navigate_to("test")
    if st.button("🔬 Alltagshilfe & KI"):
        navigate_to("assistant")
    
    st.markdown("---")
    st.info("Barrierefreie Farbunterstützung & Screening nach Ihrem exakten Design.")

# ==========================================
# 1. SEITE: HOME (STARTSEITE)
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
        <p>Ein Bild hochladen und KI Farben & Zustände (z. B. Ampeln) bestimmen lassen.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Bild hochladen", key="btn_home_assistant"):
        navigate_to("assistant")

# ==========================================
# 2. SEITE: MODUL B - FARBTEST (Natives st.image behoben!)
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
        
        # Verwende st.container(border=True) für einen sauberen, weißen Rahmen und st.image für fehlerfreie Darstellung
        with st.container(border=True):
            col_center1, col_img, col_center2 = st.columns([1, 2, 1])
            with col_img:
                st.image(q['img'], width=280)
        
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
# 3. SEITE: MODUL A - ALLTAGSHILFE
# ==========================================
elif st.session_state.page == "assistant":
    st.markdown('<div class="brush-banner">ALLTAGSHILFE</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto von Ampeln, Kabeln oder Lebensmitteln hoch, um Farbwerte zu prüfen und Seh-Simulationen zu starten.")
    
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
                    <div style="background-color: {hex_val}; height: 70px; border-radius: 12px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"></div>
                    <p style="text-align: center; margin-top: 6px; font-weight: bold; font-size: 0.9rem; color: #ffffff;">{hex_val}<br><span style="font-size:0.75rem; color:#cbd5e1;">RGB {rgb}</span></p>
                    """, unsafe_allow_html=True)
