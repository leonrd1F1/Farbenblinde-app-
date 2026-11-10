import streamlit as st
import numpy as np
from PIL import Image

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="ChromAId - Color Assistent",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FÜR DESIGN & HINTERGRUND ---
st.markdown("""
<style>
    /* Globaler Hintergrund für die gesamte App */
    .stApp {
        background-color: #0d1b2a;
        color: #e0e1dd;
    }
    
    /* Überschriften-Banner */
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
    
    /* Navigationskarten auf der Startseite */
    .nav-card {
        background-color: #1b263b;
        color: #e0e1dd;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        border: 2px solid #2a9d8f;
    }
    
    /* Weißer Container für Testbilder (löst das Problem mit dem dunklen/schwarzen Hintergrund) */
    .image-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 16px;
        text-align: center;
        display: inline-block;
        box-shadow: 0 6px 15px rgba(0,0,0,0.4);
        margin-bottom: 20px;
    }
    
    /* Buttons im einheitlichen Stil */
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
        color: white;
    }
    
    /* Ergebnis-Boxen */
    .result-box {
        padding: 20px;
        border-radius: 12px;
        background-color: #1b263b;
        border-left: 8px solid #2a9d8f;
        font-size: 1.2rem;
        margin-top: 20px;
        color: #e0e1dd;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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

# --- HUGGING FACE KI-MODELL LADEN ---
@st.cache_resource
def load_huggingface_model():
    try:
        from transformers import pipeline
        # Lädt ein performantes Vision-Transformer-Modell direkt aus der Hugging Face Cloud
        classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
        return classifier
    except Exception as e:
        st.error(f"Fehler beim Laden des Hugging Face Modells: {e}")
        return None

classifier = load_huggingface_model()

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
    st.info("ChromAId unterstützt Sie im Alltag bei der Farberkennung und beim Farbsehen.")

# ==========================================
# 1. SEITE: HOME (STARTSEITE)
# ==========================================
if st.session_state.page == "home":
    st.markdown('<div class="title-banner">COLOR ASSISTENT</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="nav-card">
            <h3>👁️ FARBTEST</h3>
            <p>Analysieren Sie Ihre Farbwahrnehmung mit interaktiven Testtafeln.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Test Starten", key="btn_start_test"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            navigate_to("test")
            
    with col2:
        st.markdown("""
        <div class="nav-card">
            <h3>📸 KI-ANALYSE</h3>
            <p>Laden Sie ein Bild hoch, um Farben & Zustände bestimmen zu lassen.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Bild hochladen", key="btn_start_assistant"):
            navigate_to("assistant")

# ==========================================
# 2. SEITE: MODUL B - FARBTEST (SCREENING)
# ==========================================
elif st.session_state.page == "test":
    st.markdown('<div class="title-banner">FARBTEST (SCREENING)</div>', unsafe_allow_html=True)
    
    test_questions = [
        {
            "img": "https://upload.wikimedia.org/wikipedia/commons/e/e3/Ishihara_9.png",
            "question": "Welche Zahl oder Form erkennen Sie in diesem Punktmuster?",
            "options": ["5", "6", "7 (oder ähnlich)", "Keine Zahl erkennbar"],
            "correct": "7 (or similar)"
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
        
        # Bild in einem sauberen weißen Container zentriert darstellen (verhindert unsichtbare/schwarze Bildbereiche)
        st.markdown(f"""
        <div style="text-align: center;">
            <div class="image-card">
                <img src="{q['img']}" width="280" style="border-radius: 8px;" />
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### {q['question']}")
        selected_option = st.radio("Bitte wählen Sie Ihre Option:", q["options"], key=f"q_{step}")
        
        if st.button("Nächste Frage ➔"):
            st.session_state.test_answers.append(selected_option)
            st.session_state.test_step += 1
            st.rerun()
    else:
        st.markdown("### 📊 Testergebnis & Auswertung")
        st.success("Der Farbtest wurde erfolgreich abgeschlossen!")
        
        correct_count = sum(1 for i, ans in enumerate(st.session_state.test_answers) if ans in test_questions[i]["correct"] or "7" in ans)
        
        if correct_count >= 2:
            st.info("Ergebnis-Tendenz: **Unauffälliges Farbsehen**. Es konnten keine signifikanten Anzeichen einer Farbfehlsichtigkeit festgestellt werden.")
        else:
            st.warning("Ergebnis-Tendenz: **Mögliche Auffälligkeiten im Farbsehen (z. B. Rot-Grün-Schwäche)** erkannt.")
            
        st.markdown("""
        > **Medizinischer Hinweis:** Dieses Screening dient lediglich der ersten Orientierung und ersetzt keine professionelle Diagnose beim Augenarzt oder Optiker.
        """)
        
        if st.button("🔄 Test wiederholen"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            st.rerun()

# ==========================================
# 3. SEITE: MODUL A - ALLTAGS-ASSISTENT (HUGGING FACE KI)
# ==========================================
elif st.session_state.page == "assistant":
    st.markdown('<div class="title-banner">ALLTAGSHILFE & HUGGING FACE KI</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto hoch, um eine KI-gestützte Analyse direkt aus der Cloud zu starten.")
    
    uploaded_file = st.file_uploader("Foto auswählen (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Hochgeladenes Bild", width=350)
        
        if st.button("🔍 Bild mit Hugging Face KI analysieren"):
            with st.spinner("Frage Hugging Face Cloud-Modell ab..."):
                if classifier is not None:
                    try:
                        results = classifier(image)
                        top_result = results[0]
                        label = top_result['label']
                        score = top_result['score'] * 100
                        
                        st.markdown(f"""
                        <div class="result-box">
                            <h3>KI-Ergebnis (Hugging Face):</h3>
                            <p><b>Klasse:</b> {label}</p>
                            <p><b>Konfidenz:</b> {score:.2f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Fehler bei der Klassifikation: {e}")
                else:
                    st.warning("Das Hugging Face Modell konnte nicht geladen werden.")
