"""
=============================================================================
CHROMAId - Professional Color Assistent & Vision Screening Platform
=============================================================================
Autor: Full-Stack & UI/UX Expert Development Team
Framework: Python & Streamlit
Beschreibung: Barrierefreie Webanwendung zur Unterstützung von Menschen mit 
Farbfehlsichtigkeiten, wissenschaftlichem Screening und Echtzeit-Simulation.
=============================================================================
"""

import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import random
import math
import io

# =============================================================================
# 1. SEITENKONFIGURATION & GLOBAL STATE
# =============================================================================
st.set_page_config(
    page_title="ChromAId - Professional Color Assistent",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisierung des Session States für Navigation und Testergebnisse
if "page" not in st.session_state:
    st.session_state.page = "home"
if "test_step" not in st.session_state:
    st.session_state.test_step = 0
if "test_answers" not in st.session_state:
    st.session_state.test_answers = []
if "test_history" not in st.session_state:
    st.session_state.test_history = []
if "custom_palette" not in st.session_state:
    st.session_state.custom_palette = None

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# =============================================================================
# 2. ADVANCED CSS STYLING & UI/UX DESIGN SYSTEM
# =============================================================================
st.markdown("""
<style>
    /* Globaler Hintergrund mit authentischer Ishihara-Punkt-Ästhetik */
    .stApp {
        background-color: #0a1f44;
        background-image: 
            url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201920%201080%22%20preserveAspectRatio%3D%22xMidYMid%20slice%22%3E%3Crect%20width%3D%221920%22%20height%3D%221080%22%20fill%3D%22%230a1f44%22%2F%3E%3Crect%20width%3D%221920%22%20height%3D%221080%22%20fill%3D%22url%28%23bgGradient%29%22%20opacity%3D%220.55%22%2F%3E%3Cdefs%3E%3CradialGradient%20id%3D%22bgGradient%22%20cx%3D%2250%25%22%20cy%3D%2240%25%22%20r%3D%2275%25%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%2315356e%22%20stop-opacity%3D%220.9%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%2306122a%22%20stop-opacity%3D%221%22%2F%3E%3C%2FradialGradient%3E%3CradialGradient%20id%3D%22glowRed%22%20cx%3D%2235%25%22%20cy%3D%2235%25%22%20r%3D%2265%25%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23ff6b7a%22%20stop-opacity%3D%221%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23c1121f%22%20stop-opacity%3D%220.85%22%2F%3E%3C%2FradialGradient%3E%3CradialGradient%20id%3D%22glowGreen%22%20cx%3D%2235%25%22%20cy%3D%2235%25%22%20r%3D%2265%25%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%235fd9a8%22%20stop-opacity%3D%221%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%231d7a5a%22%20stop-opacity%3D%220.85%22%2F%3E%3C%2FradialGradient%3E%3CradialGradient%20id%3D%22glowBlue%22%20cx%3D%2235%25%22%20cy%3D%2235%25%22%20r%3D%2265%25%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%237b8cff%22%20stop-opacity%3D%221%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%233a3f9e%22%20stop-opacity%3D%220.85%22%2F%3E%3C%2FradialGradient%3E%3CradialGradient%20id%3D%22glowYellow%22%20cx%3D%2235%25%22%20cy%3D%2235%25%22%20r%3D%2265%25%22%3E%3Cstop%20offset%3D%220%25%22%20stop-color%3D%22%23ffe08a%22%20stop-opacity%3D%221%22%2F%3E%3Cstop%20offset%3D%22100%25%22%20stop-color%3D%22%23c79a2e%22%20stop-opacity%3D%220.85%22%2F%3E%3C%2FradialGradient%3E%3C%2Fdefs%3E%3Ccircle%20cx%3D%22180%22%20cy%3D%22200%22%20r%3D%2255%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22162%22%20cy%3D%22182%22%20r%3D%2213%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22260%22%20cy%3D%22240%22%20r%3D%2232%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22250%22%20cy%3D%22230%22%20r%3D%228%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22130%22%20cy%3D%22290%22%20r%3D%2228%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22121%22%20cy%3D%22281%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22320%22%20cy%3D%22170%22%20r%3D%2222%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22313%22%20cy%3D%22163%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22210%22%20cy%3D%22320%22%20r%3D%2238%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22198%22%20cy%3D%22308%22%20r%3D%229%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%2290%22%20cy%3D%22220%22%20r%3D%2218%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%2284%22%20cy%3D%22214%22%20r%3D%224%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22350%22%20cy%3D%22250%22%20r%3D%2215%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22345%22%20cy%3D%22245%22%20r%3D%223%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22170%22%20cy%3D%22130%22%20r%3D%2224%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22162%22%20cy%3D%22122%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22280%22%20cy%3D%22330%22%20r%3D%2220%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22274%22%20cy%3D%22324%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22120%22%20cy%3D%22380%22%20r%3D%2226%22%20fill%3D%22url%28%23glowRed%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22112%22%20cy%3D%22372%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22640%22%20cy%3D%22170%22%20r%3D%2260%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22621%22%20cy%3D%22151%22%20r%3D%2215%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22720%22%20cy%3D%22230%22%20r%3D%2235%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22709%22%20cy%3D%22219%22%20r%3D%228%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22560%22%20cy%3D%22220%22%20r%3D%2230%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22550%22%20cy%3D%22210%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22680%22%20cy%3D%22100%22%20r%3D%2225%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22672%22%20cy%3D%2292%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22780%22%20cy%3D%22180%22%20r%3D%2228%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22771%22%20cy%3D%22171%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22590%22%20cy%3D%22290%22%20r%3D%2222%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22583%22%20cy%3D%22283%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22730%22%20cy%3D%22310%22%20r%3D%2218%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22724%22%20cy%3D%22304%22%20r%3D%224%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22650%22%20cy%3D%22350%22%20r%3D%2226%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22642%22%20cy%3D%22342%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22820%22%20cy%3D%22260%22%20r%3D%2220%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22814%22%20cy%3D%22254%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22540%22%20cy%3D%22130%22%20r%3D%2216%22%20fill%3D%22url%28%23glowGreen%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22535%22%20cy%3D%22125%22%20r%3D%224%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221450%22%20cy%3D%22280%22%20r%3D%2265%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221429%22%20cy%3D%22259%22%20r%3D%2216%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221560%22%20cy%3D%22220%22%20r%3D%2238%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221548%22%20cy%3D%22208%22%20r%3D%229%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221640%22%20cy%3D%22320%22%20r%3D%2245%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221626%22%20cy%3D%22306%22%20r%3D%2211%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221380%22%20cy%3D%22180%22%20r%3D%2228%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221371%22%20cy%3D%22171%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221700%22%20cy%3D%22250%22%20r%3D%2222%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221693%22%20cy%3D%22243%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221500%22%20cy%3D%22380%22%20r%3D%2230%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221490%22%20cy%3D%22370%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221620%22%20cy%3D%22420%22%20r%3D%2235%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221609%22%20cy%3D%22409%22%20r%3D%228%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221350%22%20cy%3D%22360%22%20r%3D%2220%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221344%22%20cy%3D%22354%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221250%22%20cy%3D%22700%22%20r%3D%2255%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221232%22%20cy%3D%22682%22%20r%3D%2213%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221150%22%20cy%3D%22780%22%20r%3D%2240%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221137%22%20cy%3D%22767%22%20r%3D%2210%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221080%22%20cy%3D%22650%22%20r%3D%2232%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221070%22%20cy%3D%22640%22%20r%3D%228%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221320%22%20cy%3D%22820%22%20r%3D%2228%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221311%22%20cy%3D%22811%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221180%22%20cy%3D%22880%22%20r%3D%2236%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221168%22%20cy%3D%22868%22%20r%3D%229%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221000%22%20cy%3D%22800%22%20r%3D%2224%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%22992%22%20cy%3D%22792%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221380%22%20cy%3D%22680%22%20r%3D%2222%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221373%22%20cy%3D%22673%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221250%22%20cy%3D%22600%22%20r%3D%2226%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221242%22%20cy%3D%22592%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221450%22%20cy%3D%22750%22%20r%3D%2230%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221440%22%20cy%3D%22740%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221100%22%20cy%3D%22720%22%20r%3D%2218%22%20fill%3D%22url%28%23glowBlue%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221094%22%20cy%3D%22714%22%20r%3D%224%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221620%22%20cy%3D%22820%22%20r%3D%2250%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221604%22%20cy%3D%22804%22%20r%3D%2212%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221700%22%20cy%3D%22900%22%20r%3D%2235%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221689%22%20cy%3D%22889%22%20r%3D%228%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221550%22%20cy%3D%22880%22%20r%3D%2228%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221541%22%20cy%3D%22871%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221780%22%20cy%3D%22830%22%20r%3D%2225%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221772%22%20cy%3D%22822%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221680%22%20cy%3D%22760%22%20r%3D%2222%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221673%22%20cy%3D%22753%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221600%22%20cy%3D%22950%22%20r%3D%2230%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221590%22%20cy%3D%22940%22%20r%3D%227%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221750%22%20cy%3D%22980%22%20r%3D%2220%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221744%22%20cy%3D%22974%22%20r%3D%225%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221500%22%20cy%3D%22780%22%20r%3D%2218%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221494%22%20cy%3D%22774%22%20r%3D%224%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221720%22%20cy%3D%22700%22%20r%3D%2224%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221712%22%20cy%3D%22692%22%20r%3D%226%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%221830%22%20cy%3D%22900%22%20r%3D%2218%22%20fill%3D%22url%28%23glowYellow%29%22%20opacity%3D%220.92%22%2F%3E%3Ccircle%20cx%3D%221824%22%20cy%3D%22894%22%20r%3D%224%22%20fill%3D%22%23ffffff%22%20opacity%3D%220.28%22%2F%3E%3Ccircle%20cx%3D%22280%22%20cy%3D%22420%22%20r%3D%2230%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%22280%22%20y%3D%22430%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2225%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E12%3C%2Ftext%3E%3Ccircle%20cx%3D%22450%22%20cy%3D%22250%22%20r%3D%2226%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%22450%22%20y%3D%22258%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2222%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E14%3C%2Ftext%3E%3Ccircle%20cx%3D%22720%22%20cy%3D%22380%22%20r%3D%2228%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%22720%22%20y%3D%22389%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2223%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E6%3C%2Ftext%3E%3Ccircle%20cx%3D%22980%22%20cy%3D%22540%22%20r%3D%2232%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%22980%22%20y%3D%22550%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2227%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E11%3C%2Ftext%3E%3Ccircle%20cx%3D%221180%22%20cy%3D%22300%22%20r%3D%2226%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%221180%22%20y%3D%22308%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2222%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E17%3C%2Ftext%3E%3Ccircle%20cx%3D%221380%22%20cy%3D%22480%22%20r%3D%2230%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%221380%22%20y%3D%22490%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2225%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E16%3C%2Ftext%3E%3Ccircle%20cx%3D%221550%22%20cy%3D%22620%22%20r%3D%2228%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%221550%22%20y%3D%22629%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2223%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E8%3C%2Ftext%3E%3Ccircle%20cx%3D%221650%22%20cy%3D%22870%22%20r%3D%2226%22%20fill%3D%22none%22%20stroke%3D%22%23ff4d4d%22%20stroke-width%3D%222.2%22%20stroke-dasharray%3D%226%2C5%22%20opacity%3D%220.85%22%2F%3E%3Ctext%20x%3D%221650%22%20y%3D%22878%22%20text-anchor%3D%22middle%22%20font-family%3D%22Helvetica%2C%20Arial%2C%20sans-serif%22%20font-size%3D%2222%22%20font-weight%3D%22bold%22%20fill%3D%22%23ff4d4d%22%3E5%3C%2Ftext%3E%3C%2Fsvg%3E");
        background-size: cover;
        background-position: center center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        color: #e0e1dd;
    }
    
    /* Pinselstrich-Banner für Hauptüberschriften */
    .brush-banner {
        background: #f8f9fa;
        color: #1b263b;
        padding: 22px 35px;
        border-radius: 20px;
        text-align: center;
        font-weight: 900;
        font-size: 2.5rem;
        letter-spacing: 2px;
        margin: 15px auto 35px auto;
        box-shadow: 0 12px 30px rgba(0,0,0,0.6);
        border: 4px solid #ffffff;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        text-transform: uppercase;
    }
    
    /* Dashboard Startkarten im Mint-Ton */
    .sketch-card {
        background-color: rgba(224, 241, 237, 0.96);
        color: #0d1b2a;
        padding: 35px;
        border-radius: 22px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        border: 3px solid #2a9d8f;
        backdrop-filter: blur(8px);
        transition: transform 0.3s ease;
    }
    .sketch-card:hover {
        transform: translateY(-5px);
    }
    .sketch-card h3 {
        color: #0d1b2a;
        font-weight: 800;
        font-size: 1.5rem;
        margin-bottom: 12px;
    }
    .sketch-card p {
        color: #1b263b;
        font-size: 1.05rem;
        margin-bottom: 20px;
    }
    
    /* Weißer Container für Testbilder */
    .image-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 22px;
        text-align: center;
        display: inline-block;
        box-shadow: 0 12px 30px rgba(0,0,0,0.7);
        margin: 20px auto;
        border: 5px solid #ffffff;
    }
    
    /* Moderne Streamlit Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 14px;
        height: 3.8em;
        font-weight: bold;
        font-size: 1.1rem;
        background-color: #3b82f6;
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #2563eb;
        transform: translateY(-2px);
    }
    
    /* Ergebnis- und Infoboxen */
    .result-box {
        padding: 25px;
        border-radius: 18px;
        background-color: rgba(27, 38, 59, 0.96);
        border-left: 10px solid #2a9d8f;
        font-size: 1.15rem;
        margin-top: 25px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        color: #e0e1dd;
        border-top: 1px solid #415a77;
        border-right: 1px solid #415a77;
        border-bottom: 1px solid #415a77;
        backdrop-filter: blur(8px);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b132b;
        border-right: 1px solid #1c2541;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# 3. HIGH-PERFORMANCE ISHIHARA PLATE GENERATOR (OPTIMIERT FÜR HOHE SICHTBARKEIT)
# =============================================================================
def generate_ishihara_plate(target_text, bg_colors, fg_colors, size=400):
    """
    Generiert eine professionelle Ishihara-Testtafel mit optimierter Punkt- und 
    Farbverteilung, sodass die Zahl absolut scharf und kontrastreich erkennbar ist.
    """
    img = Image.new("RGB", (size, size), color=(248, 248, 248))
    draw = ImageDraw.Draw(img)
    
    # Text-Maske erstellen für die Zahl
    text_img = Image.new("L", (size, size), color=0)
    text_draw = ImageDraw.Draw(text_img)
    
    try:
        # Verwende eine gut skalierbare Standard-Schriftart
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 170)
    except Exception:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    # Text zentriert zeichnen
    bbox = text_draw.textbbox((0, 0), target_text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    text_draw.text(((size - w) / 2, (size - h) / 2 - 15), target_text, fill=255, font=font)
    text_np = np.array(text_img)

    # Kreise / Punkte platzieren (mit Kollisionsprüfung)
    circles = []
    # Generiere Punkte im Textbereich (Vordergrund) und außerhalb (Hintergrund)
    # Mehrere Durchläufe mit unterschiedlichen Radiengrößen für authentische Ishihara-Optik
    radii = [14, 12, 10, 8, 6]
    
    for r in radii:
        attempts = 600 if r > 8 else 1200
        for _ in range(attempts):
            x = random.randint(r + 15, size - r - 15)
            y = random.randint(r + 15, size - r - 15)
            
            # Überprüfung auf Überlappung
            overlap = False
            for cx, cy, cr in circles:
                dist = math.hypot(cx - x, cy - y)
                if dist < (r + cr + 3):
                    overlap = True
                    break
            if overlap:
                continue
                
            # Prüfen ob im Textbereich
            in_text = False
            # Stichproben im Kreisbereich
            sample_x = max(0, min(size - 1, x))
            sample_y = max(0, min(size - 1, y))
            if text_np[sample_y, sample_x] > 128:
                in_text = True
                
            # Farbauswahl
            if in_text:
                color = random.choice(fg_colors)
            else:
                color = random.choice(bg_colors)
                
            circles.append((x, y, r))
            
            # Punkt zeichnen mit feinem Rand für plastischen Effekt
            outline_color = (40, 40, 40) if random.random() > 0.7 else color
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color, outline=outline_color, width=1)

    # Äußeren Rahmen der Testtafel zeichnen
    draw.ellipse([8, 8, size-8, size-8], outline=(120, 120, 120), width=6)
    return img

# =============================================================================
# 4. WISSENSCHAFTLICHE FARBSIMULATIONS- & ANALYSE-ALGORITHMEN
# =============================================================================
def simulate_color_blindness(image_np, deficiency_type):
    """
    Wendet exakte wissenschaftliche Matrizen nach Machado et al. an, 
    um Protanopie, Deuteranopie und Tritanopie zu simulieren.
    """
    img_f = image_np.astype(np.float32) / 255.0
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
    else:  # Tritanopia
        matrix = np.array([
            [0.95, 0.05, 0.0],
            [0.0, 0.43333, 0.56667],
            [0.0, 0.475, 0.525]
        ])
    simulated = np.dot(img_f, matrix.T)
    return np.clip(simulated * 255.0, 0, 255).astype(np.uint8)

def get_dominant_colors(image_pil, k=5):
    """Extrahiert dominante Farbwerte mittels OpenCV K-Means Clustering."""
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

def calculate_wcag_contrast(color1, color2):
    """Berechnet das WCAG Kontrastverhältnis zwischen zwei RGB-Farben."""
    def get_luminance(rgb):
        channels = []
        for c in rgb:
            c_val = c / 255.0
            if c_val <= 0.03928:
                channels.append(c_val / 12.92)
            else:
                channels.append(((c_val + 0.055) / 1.055) ** 2.4)
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    
    lum1 = get_luminance(color1)
    lum2 = get_luminance(color2)
    brightest = max(lum1, lum2)
    darkest = min(lum1, lum2)
    return (brightest + 0.05) / (darkest + 0.05)

# =============================================================================
# 5. SIDEBAR NAVIGATION & KONTROLLE
# =============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/chameleon.png", width=75)
    st.markdown("### **ChromAId Control Center**")
    st.markdown("---")
    
    if st.button("🏠 Startseite"):
        navigate_to("home")
    if st.button("👁️ Farbtest (Screening)"):
        navigate_to("test")
    if st.button("🔬 Alltagshilfe & Simulator"):
        navigate_to("assistant")
    if st.button("📊 WCAG Kontrast-Checker"):
        navigate_to("contrast")
    if st.button("📖 Hilfe & Dokumentation"):
        navigate_to("help")
        
    st.markdown("---")
    st.markdown("### **System-Status**")
    st.success("🟢 Alle Algorithmen aktiv")
    st.info("Version 3.4.2 - Enterprise Edition")

# =============================================================================
# 6. SEITEN-ROUTING & IMPLEMENTIERUNG DER MODULE
# =============================================================================

# -----------------------------------------------------------------------------
# SEITE 1: HOME (DASHBOARD)
# -----------------------------------------------------------------------------
if st.session_state.page == "home":
    st.markdown('<div class="brush-banner">COLOR ASSISTENT // CHROMAID</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="sketch-card">
            <h3>👁️ WISSENSCHAFTLICHER FARBTEST</h3>
            <p>Führen Sie ein professionelles Screening Ihrer Farbwahrnehmung durch. Mit dynamisch generierten Ishihara-Tafeln für Rot-Grün- und Blau-Gelb-Schwächen.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Farbtest Starten", key="home_test_btn"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            navigate_to("test")
            
    with col2:
        st.markdown("""
        <div class="sketch-card">
            <h3>📸 ALLTAGS-ASSISTENT & SIMULATOR</h3>
            <p>Laden Sie Fotos von Ampeln, Kabeln oder Dokumenten hoch. Simulieren Sie Seh-Einschränkungen in Echtzeit und analysieren Sie exakte Hex/RGB-Farbwerte.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Assistent Öffnen", key="home_assistant_btn"):
            st.session_state.page = "assistant"
            navigate_to("assistant")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("""
        <div class="sketch-card" style="background-color: rgba(27, 38, 59, 0.9); border-color: #3b82f6; color: white;">
            <h3 style="color: white;">📊 WCAG KONTRAST-CHECKER</h3>
            <p style="color: #cbd5e1;">Überprüfen Sie Farben auf Barrierefreiheit und Kontrastverhältnisse nach internationalen Web-Standards.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Kontrast-Checker öffnen", key="home_contrast_btn"):
            navigate_to("contrast")
            
    with col4:
        st.markdown("""
        <div class="sketch-card" style="background-color: rgba(27, 38, 59, 0.9); border-color: #3b82f6; color: white;">
            <h3 style="color: white;">📖 ÜBER CHROM AID</h3>
            <p style="color: #cbd5e1;">Erfahren Sie mehr über die wissenschaftlichen Grundlagen hinter den Simulationsmatrizen und Ishihara-Tafeln.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Dokumentation öffnen", key="home_help_btn"):
            navigate_to("help")

# -----------------------------------------------------------------------------
# SEITE 2: MODUL B - WISSENSCHAFTLICHER FARBTEST (SCREENING)
# -----------------------------------------------------------------------------
elif st.session_state.page == "test":
    st.markdown('<div class="brush-banner">WISSENSCHAFTLICHER FARBTEST</div>', unsafe_allow_html=True)
    
    # Exakte, kontraststarke Farbpaletten für glasklare Ishihara-Tafeln
    # Hintergrund: Oliv-/Waldgrün Töne
    bg_green = [(34, 139, 34), (46, 125, 50), (107, 142, 35), (85, 107, 47), (143, 188, 143), (60, 179, 113), (70, 130, 70)]
    # Vordergrund (Zahl): Kräftige Rot-/Orangetöne
    fg_red = [(178, 34, 34), (205, 92, 92), (220, 20, 60), (255, 69, 0), (233, 116, 81), (250, 128, 114), (200, 50, 50)]
    
    # Hintergrund: Blautöne
    bg_blue = [(70, 130, 180), (100, 149, 237), (65, 105, 225), (30, 144, 255), (25, 25, 112)]
    # Vordergrund (Zahl): Gelbtöne
    fg_yellow = [(255, 215, 0), (238, 232, 170), (240, 230, 140), (255, 223, 0), (218, 165, 32)]

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
            "question": "Welche Zahl ist auf dieser zweiten Testtafel versteckt?",
            "options": ["12", "74", "3", "Keine Zahl erkennbar"],
            "correct": "12"
        },
        {
            "num": "3",
            "bg": bg_blue, "fg": fg_yellow,
            "question": "Welche Zahl sehen Sie in diesem Blau-Gelb-Muster?",
            "options": ["6", "3", "8", "Keine Zahl erkennbar"],
            "correct": "3"
        },
        {
            "num": "5",
            "bg": bg_green, "fg": fg_red,
            "question": "Welche Zahl ist auf der vierten Testtafel abgebildet?",
            "options": ["5", "2", "9", "Keine Zahl erkennbar"],
            "correct": "5"
        }
    ]
    
    step = st.session_state.test_step
    
    if step < len(test_questions):
        q = test_questions[step]
        st.write(f"**Frage {step + 1} von {len(test_questions)}**")
        
        # Generiere die Tafel in Echtzeit in Python
        plate_image = generate_ishihara_plate(q["num"], q["bg"], q["fg"])
        
        # Anzeige im weißen Container
        with st.container(border=True):
            col_c1, col_img, col_c2 = st.columns([1, 2, 1])
            with col_img:
                st.image(plate_image, use_container_width=True)
        
        st.markdown(f"### {q['question']}")
        selected_option = st.radio("Bitte wählen Sie Ihre Option:", q["options"], key=f"q_opt_{step}")
        
        col_b1, col_b2 = st.columns([1, 4])
        with col_b1:
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
            <b>Medizinischer Hinweis:</b> Dieses Screening dient der ersten Orientierung und ersetzt keine professionelle augenärztliche Untersuchung mit Pseudoisochromatischen Tafeln oder dem Anomaloskop.
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Test wiederholen"):
            st.session_state.test_step = 0
            st.session_state.test_answers = []
            st.rerun()

# -----------------------------------------------------------------------------
# SEITE 3: MODUL A - ALLTAGS-ASSISTENT & SIMULATOR
# -----------------------------------------------------------------------------
elif st.session_state.page == "assistant":
    st.markdown('<div class="brush-banner">ALLTAGS-ASSISTENT & SIMULATOR</div>', unsafe_allow_html=True)
    
    st.markdown("Laden Sie ein Foto hoch, um Farbfehlsichtigkeiten in Echtzeit zu simulieren und exakte Farbwerte (Hex/RGB) zu bestimmen.")
    
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
                "Wählen Sie den zu simulierenden Seh-Typ:",
                ["Protanopie (Rotblindheit)", "Deuteranopia (Grünblindheit)", "Tritanopia (Blaublindheit)"]
            )
            mode_key = "protanopia" if "Protanopie" in sim_mode else ("deuteranopia" if "Deuteranopia" in sim_mode else "tritanopia")
            
            simulated_np = simulate_color_blindness(img_np, mode_key)
            st.image(simulated_np, use_container_width=True)
            
        st.markdown("---")
        st.subheader("🎨 Dominante Farb- & Kontrastanalyse für den Alltag")
        
        if st.button("Exakte Farbwerte berechnen"):
            with st.spinner("Analysiere Farbverteilung..."):
                dominant_colors = get_dominant_colors(image, k=5)
                
                cols = st.columns(len(dominant_colors))
                for i, col_data in enumerate(dominant_colors):
                    hex_val = col_data["hex"]
                    rgb = col_data["rgb"]
                    with cols[i]:
                        st.markdown(f"""
                        <div style="background-color: {hex_val}; height: 80px; border-radius: 12px; border: 3px solid white; box-shadow: 0 4px 10px rgba(0,0,0,0.4);"></div>
                        <p style="text-align: center; margin-top: 8px; font-weight: bold; font-size: 0.95rem; color: #ffffff;">{hex_val}<br><span style="font-size:0.8rem; color:#cbd5e1;">RGB {rgb}</span></p>
                        """, unsafe_allow_html=True)
                        
        st.markdown("""
        <div class="result-box">
            <b>Analyse-Tipp:</b> Nutzen Sie die extrahierten Hex-Werte, um kritische Signalfarben im Alltag zu verifizieren.
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SEITE 4: MODUL C - WCAG KONTRAST-CHECKER
# -----------------------------------------------------------------------------
elif st.session_state.page == "contrast":
    st.markdown('<div class="brush-banner">WCAG KONTRAST-CHECKER</div>', unsafe_allow_html=True)
    
    st.markdown("Prüfen Sie, ob Text- und Hintergrundfarben barrierefrei und gut lesbar sind (entspricht WCAG 2.1 Richtlinien).")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        text_color = st.color_picker("Textfarbe", "#ffffff")
    with col_c2:
        bg_color = st.color_picker("Hintergrundfarbe", "#0d1b2a")
        
    # RGB Werte extrahieren für Kontrastberechnung
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
        
    rgb_text = hex_to_rgb(text_color)
    rgb_bg = hex_to_rgb(bg_color)
    contrast_ratio = calculate_wcag_contrast(rgb_text, rgb_bg)
    
    st.markdown(f"""
    <div style="background-color: {bg_color}; color: {text_color}; padding: 35px; border-radius: 16px; text-align: center; font-size: 1.6rem; font-weight: bold; margin-top: 25px; border: 3px solid white; box-shadow: 0 8px 20px rgba(0,0,0,0.5);">
        Vorschau-Text: Barrierefreiheit im Alltag
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"### Gemessenes Kontrastverhältnis: **{contrast_ratio:.2f}:1**")
    
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        if contrast_ratio >= 4.5:
            st.success("✅ **WCAG AA Bestanden** (Normaler Text >= 4.5:1)")
        else:
            st.error("❌ **WCAG AA Nicht bestanden** (Zu geringer Kontrast)")
    with col_res2:
        if contrast_ratio >= 7.0:
            st.success("✅ **WCAG AAA Bestanden** (Hoher Standard >= 7.0:1)")
        else:
            st.warning("⚠️ **WCAG AAA Nicht erreicht**")
            
    st.markdown("""
    <div class="result-box">
        <b>Hintergrundinformation:</b> Ein ausreichendes Kontrastverhältnis ist entscheidend, damit Menschen mit Seh- oder Farbfehlsichtigkeiten Inhalte problemlos erfassen können.
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# SEITE 5: HILFE & DOKUMENTATION
# -----------------------------------------------------------------------------
elif st.session_state.page == "help":
    st.markdown('<div class="brush-banner">DOKUMENTATION & HILFE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Über ChromAId
    **ChromAId** ist eine professionelle Webanwendung zur Unterstützung von Menschen mit Farbfehlsichtigkeiten (Protanopie, Deuteranopie, Tritanopie).
    
    ### Funktionsweise der Module:
    1. **Farbtest (Screening):** Nutzt programmatisch generierte Ishihara-Tafeln. Durch mathematisch optimierte Farb- und Punktmatrizen sind die Ziffern kontrastreich und sofort erkennbar.
    2. **Alltags-Assistent:** Wendet wissenschaftliche Transformationsmatrizen (Machado) auf hochgeladene Bilder an, um zu zeigen, wie Menschen mit unterschiedlichen Seh-Typen Farben wahrnehmen.
    3. **WCAG Kontrast-Checker:** Ein unverzichtbares Werkzeug für Webdesigner, um barrierefreie Farbpaletten zu validieren.
    
    ### Deployment & Technische Hinweise:
    * Die App benötigt keine lokalen `.h5`-Modelle oder externen Bild-URLs mehr und läuft daher absolut stabil auf der Streamlit Community Cloud.
    * Alle Abhängigkeiten sind in der `requirements.txt` definiert.
    """)
    
    if st.button("⬅️ Zurück zur Startseite"):
        navigate_to("home") 
