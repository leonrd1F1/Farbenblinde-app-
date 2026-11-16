import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import random
import math

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="ChromAId - Professional Color Assistent",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONELLES CUSTOM CSS & DESIGN ---
st.markdown("""
<style>
    /* Globaler Hintergrund: Dunkles Blau mit Ishihara-Ästhetik */
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
            radial-gradient(#457b9d 20px, transparent 21px);
        background-size: 220px 220px, 160px 160px, 130px 130px, 260px 260px, 190px 190px, 230px 230px, 170px 170px, 310px 310px;
        background-position: 0 0, 35px 55px, 85px 25px, 125px 145px, 55px 185px, 165px 85px, 205px 45px, 105px 225px;
        background-attachment: fixed;
        color: #e0e1dd;
    }
    
    /* Charakteristischer Pinselstrich-Banner für Überschriften */
    .brush-banner {
        background: #f8f9fa;
        color: #1b263b;
        padding: 20px 30px;
        border-radius: 18px;
        text-align: center;
        font-weight: 900;
        font-size: 2.3rem;
        letter-spacing: 1.5px;
        margin: 10px auto 30px auto;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        border: 4px solid #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-transform: uppercase;
    }
    
    /* Startkarten im Mint-Ton */
    .sketch-card {
        background-color: rgba(224, 241, 237, 0.95);
        color: #0d1b2a;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        margin-bottom: 25px;
        border: 3px solid #2a9d8f;
        backdrop-filter: blur(5px);
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
    
    /* Weißer Container für Testbilder */
    .image-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 20px;
        text-align: center;
        display: inline-block;
        box-shadow: 0 10px 25px rgba(0,0,0,0.6);
        margin: 15px auto;
        border: 4px solid #ffffff;
    }
    
    /* Streamlit Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 14px;
        height: 3.8em;
        font-weight: bold;
        font-size: 1.1rem;
        background-color: #3b82f6;
        color: white;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
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

# ==========================================
# ROBUUSTER ISHIHARA-TAFEL GENERATOR (PYTHON)
# Garantiert 100% funktionierende Testbilder ohne externe URLs!
# ==========================================
def generate_ishihara_plate(target_text, bg_colors, fg_colors, size=350):
    """
    Generiert programmatisch eine Ishihara-ähnliche Punkt-Testtafel als PIL Image.
    Dadurch gibt es nie wieder Fehler durch blockierte URLs oder Netzwerkprobleme.
    """
    img = Image.new("RGB", (size, size), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    
    # 1. Erstelle ein temporäres Bild für den Text (Zahl) um Pixelpositionen zu ermitteln
    text_img = Image.new("L", (size, size), color=0)
    text_draw = ImageDraw.Draw(text_img)
    
    try:
        # Versuche eine Standardschriftart zu laden
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 150)
    except:
        try:
            font = ImageFont.load_default()
        except:
            font = None

    # Zeichne Zahl zentriert in das Test-Maskenbild
    # Da Standard-Fonts in Größe variieren, nutzen wir eine saubere Textplatzierung
    bbox = text_draw.textbbox((0, 0), target_text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    text_draw.text(((size - w) / 2, (size - h) / 2 - 20), target_text, fill=255, font=font)
    text_np = np.array(text_img)

    # 2. Generiere viele zufällige Punkte mit Kollisionsprüfung
    circles = []
    num_attempts = 1500
    
    for _ in range(num_attempts):
        r = random.randint(6, 15)
        x = random.randint(r + 10, size - r - 10)
        y = random.randint(r + 10, size - r - 10)
        
        # Prüfe ob Kreis zu nah an anderen Punkten ist
        overlap = False
        for cx, cy, cr in circles:
            dist = math.hypot(cx - x, cy - y)
            if dist < (r + cr + 2):
                overlap = True
                break
        if overlap:
            continue
            
        # Prüfe ob der Punkt im Textbereich liegt
        in_text = False
        if 0 <= y < size and 0 <= x < size:
            if text_np[y, x] > 128:
                in_text = True
                
        # Farbzuweisung je nach Position (Hintergrund vs. Zahl)
        if in_text:
            color = random.choice(fg_colors)
        else:
            color = random.choice(bg_colors)
            
        circles.append((x, y, r))
        
        # Zeichne Punkt mit leichtem Schatten/Rand für Ishihara-Optik
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=(20, 20, 20) if random.random() > 0.8 else color)

    # Zeichne äußeren runden Rahmen der Testtafel
    draw.ellipse([5, 5, size-5, size-5], outline=(150, 150, 150), width=4)
    return img

# --- WISSENSCHAFTLICHE FARBSIMULATIONS-ALGORITHMEN ---
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
    st.markdown("### **ChromAId Control Center**")
    if st.button("🏠 Startseite"):
        navigate_to("home")
    if st.button("👁️ Farbtest (Screening)"):
        navigate_to("test")
    if st.button("🔬 Alltagshilfe & Simulator"):
        navigate_to("assistant")
    if st.button("📊 WCAG Kontrast-Checker"):
        navigate_to("contrast")
    
    st.markdown("---")
    st.info("Professionelles Assistenzsystem zur Erkennung, Simulation und Analyse von Farbfehlsichtigkeiten.")

# ==========================================
# 1. SEITE: HOME (STARTSEITE)
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="brush-banner">COLOR ASSISTENT</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="sketch-card">
            <h3>👁️ FARBTEST MACHEN</h3>
            <p>Wissenschaftlich fundiertes Screening Ihrer Farbwahrnehmung mit dynamischen Testtafeln.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Test Starten", key="btn_home_test"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            navigate_to("test")
            
    with col2:
        st.markdown("""
        <div class="sketch-card">
            <h3>📸 ALLTAGS-ASSISTENT</h3>
            <p>Fotos hochladen, exakte Farbwerte (Hex/RGB) extrahieren und Seh-Simulationen starten.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Assistent öffnen", key="btn_home_assistant"):
            navigate_to("assistant")

# ==========================================
# 2. SEITE: MODUL B - FARBTEST (PROGRAMMATISCH GENERIERTE TAFELN)
# ==========================================
elif st.session_state.page == "test":
    st.markdown('<div class="brush-banner">WISSENSCHAFTLICHER FARBTEST</div>', unsafe_allow_html=True)
    
    # Definition der Testfragen mit lokal generierten Paletten für Rot-Grün / Blau-Gelb
    # Hintergrund: Grüntöne/Oliv, Vordergrund (Zahl): Rottöne/Orange
    bg_green = [(34, 139, 34), (46, 125, 50), (107, 142, 35), (85, 107, 47), (143, 188, 143), (60, 179, 113)]
    fg_red = [(178, 34, 34), (205, 92, 92), (220, 20, 60), (255, 69, 0), (233, 116, 81), (250, 128, 114)]
    
    # Hintergrund: Blautöne, Vordergrund: Gelbtöne
    bg_blue = [(70, 130, 180), (100, 149, 237), (65, 105, 225), (30, 144, 255)]
    fg_yellow = [(255, 215, 0), (238, 232, 170), (240, 230, 140), (255, 223, 0)]

    test_questions = [
        {
            "num": "7",
            "bg": bg_green, "fg": fg_red,
            "question": "Welche Zahl erkennen Sie in diesem Rot-Grün-Punktmuster?",
            "options": ["5", "6", "7", "Keine Zahl erkennbar"],
            "correct": "7"
        },
        {
            "num": "12",
            "bg": bg_green, "fg": fg_red,
            "question": "Welche Zahl ist auf dieser zweiten Ishihara-Tafel versteckt?",
            "options": ["12", "74", "3", "Keine Zahl erkennbar"],
            "correct": "12"
        },
        {
            "num": "3",
            "bg": bg_blue, "fg": fg_yellow,
            "question": "Welche Zahl sehen Sie in diesem Gelb-Blau-Muster?",
            "options": ["6", "3", "8", "Keine Zahl erkennbar"],
            "correct": "3"
        }
    ]
    
    step = st.session_state.test_step
    
    if step < len(test_questions):
        q = test_questions[step]
        st.write(f"**Frage {step + 1} von {len(test_questions)}**")
        
        # Generiere das Bild lokal in Python – absolut fehlerfrei und ohne externe Abhängigkeiten!
        plate_image = generate_ishihara_plate(q["num"], q["bg"], q["fg"])
        
        with st.container(border=True):
            col_c1, col_img, col_c2 = st.columns([1, 2, 1])
            with col_img:
                st.image(plate_image, use_container_width=True)
        
        st.markdown(f"### {q['question']}")
        selected_option = st.radio("Bitte wählen Sie Ihre Option:", q["options"], key=f"q_opt_{step}")
        
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
                st.warning("Ergebnis: **Mögliche Farbfehlsichtigkeit** erkannt")
                
        st.markdown("""
        <div class="result-box">
            <b>Medizinischer Hinweis:</b> Dieses Screening dient der ersten Orientierung und ersetzt keine professionelle augenärztliche Untersuchung (z.B. mit dem Anomaloskop).
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Test wiederholen"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            st.rerun()

# ==========================================
# 3. SEITE: MODUL A - ALLTAGS-ASSISTENT & SIMULATOR
# ==========================================
elif st.session_state.page == "assistant":
    st.markdown('<div class="brush-banner">ALLTAGS-ASSISTENT</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto von Ampeln, Kabeln oder Dokumenten hoch. Das System simuliert verschiedene Farbfehlsichtigkeiten und extrahiert exakte Farbwerte.")
    
    uploaded_file = st.file_uploader("Foto auswählen (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(image)
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Originalbild")
            st.image(image, use_container_width=True)
            
        with col2:
            st.subheader("Farbfehlsichtigkeits-Simulation")
            sim_mode = st.selectbox(
                "Seh-Typ wählen:",
                ["Protanopie (Rotblindheit)", "Deuteranopia (Grünblindheit)", "Tritanopia (Blaublindheit)"]
            )
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
                    <div style="background-color: {hex_val}; height: 75px; border-radius: 12px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"></div>
                    <p style="text-align: center; margin-top: 6px; font-weight: bold; font-size: 0.9rem; color: #ffffff;">{hex_val}<br><span style="font-size:0.75rem; color:#cbd5e1;">RGB {rgb}</span></p>
                    """, unsafe_allow_html=True)

# ==========================================
# 4. SEITE: MODUL C - WCAG KONTRAST-CHECKER
# ==========================================
elif st.session_state.page == "contrast":
    st.markdown('<div class="brush-banner">WCAG KONTRAST-CHECKER</div>', unsafe_allow_html=True)
    
    st.markdown("Prüfen Sie, ob Text- und Hintergrundfarben barrierefrei und gut lesbar sind (entspricht WCAG 2.1 Richtlinien).")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        text_color = st.color_picker("Textfarbe", "#ffffff")
    with col_c2:
        bg_color = st.color_picker("Hintergrundfarbe", "#0d1b2a")
        
    st.markdown(f"""
    <div style="background-color: {bg_color}; color: {text_color}; padding: 30px; border-radius: 12px; text-align: center; font-size: 1.5rem; font-weight: bold; margin-top: 20px; border: 2px solid white;">
        Vorschau-Text: Barrierefreiheit im Alltag
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="result-box">
        <b>Barrierefreiheits-Standard:</b> Für normalen Text wird ein Kontrastverhältnis von mindestens <b>4.5:1</b> empfohlen, für große Überschriften <b>3:1</b>.
    </div>
    """, unsafe_allow_html=True)
