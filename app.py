import streamlit as st
import numpy as np
from PIL import Image
import cv2
import os

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="ChromAId - Color Assistent",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FÜR BARRIEREFREIHEIT & DESIGN ---
st.markdown("""
<style>
    /* Allgemeine Farbpalette & High Contrast */
    :root {
        --bg-color: #0d1b2a;
        --card-bg: #1b263b;
        --accent-color: #415a77;
        --highlight: #e0e1dd;
        --success: #2a9d8f;
        --warning: #e76f51;
    }
    
    .main {
        background-color: var(--bg-color);
        color: var(--highlight);
    }
    
    /* Überschriften im Chalkboard/Brush-Stil der Vorlage */
    .title-banner {
        background: #f8f9fa;
        color: #1b263b;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: 800;
        font-size: 2rem;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Karten-Design für Startscreen (angelehnt an UI-Skizze) */
    .nav-card {
        background-color: #e0f1ed;
        color: #0d1b2a;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        margin-bottom: 20px;
        border: 2px solid #2a9d8f;
        transition: transform 0.2s ease;
    }
    .nav-card:hover {
        transform: translateY(-3px);
    }
    
    /* Große, barrierefreie Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5em;
        font-weight: bold;
        font-size: 1.1rem;
        background-color: #2a9d8f;
        color: white;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #21867a;
    }
    
    /* Info-Boxen */
    .result-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #1b263b;
        border-left: 8px solid #2a9d8f;
        font-size: 1.2rem;
        margin-top: 20px;
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

# --- HILFSFUNKTIONEN ---
def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

@st.cache_resource
def load_ai_model():
    model_path = "model/keras_model.h5"
    labels_path = "model/labels.txt"
    
    if not os.path.exists(model_path) or not os.path.exists(labels_path):
        return None, None
    
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path, compile=False)
        with open(labels_path, "r", encoding="utf-8") as f:
            labels = [line.strip() for line in f.readlines()]
        return model, labels
    except Exception as e:
        st.error(f"Fehler beim Laden des KI-Modells: {e}")
        return None, None

model, labels = load_ai_model()

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/chameleon.png", width=80)
    st.markdown("### **ChromAId Navigation**")
    if st.button("🏠 Startseite (Home)"):
        navigate_to("home")
    if st.button("👁️ Farbtest (Screening)"):
        navigate_to("test")
    if st.button("📸 Alltags-Assistent (KI)"):
        navigate_to("assistant")
    
    st.markdown("---")
    st.markdown("### Barrierefreiheit")
    high_contrast = st.checkbox("Hoher Kontrast / Modus", value=True)
    st.info("ChromAId unterstützt Sie im Alltag bei der Farberkennung und beim Farbsehen[cite: 1, 2].")

# ==========================================
# 1. SEITE: HOME (STARTSEITE)[cite: 2]
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="title-banner">COLOR ASSISTENT</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h3>👁️ FARBTEST MACHEN</h3>
            <p>Analysieren Sie Ihre Farbwahrnehmung und erhalten Sie strukturierte Ergebnisse.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Starten", key="btn_start_test"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            navigate_to("test")
            
    with col2:
        st.markdown("""
        <div class="nav-card">
            <h3>📸 ALLTAGS-FARB KI-ANALYSE</h3>
            <p>Ein Bild hochladen und KI Farben & Zustände (z. B. Ampeln) bestimmen lassen[cite: 4].</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Bild hochladen", key="btn_start_assistant"):
            navigate_to("assistant")

# ==========================================
# 2. SEITE: MODUL B - FARBTEST (SCREENING)[cite: 3]
# ==========================================
elif st.session_state.page == "test":
    st.markdown('<div class="title-banner">FARBTEST</div>', unsafe_allow_html=True)
    
    # Definition von Test-Fragen (Ishihara-inspiriert)
    test_questions = [
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Ishihara_9.png", # Beispiel Ishihara Tafel
            "question": "Welche Zahl oder Form erkennen Sie in diesem Punktmuster?",
            "options": ["5", "6", "7 (oder ähnlich)", "Keine Zahl erkennbar"],
            "correct": "7 (oder ähnlich)"
        },
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/7/7f/Ishihara_1.png",
            "question": "Welche Zahl sehen Sie auf dieser Testtafel?",
            "options": ["12", "74", "3", "Keine Zahl"],
            "correct": "12"
        },
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Ishihara_3.png",
            "question": "Welche Zahl ist hier versteckt?",
            "options": ["6", "29", "45", "Keine Zahl"],
            "correct": "6"
        }
    ]
    
    step = st.session_state.test_step
    
    if step < len(test_questions):
        q = test_questions[step]
        st.write(f"**Frage {step + 1} von {len(test_questions)}**")
        st.image(q["img"], width=320, caption="Ishihara-Testtafel")
        st.markdown(f"### {q['question']}")
        
        selected_option = st.radio("Bitte wählen Sie Ihre Option:", q["options"], key=f"q_{step}")
        
        if st.button("Nächste Frage ➔"):
            st.session_state.test_answers.append(selected_option)
            st.session_state.test_step += 1
            st.rerun()
    else:
        # Auswertung
        st.markdown("### 📊 Testergebnis & Auswertung")
        st.success("Der Farbtest wurde erfolgreich abgeschlossen!")
        
        # Algorithmus-Score (vereinfacht zu Demonstrationszwecken)
        correct_count = sum(1 for i, ans in enumerate(st.session_state.test_answers) if ans == test_questions[i]["correct"])
        
        if correct_count == len(test_questions):
            st.info("Ergebnis-Tendenz: **Unauffälliges Farbsehen**. Es konnten keine signifikanten Anzeichen einer Farbfehlsichtigkeit festgestellt werden.")
        elif correct_count >= 1:
            st.warning("Ergebnis-Tendenz: **Mögliche Rot-Grün-Schwäche (z. B. Deuteranopie/Protanopie)** erkannt.")
        else:
            st.warning("Ergebnis-Tendenz: **Auffälligkeiten im Farbsehen** festgestellt.")
            
        st.markdown("""
        > **Medizinischer Hinweis:** Dieses Screening dient lediglich der ersten Orientierung und ersetzt keinesfalls eine professionelle Diagnose beim Augenarzt oder Optiker.
        """)
        
        if st.button("🔄 Test wiederholen"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            st.rerun()

# ==========================================
# 3. SEITE: MODUL A - ALLTAGS-ASSISTENT[cite: 4]
# ==========================================
elif st.session_state.page == "assistant":
    st.markdown('<div class="title-banner">ALLTAGSHILFE & KI-ANALYSE</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto von Ampeln, Kabeln oder Lebensmitteln hoch, um eine sofortige KI-Analyse zu erhalten[cite: 4].")
    
    uploaded_file = st.file_uploader("Foto auswählen (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Hochgeladenes Bild", width=350)
        
        if st.button("🔍 Bild analysieren"):
            with st.spinner("KI analysiert Farben und Zustände..."):
                if model is not None and labels is not None:
                    # Echte Teachable Machine Modell-Inferenz
                    image_resized = image.resize((224, 224))
                    image_array = np.asarray(image_resized)
                    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
                    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
                    data[0] = normalized_image_array
                    
                    prediction = model.predict(data)
                    index = np.argmax(prediction)
                    class_name = labels[index]
                    confidence_score = prediction[0][index]
                    
                    st.markdown(f"""
                    <div class="result-box">
                        <h3>Ergebnis:</h3>
                        <p><b>{class_name}</b></p>
                        <p style="font-size: 0.9rem; color: #a0aec0;">Konfidenz: {confidence_score * 100:.2f}%</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Fallback-Modus für Demo-Zwecke (ohne `.h5` Datei)
                    st.markdown("""
                    <div class="result-box" style="border-left-color: #e76f51;">
                        <h3>Ergebnis (Demo-Modus):</h3>
                        <p style="font-size: 1.5rem; font-weight: bold; color: #ff6b6b;">🔴 Die Ampel ist rot — STOPP</p>
                        <p style="font-size: 0.9rem; color: #a0aec0;">(Hinweis: Kein Teachable Machine Modell gefunden. Legen Sie <code>keras_model.h5</code> & <code>labels.txt</code> in den Ordner <code>model/</code>, um echte Klassifikation zu aktivieren).</p>
                    </div>
                    """, unsafe_allow_html=True)
