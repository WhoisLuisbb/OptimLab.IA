import streamlit as st
import numpy as np
from pathlib import Path
import re
import joblib
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
import json
import warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS (SETUP)
# ==========================================
st.set_page_config(page_title="OptimLab.IA", layout="wide", page_icon="🔊")

# CSS: Estilo Cyberpunk + Marco del Menú + Ajustes de Texto
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
.stApp {
    background-color: #020205;
    background-image: 
        radial-gradient(circle at 50% 50%, rgba(20, 20, 40, 0.4) 0%, rgba(0, 0, 0, 0.9) 100%),
        linear-gradient(rgba(0, 255, 255, 0.07) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 255, 255, 0.07) 1px, transparent 1px);
    background-size: cover, 40px 40px, 40px 40px;
    color: #e0e0e0;
    font-family: 'Roboto Mono', monospace;
}
h1, h2, h3 {
    color: #00ffff !important;
    text-shadow: 2px 2px 0px #ff00ff;
    font-family: 'Roboto Mono', monospace;
    text-transform: uppercase;
}
/* EL MARCO DEL MENÚ (Caja con borde neon) - INVISIBLE */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: none !important;
    background-color: transparent !important;
    box-shadow: none !important;
    border-radius: 0px;
    padding: 0px;
}
/* Botones con centrado */
div.stButton {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
    text-align: center;
}
.stButton > button {
    background: linear-gradient(45deg, #000000, #1a1a1a);
    color: #00ffff;
    border: 2px solid #00ffff;
    border-bottom: 4px solid #ff00ff;
    font-weight: bold;
    display: block;
    margin: 10px auto;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
    padding: 12px 24px;
    min-width: 280px;
    max-width: 350px;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.stButton > button:hover {
    background: linear-gradient(45deg, #00ffff, #0088ff);
    color: #000000;
    box-shadow: 0 0 25px #00ffff;
    transform: translateY(-3px);
}
.stButton > button:active {
    transform: translateY(-1px);
}
/* Botones principales (iniciar análisis, avanzar) */
.stButton > button[kind="primary"] {
    background: linear-gradient(45deg, #003366, #001133);
    border: 2px solid #00ffff;
    border-bottom: 4px solid #ff00ff;
    font-weight: 900;
    font-size: 1.2rem;
    min-height: 70px;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(45deg, #00ffff, #0088ff);
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.8);
}
/* Botones secundarios (obtener recomendación) */
.stButton > button[kind="secondary"] {
    background: linear-gradient(45deg, #330033, #220022);
    border: 2px solid #ff00ff;
    border-bottom: 4px solid #00ffff;
    min-height: 60px;
}
.stButton > button[kind="secondary"]:hover {
    background: linear-gradient(45deg, #ff00ff, #cc00cc);
    color: #000000;
    box-shadow: 0 0 25px rgba(255, 0, 255, 0.8);
}
/* Botones de elección */
.choice-button {
    background: linear-gradient(45deg, #001122, #003344) !important;
    border: 3px solid #00ffff !important;
    font-size: 1.1rem !important;
    font-weight: 900 !important;
    padding: 15px 25px !important;
    min-width: 250px !important;
    height: auto !important;
    min-height: 60px !important;
    margin: 10px 0 !important;
    box-shadow: 0 0 15px rgba(0, 255, 255, 0.3) !important;
}
.choice-button:hover {
    background: linear-gradient(45deg, #00ffff, #0088ff) !important;
    color: #000000 !important;
    box-shadow: 0 0 25px rgba(0, 255, 255, 0.8) !important;
    transform: translateY(-3px) !important;
}
.choice-initial {
    border-color: #ff0000 !important;
    background: linear-gradient(45deg, #440000, #220000) !important;
}
.choice-ia {
    border-color: #00ff00 !important;
    background: linear-gradient(45deg, #004400, #002200) !important;
}
.choice-manual {
    border-color: #ffff00 !important;
    background: linear-gradient(45deg, #444400, #222200) !important;
}
/* Sliders modernos (faders) */
.stSlider {
    padding: 12px 0 10px 0 !important;
    margin: 0 !important;
}
.stSlider label {
    font-size: 0.8rem !important;
    font-weight: bold !important;
    color: #00ffff !important;
    margin-bottom: 8px !important;
    display: block !important;
    line-height: 1.3 !important;
}
/* Pista del slider */
.stSlider > div > div:nth-child(2) {
    margin-top: 5px !important;
}
.stSlider > div > div:nth-child(2) > div:nth-child(1) {
    background: transparent !important;
    border-radius: 0px !important;
    height: 0px !important;
}
.stSlider > div > div:nth-child(2) > div:nth-child(1) > div {
    background: linear-gradient(45deg, #00ffff, #ff00ff) !important;
    border: 2px solid white !important;
    box-shadow: 0 0 12px rgba(0, 255, 255, 0.8) !important;
    width: 14px !important;
    height: 14px !important;
    border-radius: 50% !important;
    top: -5px !important;
}
/* Contenedor de valores min/max */
.stSlider > div > div:nth-child(2) > div:nth-child(2) {
    display: flex !important;
    justify-content: space-between !important;
    margin-top: 3px !important;
    padding: 0 2px !important;
}
/* Valores del slider (min/max/actual) */
.stSlider > div > div:nth-child(2) > div:nth-child(2) > span {
    font-size: 0.65rem !important;
    color: #ff00ff !important;
    font-weight: bold !important;
    line-height: 1 !important;
}
/* Columnas para sliders */
[data-testid="column"] {
    padding: 0 8px !important;
}
/* Inputs y Selectores */
div[data-baseweb="select"] > div, div[data-baseweb="radio"] {
    background-color: rgba(0,0,0,0.5) !important;
    color: #fff !important;
    border-color: #333 !important;
}
/* Alerts y Expander */
.stAlert {
    background-color: rgba(0, 20, 40, 0.8);
    border: 1px solid #00ffff;
    color: #e0e0e0;
}
/* Paneles de texto (marco) */
.neon-panel {
    border: 2px solid rgba(0, 255, 255, 0.85);
    background: linear-gradient(180deg, rgba(0, 15, 35, 0.95), rgba(0, 5, 20, 0.75));
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.25), inset 0 0 20px rgba(0, 255, 255, 0.05);
    border-radius: 12px;
    padding: 22px 22px;
    margin: 15px 0 25px 0;
}
.neon-panel .panel-title {
    color: #00ffff;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.6), 2px 2px 0px rgba(255, 0, 255, 0.5);
    font-weight: 800;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin: 0 0 12px 0;
    font-size: 1.2rem;
}
.neon-panel p {
    color: #e0e0e0;
    font-size: 0.95rem;
    line-height: 1.6rem;
    margin: 0 0 10px 0;
}
.neon-panel p:last-child {
    margin-bottom: 0;
}
/* Estado inicial de los expanders cerrados */
.streamlit-expanderHeader {
    border: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 5px !important;
    margin-bottom: 5px !important;
}
.streamlit-expanderContent {
    border-left: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-right: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-bottom: 1px solid rgba(0, 255, 255, 0.3) !important;
    border-radius: 0 0 5px 5px !important;
    padding: 15px !important;
}
/* Espaciado entre columnas para evitar superposición */
[data-testid="column"] {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px !important;
}
/* Contenedores de botones */
div.row-widget.stHorizontalBlock {
    gap: 20px !important;
    justify-content: center !important;
    align-items: center !important;
}
/* Botones en fila */
div[data-testid="column"] > div {
    display: flex;
    justify-content: center;
    width: 100%;
}
/* Contenedores con borde - INVISIBLE */
[data-testid="stContainer"] {
    border: none !important;
    background: transparent !important;
    border-radius: 0px;
    padding: 0px !important;
    margin: 0px !important;
    box-shadow: none !important;
}
/* Subheaders en columnas */
.stSubheader {
    color: #00ffff !important;
    text-shadow: 0 0 8px rgba(0, 255, 255, 0.4) !important;
    font-size: 1.1rem !important;
    font-weight: bold !important;
    margin-bottom: 12px !important;
}
/* Cajitas neon para recomendaciones */
.recommendation-box {
    border: 2px solid #00ffff;
    background: linear-gradient(135deg, rgba(0, 25, 50, 0.95), rgba(0, 5, 25, 0.95));
    box-shadow: 0 0 30px rgba(0, 255, 255, 0.5), inset 0 0 20px rgba(0, 255, 255, 0.1);
    border-radius: 14px;
    padding: 28px;
    margin: 25px 0;
    position: relative;
    overflow: hidden;
}
.recommendation-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00ffff, #ff00ff, #00ffff);
    animation: shimmer 3s infinite linear;
}
.recommendation-title {
    color: #00ffff;
    text-shadow: 0 0 10px rgba(0, 255, 255, 0.7);
    font-size: 1.4rem;
    font-weight: 900;
    text-align: center;
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 2px;
}
.recommendation-metric {
    background: rgba(0, 0, 0, 0.4);
    border: 1px solid rgba(0, 255, 255, 0.3);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
    transition: all 0.3s ease;
}
.recommendation-metric:hover {
    background: rgba(0, 255, 255, 0.1);
    border-color: #00ffff;
    transform: translateY(-2px);
}
.metric-title {
    color: #ff00ff;
    font-size: 1rem;
    font-weight: bold;
    margin-bottom: 5px;
}
.metric-value {
    color: #00ffff;
    font-size: 1.8rem;
    font-weight: 900;
    text-shadow: 0 0 8px rgba(0, 255, 255, 0.5);
}
@keyframes shimmer {
    0% { background-position: -200px 0; }
    100% { background-position: 200px 0; }
}
/* Mejoras para las métricas de streamlit */
[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
    font-weight: 900 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 1rem !important;
    font-weight: bold !important;
}
/* Contenedor específico para botones de elección */
.election-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 15px !important;
}
/* Checkboxes mejorados */
[data-testid="stCheckbox"] {
    margin: 8px 0 !important;
}
[data-testid="stCheckbox"] label {
    color: #00ffff !important;
    font-weight: 600 !important;
}
/* Dividers */
hr, [data-testid="stHorizontalBlock"] > hr {
    border: none !important;
    height: 2px !important;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.5), transparent) !important;
    margin: 15px 0 !important;
}
/* Radios mejorados */
[data-testid="stRadio"] {
    margin: 10px 0 !important;
}
[data-testid="stRadio"] label {
    color: #00ffff !important;
    font-weight: 600 !important;
}
    width: 100%;
    margin: 0 auto;
}
.election-button {
    min-height: 60px !important;
    margin: 5px 0 !important;
}
/* Hacer columnas completamente invisibles */
[data-testid="column"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}
/* Hacer filas horizontales invisibles */
div[data-testid="stHorizontalBlock"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
/* Hacer tabs y expanders sin fondo */
.streamlit-expanderHeader {
    border: none !important;
    border-radius: 0px !important;
    margin-bottom: 0px !important;
    background: transparent !important;
}
.streamlit-expanderContent {
    border: none !important;
    border-radius: 0px !important;
    padding: 0px !important;
    background: transparent !important;
}
/* Bloques de contenido general invisible */
div.stBlock--scrollContainer {
    background: transparent !important;
}
/* Contenedor raíz de Streamlit invisible */
.stMain > [data-testid="stVerticalBlockBorderWrapper"] {
    background: transparent !important;
    border: none !important;
}
.theory-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    margin: 16px 0 24px 0;
}
.theory-card {
    border: 1px solid rgba(0, 255, 255, 0.4);
    border-radius: 12px;
    padding: 16px;
    background: linear-gradient(180deg, rgba(0, 22, 40, 0.92), rgba(0, 7, 20, 0.78));
    box-shadow: 0 0 16px rgba(0, 255, 255, 0.14);
}
.theory-card h4 {
    color: #00ffff;
    margin: 0 0 8px 0;
    font-size: 1rem;
}
.theory-card p {
    margin: 0;
    color: #d9f7ff;
    font-size: 0.9rem;
    line-height: 1.5rem;
}
.equation-box {
    border-left: 4px solid #ff00ff;
    background: rgba(255, 0, 255, 0.08);
    padding: 12px 16px;
    border-radius: 8px;
    margin: 10px 0 18px 0;
}
</style>
""", unsafe_allow_html=True)

# Matplotlib Dark Theme
plt.style.use('dark_background')
plt.rcParams.update({
    'axes.facecolor': (0,0,0,0),
    'figure.facecolor': (0,0,0,0),
    'grid.color': '#00ffff',
    'grid.linestyle': ':',
    'text.color': '#e0e0e0',
    'axes.labelcolor': '#ff00ff',
    'xtick.color': '#00ffff',
    'ytick.color': '#00ffff',
    'axes.edgecolor': '#00ffff'
})

# ==========================================
# 2. CONSTANTES Y RUTAS (AJUSTADAS A NUEVOS MODELOS)
# ==========================================
CLEAN_DIR = Path("CLEAN_FILES_NORM") if Path("CLEAN_FILES_NORM").exists() else Path("CLEAN_FILES")

# Modelos nuevos (ajusta estas rutas según tu Google Drive)
MODEL_EQUALES = Path("aligner_type0_final.keras")
MODEL_DIFERENTES = Path("aligner_type0_diff_dist8_final.keras")

N_BINS = 2048
FMIN, FMAX = 20.0, 20000.0
MAX_DELAY_MS = 30.0
MAX_GAIN_DB = 6.0
SOUND_SPEED = 343.0
NUM_RE = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")

# ==========================================
# 3. FUNCIONES DSP (CORE LOGIC)
# ==========================================
def stable_seed(*items) -> int:
    s = "|".join(str(x) for x in items).encode("utf-8")
    return int(hashlib.sha256(s).hexdigest()[:8], 16)

def magphase_deg_to_complex(mag_db, phase_deg):
    return (10.0 ** (mag_db / 20.0) * np.exp(1j * np.deg2rad(phase_deg))).astype(np.complex64)

def complex_to_magphase_deg(X):
    return (20*np.log10(np.maximum(np.abs(X), 1e-12))).astype(np.float32), np.rad2deg(np.angle(X)).astype(np.float32)

def apply_dsp(X, f_hz, delay_ms, gain_db, pol):
    phase_shift = np.deg2rad(-360.0 * f_hz * (delay_ms / 1000.0)).astype(np.float32)
    out = X * np.exp(1j * phase_shift) * (10.0**(gain_db/20.0))
    if pol:
        out = -out
    return out.astype(np.complex64)

def find_crossover_frequency(f, mag_AB, mag_C):
    """Encuentra la frecuencia de cruce donde las dos fuentes comparten energía de manera significativa."""
    # Para subwoofers, nos interesan las bajas frecuencias (20-200 Hz)
    low_freq_mask = (f >= 20) & (f <= 200)
    
    if not np.any(low_freq_mask):
        return 100.0  # Frecuencia por defecto
    
    f_low = f[low_freq_mask]
    mag_AB_low = mag_AB[low_freq_mask]
    mag_C_low = mag_C[low_freq_mask]
    
    # Normalizar las magnitudes en el rango bajo
    mag_AB_norm = mag_AB_low - np.max(mag_AB_low)
    mag_C_norm = mag_C_low - np.max(mag_C_low)
    
    # Encontrar puntos donde ambas tienen energía razonable (dentro de -15 dB del máximo)
    threshold = -15
    mask_AB_valid = mag_AB_norm >= threshold
    mask_C_valid = mag_C_norm >= threshold
    
    # Intersección de rangos válidos
    valid_mask = mask_AB_valid & mask_C_valid
    
    if np.any(valid_mask):
        mag_diff = np.abs(mag_AB_norm[valid_mask] - mag_C_norm[valid_mask])
        
        if len(mag_diff) > 5:
            kernel_size = min(5, len(mag_diff))
            kernel = np.ones(kernel_size) / kernel_size
            mag_diff_smooth = np.convolve(mag_diff, kernel, mode='valid')
            
            min_idx_smooth = np.argmin(mag_diff_smooth)
            min_idx = min_idx_smooth + kernel_size // 2
            min_idx = min(min_idx, len(f_low[valid_mask]) - 1)
        else:
            min_idx = np.argmin(mag_diff)
        
        crossover_freq = f_low[valid_mask][min_idx]
        
        if crossover_freq < 30:
            mag_diff_all = np.abs(mag_AB_norm - mag_C_norm)
            freq_weight = 1.0 / (1.0 + np.exp(-0.05 * (f_low - 80)))
            weighted_diff = mag_diff_all * freq_weight
            min_idx_weighted = np.argmin(weighted_diff)
            crossover_freq = f_low[min_idx_weighted]
    else:
        mag_diff = np.abs(mag_AB_norm - mag_C_norm)
        min_idx = np.argmin(mag_diff)
        crossover_freq = f_low[min_idx]
    
    # Clip al rango típico de crossover para subwoofers
    crossover_freq = np.clip(crossover_freq, 50, 120)
    
    return crossover_freq

def calculate_subwoofer_delay(f, mag_AB, phase_AB, mag_C, phase_C, crossover_freq):
    """Calcula el delay óptimo para el subwoofer basado en la frecuencia de cruce."""
    idx = np.argmin(np.abs(f - crossover_freq))
    
    phase_AB_at_crossover = phase_AB[idx]
    phase_C_at_crossover = phase_C[idx]
    
    phase_AB_norm = phase_AB_at_crossover % 360
    phase_C_norm = phase_C_at_crossover % 360
    
    phase_diff = phase_AB_norm - phase_C_norm
    if phase_diff > 180:
        phase_diff -= 360
    elif phase_diff < -180:
        phase_diff += 360
    
    delay_ms = (phase_diff / 360.0) * (1000.0 / crossover_freq)
    
    phase_C_inverted = (phase_C_norm + 180) % 360
    phase_diff_inverted = phase_AB_norm - phase_C_inverted
    if phase_diff_inverted > 180:
        phase_diff_inverted -= 360
    elif phase_diff_inverted < -180:
        phase_diff_inverted += 360
    
    delay_ms_inverted = (phase_diff_inverted / 360.0) * (1000.0 / crossover_freq)
    
    if abs(delay_ms) > 10 and abs(delay_ms_inverted) < abs(delay_ms):
        return delay_ms_inverted, True
    elif abs(delay_ms) <= 10:
        return delay_ms, False
    else:
        if abs(delay_ms_inverted) < abs(delay_ms):
            return delay_ms_inverted, True
        else:
            return delay_ms, False

def load_clean_txt(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    rows = []
    for ln in text.splitlines():
        toks = NUM_RE.findall(ln.strip().replace(",", " "))
        if len(toks) >= 3:
            f, mag, ph = float(toks[0]), float(toks[1]), float(toks[2])
            if f > 0:
                rows.append((f, mag, ph))
    if len(rows) < 10:
        raise ValueError(f"Archivo inválido: {path}")
    arr = np.array(sorted(rows, key=lambda x: x[0]), dtype=np.float64)
    _, idx = np.unique(arr[:, 0], return_index=True)
    arr = arr[np.sort(idx)]
    return arr[:,0], arr[:,1], arr[:,2]

def resample_to_bins(f, mag_db, ph_deg, fmin=FMIN, fmax=FMAX, n_bins=N_BINS):
    """Resample sin unwrap/wrap - igual que en el generador de datos del entrenamiento"""
    f_target = np.logspace(np.log10(fmin), np.log10(fmax), n_bins).astype(np.float32)
    mag_i = np.interp(f_target, f, mag_db).astype(np.float32)
    ph_i = np.interp(f_target, f, ph_deg).astype(np.float32)
    return f_target, mag_i, ph_i

# ==========================================
# 4. FUNCIONES AI / MODELO - PARA NUEVOS MODELOS
# ==========================================
def load_model_by_type(model_type):
    """Carga el modelo según el tipo de fuentes"""
    if model_type == "iguales":
        model_path = MODEL_EQUALES
    elif model_type == "diferentes":
        model_path = MODEL_DIFERENTES
    else:
        raise ValueError(f"Tipo de modelo desconocido: {model_type}")
    
    if not model_path.exists():
        return None
    
    try:
        model = load_model(str(model_path), compile=False)
        return model
    except Exception as e:
        st.error(f"Error cargando modelo {model_type}: {str(e)[:200]}")
        return None

def build_X_for_new_model(R_mag_db, cos_dphi, sin_dphi):
    """Construye entrada para los nuevos modelos (2048, 3)"""
    # Clip R_mag_db como en el entrenamiento
    R_mag_db = np.clip(R_mag_db, -60.0, 60.0).astype(np.float32)
    
    X = np.stack([R_mag_db, cos_dphi, sin_dphi], axis=1)  # (2048, 3)
    return X[None, :, :]  # Añadir dimensión de batch

def predict_with_new_model(model, X):
    """Predicción con los nuevos modelos (4 salidas)"""
    out_delay_bin, out_delay_res_ms, out_gain_db, out_pol = model.predict(X, verbose=0)
    
    # Procesar delay (bin + residual)
    bin_idx = np.argmax(out_delay_bin[0, :])
    delay_bin_ms = bin_idx * 0.5 - 30.0  # bins de ±30ms con paso 0.5ms
    delay_res_ms = out_delay_res_ms[0, 0]
    delay_ms = delay_bin_ms + delay_res_ms
    
    # Ganancia
    gain_db = out_gain_db[0, 0]
    
    # Polaridad
    pol = np.argmax(out_pol[0, :])
    
    return float(delay_ms), float(gain_db), int(pol)

def get_ai_recommendation_AB(Am, Ap, Bm, Bp, same_file):
    """Obtiene recomendación de IA para A-B usando el modelo correcto"""
    # Calcular características de entrada
    R_mag_db = Bm - Am
    dphi_rad = np.deg2rad((Bp - Ap + 180.0) % 360.0 - 180.0)
    cos_dphi = np.cos(dphi_rad)
    sin_dphi = np.sin(dphi_rad)
    
    # Seleccionar modelo
    model_type = "iguales" if same_file else "diferentes"
    model = load_model_by_type(model_type)
    
    if model is None:
        return None
    
    # Construir entrada y predecir
    X = build_X_for_new_model(R_mag_db, cos_dphi, sin_dphi)
    delay, gain, pol = predict_with_new_model(model, X)
    
    return {
        'delay': delay,
        'gain': gain,
        'pol': pol,
        'model_type': model_type
    }

def get_dsp_recommendation_C(f, Sum_mag, Sum_ph, C_mag, C_ph):
    """Calcula recomendación DSP para subwoofer"""
    try:
        crossover_freq = find_crossover_frequency(f, Sum_mag, C_mag)
        delay, pol = calculate_subwoofer_delay(f, Sum_mag, Sum_ph, C_mag, C_ph, crossover_freq)
        
        # Para subwoofer, el gain se calcula para igualar niveles en la frecuencia de cruce
        idx = np.argmin(np.abs(f - crossover_freq))
        gain = Sum_mag[idx] - C_mag[idx]
        
        return {
            'delay': delay,
            'gain': gain,
            'pol': pol,
            'crossover_freq': crossover_freq,
            'method': 'DSP'
        }
    except Exception as e:
        return None

def get_ai_recommendation_C(Sum_mag, Sum_ph, C_mag, C_ph, same_as_AB):
    """Obtiene recomendación para fuente C usando el modelo correcto"""
    model_type = "iguales" if same_as_AB else "diferentes"
    model = load_model_by_type(model_type)
    
    if model is None:
        return None
    
    # Calcular características de entrada (C vs Suma A+B)
    R_mag_db = C_mag - Sum_mag
    dphi_rad = np.deg2rad((C_ph - Sum_ph + 180.0) % 360.0 - 180.0)
    cos_dphi = np.cos(dphi_rad)
    sin_dphi = np.sin(dphi_rad)
    
    X = build_X_for_new_model(R_mag_db, cos_dphi, sin_dphi)
    delay, gain, pol = predict_with_new_model(model, X)
    
    return {
        'delay': delay,
        'gain': gain,
        'pol': pol,
        'model_type': model_type,
        'method': 'AI'
    }

# ==========================================
# 5. ANÁLISIS AUTOMÁTICO MEJORADO
# ==========================================
def analizar_fuente_detallado(f, mag, ph, nombre):
    """Análisis automático detallado de una fuente individual"""
    energia_bajas = np.mean(mag[(f >= 20) & (f <= 200)])
    energia_medias = np.mean(mag[(f > 200) & (f <= 2000)])
    energia_altas = np.mean(mag[(f > 2000) & (f <= 20000)])
    
    if energia_bajas > (energia_medias + 10) and energia_bajas > (energia_altas + 15):
        tipo = "**Subwoofer** (respuesta predominante en bajas frecuencias < 200 Hz)"
    elif energia_altas > (energia_bajas + 15) and energia_altas > (energia_medias + 10):
        tipo = "**Driver de compresión / HF** (respuesta predominante en altas frecuencias > 2 kHz)"
    elif abs(energia_bajas - energia_altas) < 10 and energia_medias > (energia_bajas - 5):
        tipo = "**Fuente de Rango Completo** (respuesta balanceada en todo el espectro)"
    else:
        tipo = "**Fuente especializada** (respuesta espectral particular)"
    
    ph_mean = np.mean(ph[(f > 100) & (f < 5000)])
    ph_std = np.std(ph[(f > 100) & (f < 5000)])
    
    if abs(ph_mean) < 45 and ph_std < 90:
        estado_fase = "**Polaridad estándar** (fase centrada alrededor de 0° con coherencia)"
    elif abs(abs(ph_mean) - 180) < 45 and ph_std < 90:
        estado_fase = "**Inversión de polaridad detectada** (fase centrada alrededor de 180°)"
    elif ph_std > 120:
        estado_fase = "**Fase altamente variable** (posible problema de medición o alineación)"
    else:
        estado_fase = "**Fase dentro de rangos normales**"
    
    umbral = np.max(mag) - 10
    idx_utiles = np.where(mag >= umbral)[0]
    if len(idx_utiles) > 0:
        f_min_util = f[idx_utiles[0]]
        f_max_util = f[idx_utiles[-1]]
        rango_util = f"**{f_min_util:.0f} Hz - {f_max_util:.0f} Hz**"
    else:
        rango_util = "No determinado"
    
    peaks = []
    for i in range(1, len(mag)-1):
        if mag[i] > mag[i-1] and mag[i] > mag[i+1] and mag[i] > np.max(mag) - 6:
            peaks.append((f[i], mag[i] - np.mean(mag)))
    
    if peaks:
        peaks_sorted = sorted(peaks, key=lambda x: x[1], reverse=True)[:3]
        picos_texto = "Picos significativos: " + ", ".join([f"{freq:.0f} Hz (+{db:.1f} dB)" for freq, db in peaks_sorted])
    else:
        picos_texto = "Sin picos resonantes significativos"
    
    reporte = f"""
    ### Análisis Automático: {nombre}
    
    **Tipo de Fuente:** {tipo}
    
    **Estado de Fase:** {estado_fase}
    
    **Rango Útil Efectivo:** {rango_util}
    
    **Características Espectrales:**
    - Nivel promedio bajas frecuencias (20-200 Hz): **{energia_bajas:.1f} dB**
    - Nivel promedio medias frecuencias (200-2000 Hz): **{energia_medias:.1f} dB**
    - Nivel promedio altas frecuencias (2-20 kHz): **{energia_altas:.1f} dB**
    - {picos_texto}
    
    **Observaciones:**
    {generar_observaciones_fuente(tipo, estado_fase, rango_util)}
    """
    
    return reporte

def generar_observaciones_fuente(tipo, estado_fase, rango_util):
    observaciones = []
    
    if "Subwoofer" in tipo:
        observaciones.append("• Esta fuente está optimizada para reproducir frecuencias graves.")
        observaciones.append("• Requiere alineación cuidadosa de fase con los tops para evitar cancelaciones.")
    elif "HF" in tipo or "compresión" in tipo:
        observaciones.append("• Atención a la directividad en altas frecuencias.")
        observaciones.append("• Verificar cobertura y ángulo de dispersión.")
    elif "Rango Completo" in tipo:
        observaciones.append("• Fuente versátil para aplicaciones generales.")
        observaciones.append("• Verificar respuesta plana en el rango vocal (200 Hz - 2 kHz).")
    
    if "Inversión" in estado_fase:
        observaciones.append("• Se recomienda verificar conexiones eléctricas.")
        observaciones.append("• Considerar inversión de polaridad para alineación con otras fuentes.")
    
    if "variable" in estado_fase:
        observaciones.append("• La fase inconsistente puede indicar problemas de medición.")
        observaciones.append("• Verificar posición del micrófono y condiciones acústicas.")
    
    return "\n".join(observaciones)

def analizar_comparacion_detallada(f, magA, phA, magB, phB, nombreA, nombreB):
    diff_mag_media = np.mean(np.abs(magA - magB))
    diff_mag_max = np.max(np.abs(magA - magB))
    
    if diff_mag_media < 1.5:
        comp_mag = f"**Niveles muy similares** (diferencia promedio: {diff_mag_media:.1f} dB)"
        nivel_obs = "Las fuentes tienen niveles prácticamente idénticos (Matched Level)."
    elif diff_mag_media < 6.0:
        comp_mag = f"**Diferencias moderadas** (diferencia promedio: {diff_mag_media:.1f} dB)"
        nivel_obs = f"Existen diferencias de nivel moderadas entre {nombreA} y {nombreB}."
    else:
        comp_mag = f"**Diferencias significativas** (diferencia promedio: {diff_mag_media:.1f} dB)"
        nivel_obs = f"Hay una diferencia de nivel considerable entre {nombreA} y {nombreB}."
    
    diff_ph = np.abs(phA - phB)
    diff_ph = np.minimum(diff_ph, 360 - diff_ph)
    diff_ph_media = np.mean(diff_ph)
    diff_ph_max = np.max(diff_ph)
    
    limit = np.max([np.max(magA), np.max(magB)]) - 15
    overlap_idx = (magA > limit) & (magB > limit)
    
    if np.any(overlap_idx):
        cancel_idxs = np.where((diff_ph > 140) & overlap_idx)[0]
        if len(cancel_idxs) > 0:
            f_cancel = f[cancel_idxs[len(cancel_idxs)//2]]
            ph_diff_at_cancel = diff_ph[cancel_idxs[len(cancel_idxs)//2]]
            comp_ph = f"**ALERTA CANCELACIÓN** ({ph_diff_at_cancel:.0f}° a {f_cancel:.0f} Hz)"
            fase_obs = f"**ALERTA:** Diferencias de fase críticas (>140°) detectadas alrededor de **{f_cancel:.0f} Hz**. Se espera 'filtro de peine' y cancelación significativa."
        else:
            if diff_ph_media < 45:
                comp_ph = f"**Fase bien alineada** (diferencia promedio: {diff_ph_media:.1f}°)"
                fase_obs = "La coherencia de fase es excelente; se espera suma constructiva."
            elif diff_ph_media < 90:
                comp_ph = f"**Fase moderadamente alineada** (diferencia promedio: {diff_ph_media:.1f}°)"
                fase_obs = "La coherencia de fase es aceptable; puede haber pequeñas interferencias."
            else:
                comp_ph = f"**Fase poco alineada** (diferencia promedio: {diff_ph_media:.1f}°)"
                fase_obs = "Existen diferencias de fase considerables que pueden causar interferencias."
    else:
        comp_ph = "**Sin superposición significativa**"
        fase_obs = "Las fuentes no superponen su rango útil significativamente."
    
    if "ALERTA" in comp_ph:
        recomendacion = "**Recomendación prioritaria:** Ajustar delay o polaridad para reducir diferencias de fase."
    elif diff_mag_media > 6.0:
        recomendacion = "**Recomendación:** Ecualizar para igualar niveles antes de ajustar fase."
    elif diff_ph_media < 45 and diff_mag_media < 3.0:
        recomendacion = "**Configuración óptima:** Las fuentes están bien alineadas."
    else:
        recomendacion = "**Recomendación:** Ajustes menores de delay y ganancia para optimizar."
    
    reporte = f"""
    ### ANÁLISIS COMPARATIVO
    
    **Magnitud:**
    {comp_mag}
    - Diferencia máxima: {diff_mag_max:.1f} dB
    {nivel_obs}
    
    **Fase:**
    {comp_ph}
    - Diferencia máxima: {diff_ph_max:.0f}°
    {fase_obs}
    
    **{recomendacion}**
    
    **De la comparación podemos identificar:**
    """
    
    return reporte

def analizar_mejoras_ia(f, mag_initial, mag_optimized, delay_error=None):
    """Analiza mejoras de forma detallada con análisis específico de IA"""
    # Calcular diferencias
    diff = mag_optimized - mag_initial
    
    # Análisis por rangos de frecuencia
    frec_ranges = {
        "Subgraves (20-80 Hz)": (20, 80),
        "Graves (80-250 Hz)": (80, 250),
        "Medio Graves (250-500 Hz)": (250, 500),
        "Medios (500-2000 Hz)": (500, 2000),
        "Medio Agudos (2k-5k Hz)": (2000, 5000),
        "Agudos (5k-20k Hz)": (5000, 20000)
    }
    
    analysis = "### ANÁLISIS DE LA OPTIMIZACIÓN\n\n"
    
    # Análisis por rangos de frecuencia
    mejora_por_rango = []
    for nombre_rango, (f_min, f_max) in frec_ranges.items():
        mask = (f >= f_min) & (f <= f_max)
        if np.any(mask):
            mejora_promedio = np.mean(diff[mask])
            mejora_max = np.max(diff[mask]) if np.any(diff[mask] > 0) else 0
            mejora_min = np.min(diff[mask]) if np.any(diff[mask] < 0) else 0
            
            if mejora_promedio > 3:
                simbolo = "✅"
                desc = f"**Mejora significativa** (+{mejora_promedio:.1f} dB promedio)"
            elif mejora_promedio > 1:
                simbolo = "⚠️"
                desc = f"**Mejora moderada** (+{mejora_promedio:.1f} dB promedio)"
            elif mejora_promedio > 0:
                simbolo = "↗️"
                desc = f"**Mejora leve** (+{mejora_promedio:.1f} dB promedio)"
            else:
                simbolo = "➖"
                desc = f"**Sin mejora** ({mejora_promedio:.1f} dB promedio)"
            
            if mejora_max > 5:
                desc += f" | Pico: +{mejora_max:.1f} dB"
            
            analysis += f"{simbolo} **{nombre_rango}**: {desc}\n"
            mejora_por_rango.append((nombre_rango, mejora_promedio))
    
    # Resumen general mejorado
    mejora_total = np.mean(diff)
    std_mejora = np.std(diff)
    
    analysis += "\n### RESUMEN DE LA OPTIMIZACIÓN\n\n"
    
    if mejora_total > 3 and std_mejora < 2:
        analysis += "✅ **Resultado**: Optimización muy efectiva con mejora uniforme en todo el espectro.\n"
    elif mejora_total > 3:
        analysis += "⚠️ **Resultado**: Mejora significativa pero con variaciones entre rangos frecuenciales.\n"
    elif mejora_total > 1:
        analysis += "↗️ **Resultado**: Mejora moderada, se han corregido algunos problemas de alineación.\n"
    elif mejora_total > 0:
        analysis += "➖ **Resultado**: Mejora mínima, posiblemente solo ajustes finos.\n"
    else:
        analysis += "❌ **Resultado**: No se observan mejoras significativas.\n"
    
    # Si hay error de delay, incluirlo en contexto
    if delay_error is not None:
        analysis += f"\n**Ajuste temporal aplicado**: {delay_error:.2f} ms\n"
        if abs(delay_error) < 1:
            analysis += "**Nota**: Ajuste de delay muy fino, probablemente para corrección de fase.\n"
        elif abs(delay_error) < 5:
            analysis += "**Nota**: Ajuste de delay moderado, típico para alineación de drivers cercanos.\n"
        else:
            analysis += "**Nota**: Ajuste de delay significativo, posible alineación de fuentes distantes.\n"
    
    return analysis

def analizar_mejoras_fuente_C(f, mag_initial, mag_optimized, fuente_nombre="C", metodo="DSP"):
    """Análisis específico para fuente C (similar al de IA pero con contexto específico)"""
    diff = mag_optimized - mag_initial
    
    analysis = f"### ANÁLISIS DE LA INTEGRACIÓN DE {fuente_nombre}\n\n"
    
    # Análisis por rangos más específico para subwoofers
    if "SUB" in fuente_nombre.upper() or "SUBWOOFER" in fuente_nombre.upper():
        frec_ranges = {
            "Subgraves profundos (20-40 Hz)": (20, 40),
            "Subgraves (40-80 Hz)": (40, 80),
            "Graves bajos (80-120 Hz)": (80, 120),
            "Graves medios (120-250 Hz)": (120, 250),
        }
    else:
        frec_ranges = {
            "Graves (80-250 Hz)": (80, 250),
            "Medio Graves (250-500 Hz)": (250, 500),
            "Medios (500-1000 Hz)": (500, 1000),
            "Medios altos (1k-2k Hz)": (1000, 2000),
            "Agudos medios (2k-5k Hz)": (2000, 5000),
            "Agudos altos (5k-20k Hz)": (5000, 20000)
        }
    
    # Análisis por rangos
    for nombre_rango, (f_min, f_max) in frec_ranges.items():
        mask = (f >= f_min) & (f <= f_max)
        if np.any(mask):
            mejora_promedio = np.mean(diff[mask])
            
            if mejora_promedio > 3:
                simbolo = "✅"
                desc = f"**Integración excelente** (+{mejora_promedio:.1f} dB)"
            elif mejora_promedio > 1:
                simbolo = "⚠️"
                desc = f"**Integración buena** (+{mejora_promedio:.1f} dB)"
            elif mejora_promedio > 0:
                simbolo = "↗️"
                desc = f"**Integración aceptable** (+{mejora_promedio:.1f} dB)"
            elif mejora_promedio > -2:
                simbolo = "➖"
                desc = f"**Integración neutra** ({mejora_promedio:.1f} dB)"
            else:
                simbolo = "❌"
                desc = f"**Problemas de integración** ({mejora_promedio:.1f} dB)"
            
            analysis += f"{simbolo} **{nombre_rango}**: {desc}\n"
    
    # Resumen final
    mejora_total = np.mean(diff)
    
    analysis += "\n### VALORACIÓN FINAL\n\n"
    
    if mejora_total > 2:
        analysis += f"**Resultado con {metodo}**: ✅ **INTEGRACIÓN EXITOSA**\n"
        analysis += f"La fuente {fuente_nombre} se ha integrado eficazmente al sistema.\n"
    elif mejora_total > 0:
        analysis += f"**Resultado con {metodo}**: ⚠️ **INTEGRACIÓN PARCIAL**\n"
        analysis += f"La fuente {fuente_nombre} muestra mejoras pero podría optimizarse más.\n"
    else:
        analysis += f"**Resultado con {metodo}**: ❌ **PROBLEMAS DE INTEGRACIÓN**\n"
        analysis += f"Revisar la configuración de la fuente {fuente_nombre}.\n"
    
    return analysis

# ==========================================
# 6. VISUALIZACIÓN
# ==========================================
def generar_diagrama_neon(posA, posB, use_third, source_type, posC):
    """Genera diagrama limpio solo con letras A, B, C y micrófono rojo"""
    fig, ax = plt.subplots(figsize=(10, 5))
    
    def dibujar_cabina(pos, ancho=2, alto=3, color='#00ffff'):
        x, y = pos
        puntos = np.array([
            [x - ancho/2, y],
            [x - ancho/4, y + alto],
            [x + ancho/4, y + alto],
            [x + ancho/2, y]
        ])
        poly = plt.Polygon(puntos, closed=True, facecolor=color, alpha=0.3, edgecolor=color, linewidth=2)
        ax.add_patch(poly)
        return puntos
    
    dibujar_cabina(posA, color='#00ffff')
    dibujar_cabina(posB, color='#00ffff')
    
    ax.text(posA[0], posA[1] + 1.5, 'A', ha='center', va='center', color='white', 
            fontsize=24, fontweight='bold')
    ax.text(posB[0], posB[1] + 1.5, 'B', ha='center', va='center', color='white', 
            fontsize=24, fontweight='bold')
    
    if use_third:
        if source_type == "Subwoofer":
            xc, yc = posC
            rect = plt.Rectangle((xc - 1.5, yc), 3, 1.5, facecolor='#ff00ff', alpha=0.4, 
                                edgecolor='#ff00ff', linewidth=2)
            ax.add_patch(rect)
            ax.text(xc, yc + 0.75, 'C', ha='center', va='center', color='white', 
                   fontsize=24, fontweight='bold')
        else:
            dibujar_cabina(posC, color='#ffff00')
            ax.text(posC[0], posC[1] + 1.5, 'C', ha='center', va='center', color='white', 
                   fontsize=24, fontweight='bold')
    
    ax.scatter(0, 0, s=300, c='red', marker='o', edgecolors='white', linewidth=2, zorder=10)
    
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-15, 15)
    ax.set_ylim(-2, 20)
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_title("DIAGRAMA DE DISPOSICIÓN", fontweight='bold', pad=20)
    
    return fig

def plot_fuente_bonita(f, mag, ph, title, color="#00ffff"):
    """Crea gráficas interactivas y atractivas para una fuente individual"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            f"<b>RESPUESTA EN MAGNITUD: {title}</b>",
            f"<b>RESPUESTA EN FASE: {title}</b>"
        ),
        vertical_spacing=0.18,
        row_heights=[0.5, 0.5]
    )
    
    fig.add_trace(
        go.Scatter(
            x=f, y=mag,
            mode='lines',
            line=dict(color=color, width=3),
            name='Magnitud',
            showlegend=False,
            hovertemplate='Frec: %{x:.0f} Hz<br>Mag: %{y:.1f} dB<extra></extra>'
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=f, y=ph,
            mode='lines',
            line=dict(color=color, width=2.5, dash='solid'),
            name='Fase',
            showlegend=False,
            hovertemplate='Frec: %{x:.0f} Hz<br>Fase: %{y:.1f}°<extra></extra>'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=750,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=50, r=30, t=100, b=150)
    )
    
    fig.update_xaxes(
        title_text="Frecuencia (Hz)",
        type="log",
        gridcolor="#333",
        showgrid=True,
        row=1, col=1
    )
    fig.update_yaxes(
        title_text="Magnitud (dB)",
        gridcolor="#444",
        showgrid=True,
        row=1, col=1
    )
    
    fig.update_xaxes(
        title_text="Frecuencia (Hz)",
        type="log",
        gridcolor="#333",
        showgrid=True,
        row=2, col=1
    )
    fig.update_yaxes(
        title_text="Fase (°)",
        gridcolor="#444",
        showgrid=True,
        range=[-200, 200],
        tickvals=[-180, -135, -90, -45, 0, 45, 90, 135, 180],
        row=2, col=1
    )
    
    fig.add_hline(y=0, line_dash="dot", line_color="#666", opacity=0.5, row=2, col=1)
    fig.add_hline(y=180, line_dash="dot", line_color="#f66", opacity=0.5, row=2, col=1)
    fig.add_hline(y=-180, line_dash="dot", line_color="#f66", opacity=0.5, row=2, col=1)
    
    return fig

def plot_comparison_mag_phase(f, series, title_mag, title_ph=None):
    """Crea dos gráficas: una de magnitud y otra de fase, para comparar múltiples series"""
    if title_ph is None:
        title_ph = title_mag.replace("MAGNITUD", "FASE")
    
    fig_mag = go.Figure()
    
    for mag, ph, label, color in series:
        fig_mag.add_trace(go.Scatter(
            x=f, y=mag,
            mode='lines',
            line=dict(color=color, width=3),
            name=f"{label}",
            hovertemplate='Frec: %{x:.0f} Hz<br>Mag: %{y:.1f} dB<extra></extra>'
        ))
    
    fig_mag.update_layout(
        title=f"<b>{title_mag}</b>",
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=50, r=30, t=80, b=135)
    )
    
    fig_mag.update_xaxes(
        title_text="Frecuencia (Hz)",
        type="log",
        gridcolor="#333",
        showgrid=True
    )
    
    fig_mag.update_yaxes(
        title_text="Magnitud (dB)",
        gridcolor="#444",
        showgrid=True
    )
    
    fig_ph = go.Figure()
    
    for mag, ph, label, color in series:
        fig_ph.add_trace(go.Scatter(
            x=f, y=ph,
            mode='lines',
            line=dict(color=color, width=2.5, dash='solid'),
            name=f"{label}",
            hovertemplate='Frec: %{x:.0f} Hz<br>Fase: %{y:.1f}°<extra></extra>'
        ))
    
    fig_ph.update_layout(
        title=f"<b>{title_ph}</b>",
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        hovermode="x unified",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.28,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=50, r=30, t=80, b=135)
    )
    
    fig_ph.update_xaxes(
        title_text="Frecuencia (Hz)",
        type="log",
        gridcolor="#333",
        showgrid=True
    )
    
    fig_ph.update_yaxes(
        title_text="Fase (°)",
        gridcolor="#444",
        showgrid=True,
        range=[-200, 200],
        tickvals=[-180, -135, -90, -45, 0, 45, 90, 135, 180]
    )
    
    fig_ph.add_hline(y=0, line_dash="dot", line_color="#666", opacity=0.5)
    fig_ph.add_hline(y=180, line_dash="dot", line_color="#f66", opacity=0.5)
    fig_ph.add_hline(y=-180, line_dash="dot", line_color="#f66", opacity=0.5)
    
    return fig_mag, fig_ph

def create_time_of_arrival_chart():
    src_a = np.array([-2.0, 8.0])
    src_b = np.array([2.5, 6.5])
    mic = np.array([0.0, 0.0])
    dist_a = float(np.linalg.norm(src_a - mic))
    dist_b = float(np.linalg.norm(src_b - mic))
    time_a = dist_a / SOUND_SPEED * 1000.0
    time_b = dist_b / SOUND_SPEED * 1000.0
    delta_t = abs(time_b - time_a)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[src_a[0], mic[0]],
        y=[src_a[1], mic[1]],
        mode="lines",
        line=dict(color="#00ffff", width=4),
        name="Trayectoria A",
        hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=[src_b[0], mic[0]],
        y=[src_b[1], mic[1]],
        mode="lines",
        line=dict(color="#ff00ff", width=4),
        name="Trayectoria B",
        hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=[src_a[0], src_b[0], mic[0]],
        y=[src_a[1], src_b[1], mic[1]],
        mode="markers+text",
        marker=dict(size=[20, 20, 18], color=["#00ffff", "#ff00ff", "#ff5555"], line=dict(color="white", width=1)),
        text=["Fuente A", "Fuente B", "Micrófono"],
        textposition=["top center", "top center", "bottom center"],
        name="Elementos",
        hoverinfo="skip"
    ))
    fig.add_annotation(
        x=-3.5,
        y=3.0,
        text=f"dA = {dist_a:.2f} m<br>tA = {time_a:.2f} ms",
        showarrow=False,
        font=dict(color="#dffcff")
    )
    fig.add_annotation(
        x=3.6,
        y=2.4,
        text=f"dB = {dist_b:.2f} m<br>tB = {time_b:.2f} ms",
        showarrow=False,
        font=dict(color="#ffd6ff")
    )
    fig.add_annotation(
        x=10,
        y=8,
        text=f"Δt ≈ {delta_t:.2f} ms",
        showarrow=False,
        font=dict(color="#fff799", size=14)
    )
    fig.update_layout(
        title="<b>Vista superior de propagación hacia el punto de medición</b>",
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=30, t=80, b=80),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,10,20,0.35)"
        )
    )
    fig.update_xaxes(title_text="Posición lateral X (m)", gridcolor="#333", zerolinecolor="#666", range=[-5, 5])
    fig.update_yaxes(title_text="Profundidad Y (m)", gridcolor="#444", zerolinecolor="#666", range=[-1, 10], scaleanchor="x", scaleratio=1)
    return fig

def create_phase_delay_chart(delay_ms=2.0):
    f = np.logspace(np.log10(20), np.log10(2000), 500)
    phase_deg = -360.0 * f * (delay_ms / 1000.0)
    phase_wrapped = ((phase_deg + 180.0) % 360.0) - 180.0
    delay_ms_2 = 4.0
    phase_deg_2 = -360.0 * f * (delay_ms_2 / 1000.0)
    phase_wrapped_2 = ((phase_deg_2 + 180.0) % 360.0) - 180.0
    reference = np.zeros_like(f)
    sample_freqs = np.array([63.0, 125.0, 250.0, 500.0, 1000.0], dtype=np.float32)
    sample_phase = ((-360.0 * sample_freqs * (delay_ms / 1000.0) + 180.0) % 360.0) - 180.0
    sample_phase_2 = ((-360.0 * sample_freqs * (delay_ms_2 / 1000.0) + 180.0) % 360.0) - 180.0

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Fase medida", "Diferencia de fase")
    )
    fig.add_trace(go.Scatter(
        x=f, y=reference,
        mode="lines",
        line=dict(color="#888888", width=2, dash="dash"),
        name="Referencia 0 ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Fase: 0°<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=f, y=phase_wrapped,
        mode="lines",
        line=dict(color="#00ffff", width=3),
        name=f"Retardo {delay_ms:.1f} ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Fase envuelta: %{y:.1f}°<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=f, y=phase_wrapped_2,
        mode="lines",
        line=dict(color="#ff00ff", width=3),
        name=f"Retardo {delay_ms_2:.1f} ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Fase envuelta: %{y:.1f}°<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sample_freqs, y=sample_phase,
        mode="markers",
        marker=dict(size=8, color="#00ffff"),
        name=f"Lecturas {delay_ms:.1f} ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Fase: %{y:.1f}°<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=sample_freqs, y=sample_phase_2,
        mode="markers",
        marker=dict(size=8, color="#ff00ff"),
        name=f"Lecturas {delay_ms_2:.1f} ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Fase: %{y:.1f}°<extra></extra>"
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=f, y=-phase_deg,
        mode="lines",
        line=dict(color="#ffcc00", width=3),
        name=f"Δ fase {delay_ms:.1f} ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Diferencia: %{y:.1f}°<extra></extra>"
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=f, y=-phase_deg_2,
        mode="lines",
        line=dict(color="#ff6699", width=3, dash="dash"),
        name=f"Δ fase {delay_ms_2:.1f} ms",
        hovertemplate="Frecuencia: %{x:.0f} Hz<br>Diferencia: %{y:.1f}°<extra></extra>"
    ), row=2, col=1)
    fig.update_layout(
        title=f"<b>Comparación del efecto de {delay_ms:.1f} ms y {delay_ms_2:.1f} ms sobre la fase</b>",
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=150, t=90, b=60),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="left",
            x=1.02,
            bgcolor="rgba(0,10,20,0.35)"
        )
    )
    fig.update_xaxes(title_text="Frecuencia (Hz)", type="log", gridcolor="#333", row=2, col=1)
    fig.update_xaxes(type="log", gridcolor="#333", row=1, col=1)
    fig.update_yaxes(title_text="Fase (°)", gridcolor="#444", range=[-190, 190], tickvals=[-180, -90, 0, 90, 180], row=1, col=1)
    fig.update_yaxes(title_text="Δ fase acumulada (°)", gridcolor="#444", row=2, col=1)
    fig.add_hline(y=0, line_dash="dot", line_color="#666", opacity=0.6, row=1, col=1)
    fig.add_hline(y=180, line_dash="dot", line_color="#f66", opacity=0.5, row=1, col=1)
    fig.add_hline(y=-180, line_dash="dot", line_color="#f66", opacity=0.5, row=1, col=1)
    return fig

def create_polarity_chart():
    t = np.linspace(0, 0.04, 900, endpoint=False)
    a = 0.95 * np.sin(2 * np.pi * 95.0 * t)
    b = 0.7 * np.sin(2 * np.pi * 95.0 * t + np.deg2rad(65.0))
    sum_normal = a + b
    sum_inverted = a - b

    fig_signals = go.Figure()
    fig_signals.add_trace(go.Scatter(
        x=t * 1000, y=a,
        mode="lines",
        line=dict(color="#00ffff", width=2),
        name="Señal A",
        hovertemplate="Tiempo: %{x:.1f} ms<br>Amplitud: %{y:.2f}<extra></extra>"
    ))
    fig_signals.add_trace(go.Scatter(
        x=t * 1000, y=b,
        mode="lines",
        line=dict(color="#ff00ff", width=2),
        name="Señal B",
        hovertemplate="Tiempo: %{x:.1f} ms<br>Amplitud: %{y:.2f}<extra></extra>"
    ))
    fig_signals.update_layout(
        title="<b>Señales A y B en el tiempo</b>",
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=30, t=85, b=70),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.24,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,10,20,0.35)"
        )
    )
    fig_signals.update_xaxes(title_text="Tiempo (ms)", gridcolor="#333")
    fig_signals.update_yaxes(title_text="Amplitud relativa", gridcolor="#444")

    fig_sum = go.Figure()
    fig_sum.add_trace(go.Scatter(
        x=t * 1000, y=sum_normal,
        mode="lines",
        line=dict(color="#7dff7d", width=3),
        name="A + B",
        hovertemplate="Tiempo: %{x:.1f} ms<br>Amplitud: %{y:.2f}<extra></extra>"
    ))
    fig_sum.add_trace(go.Scatter(
        x=t * 1000, y=sum_inverted,
        mode="lines",
        line=dict(color="#ffcc00", width=3, dash="dash"),
        name="A + (-B)",
        hovertemplate="Tiempo: %{x:.1f} ms<br>Amplitud: %{y:.2f}<extra></extra>"
    ))
    fig_sum.update_layout(
        title="<b>Comparación de las sumas antes y después de invertir la polaridad en B</b>",
        height=360,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=30, t=85, b=70),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,10,20,0.35)"
        )
    )
    fig_sum.update_xaxes(title_text="Tiempo (ms)", gridcolor="#333")
    fig_sum.update_yaxes(title_text="Amplitud de la suma", gridcolor="#444")
    return fig_signals, fig_sum

def create_superposition_chart():
    fs = 4000
    t = np.linspace(0, 0.04, int(0.04 * fs), endpoint=False)
    freq = 100.0
    p1 = np.sin(2 * np.pi * freq * t)
    p2_constructive = np.sin(2 * np.pi * freq * t)
    p2_destructive = -np.sin(2 * np.pi * freq * t)

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Interferencia constructiva", "Interferencia destructiva")
    )

    for col, second_wave, color_sum in [(1, p2_constructive, "#00ff88"), (2, p2_destructive, "#ff5577")]:
        fig.add_trace(go.Scatter(x=t * 1000, y=p1, mode="lines", line=dict(color="#00ffff", width=2), name="Fuente 1", showlegend=(col == 1)), row=1, col=col)
        fig.add_trace(go.Scatter(x=t * 1000, y=second_wave, mode="lines", line=dict(color="#ff00ff", width=2), name="Fuente 2", showlegend=(col == 1)), row=1, col=col)
        fig.add_trace(go.Scatter(x=t * 1000, y=p1 + second_wave, mode="lines", line=dict(color=color_sum, width=3), name="Suma", showlegend=(col == 1)), row=1, col=col)

    fig.update_layout(
        title="<b>Superposición de presión acústica en el tiempo</b>",
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=30, t=90, b=85),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.16,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(0,10,20,0.35)"
        )
    )
    fig.update_xaxes(title_text="Tiempo (ms)", gridcolor="#333")
    fig.update_yaxes(title_text="Presión relativa", gridcolor="#444")
    return fig

def create_comb_filter_chart(delay_ms=2.5):
    f = np.linspace(20, 2000, 3000)
    dt = delay_ms / 1000.0
    H = 1.0 + np.exp(-1j * 2 * np.pi * f * dt)
    mag_db = 20 * np.log10(np.maximum(np.abs(H), 1e-6))
    first_null = 1.0 / (2.0 * dt)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=f,
        y=mag_db,
        mode="lines",
        line=dict(color="#00ffff", width=3),
        hovertemplate="Frecuencia: %{x:.1f} Hz<br>Magnitud: %{y:.1f} dB<extra></extra>"
    ))
    fig.add_vline(x=first_null, line_dash="dash", line_color="#ff00ff", opacity=0.8)
    fig.add_annotation(
        x=first_null,
        y=np.min(mag_db) + 2,
        text=f"Primera cancelación ≈ {first_null:.0f} Hz",
        showarrow=True,
        arrowcolor="#ff00ff",
        font=dict(color="#ffccff")
    )
    fig.update_layout(
        title=f"<b>Filtro de peine para Δt = {delay_ms:.1f} ms</b>",
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=30, t=70, b=50)
    )
    fig.update_xaxes(title_text="Frecuencia (Hz)", gridcolor="#333")
    fig.update_yaxes(title_text="Magnitud relativa (dB)", gridcolor="#444")
    return fig

def create_spatial_dependency_chart():
    x_positions = np.linspace(-6.0, 6.0, 250)
    src_a = np.array([-2.0, 8.0])
    src_b = np.array([2.0, 8.0])
    freq = 250.0

    dist_a = np.sqrt((x_positions - src_a[0])**2 + src_a[1]**2)
    dist_b = np.sqrt((x_positions - src_b[0])**2 + src_b[1]**2)
    dt = (dist_b - dist_a) / SOUND_SPEED
    H = 1.0 + np.exp(-1j * 2 * np.pi * freq * dt)
    mag_db = 20 * np.log10(np.maximum(np.abs(H), 1e-6))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=mag_db,
        mode="lines",
        line=dict(color="#00ffff", width=3),
        fill="tozeroy",
        fillcolor="rgba(0,255,255,0.15)",
        hovertemplate="Posición: %{x:.1f} m<br>Nivel: %{y:.1f} dB<extra></extra>"
    ))
    fig.update_layout(
        title="<b>Variación espacial de la suma en el área de escucha</b>",
        height=380,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,10,20,0.5)',
        font=dict(color="#e0e0e0", family="Roboto Mono"),
        margin=dict(l=40, r=30, t=70, b=50)
    )
    fig.update_xaxes(title_text="Posición lateral del oyente (m)", gridcolor="#333")
    fig.update_yaxes(title_text="Nivel resultante a 250 Hz (dB)", gridcolor="#444")
    return fig

# ==========================================
# 7. UI Y ESTRUCTURA PRINCIPAL
# ==========================================
@st.cache_data
def build_catalog(clean_dir: Path):
    cat = {}
    if clean_dir.exists():
        for b in sorted([d for d in clean_dir.iterdir() if d.is_dir()]):
            cat[b.name] = {}
            for t in sorted([d for d in b.iterdir() if d.is_dir()]):
                files = sorted(t.rglob("*.txt"))
                if files:
                    cat[b.name][t.name] = {f.stem: f for f in files}
    return cat

def main():
    st.title("OptimLab.IA")
    
    # Construir catálogo
    try:
        catalog = build_catalog(CLEAN_DIR)
        if not catalog:
            st.error("No se encontraron archivos en la base de datos. Verifica la carpeta CLEAN_FILES_NORM o CLEAN_FILES.")
            st.stop()
    except Exception as e:
        st.error(f"Error al cargar el catálogo: {str(e)}")
        st.stop()
    
    # Inicializar variables de sesión
    if 'analysis_started' not in st.session_state:
        st.session_state.analysis_started = False
    if 'ia_recommendation_AB' not in st.session_state:
        st.session_state.ia_recommendation_AB = None
    if 'user_choice_AB' not in st.session_state:
        st.session_state.user_choice_AB = 'initial'
    if 'user_adjustments_AB' not in st.session_state:
        st.session_state.user_adjustments_AB = {
            'delay': 0.0,
            'gain': 0.0,
            'pol': False
        }
    if 'chosen_config_AB' not in st.session_state:
        st.session_state.chosen_config_AB = {
            'delay': 0.0,
            'gain': 0.0,
            'pol': False
        }
    if 'dsp_recommendation_C' not in st.session_state:
        st.session_state.dsp_recommendation_C = None
    if 'user_choice_C' not in st.session_state:
        st.session_state.user_choice_C = 'initial'
    if 'user_adjustments_C' not in st.session_state:
        st.session_state.user_adjustments_C = {
            'delay': 0.0,
            'gain': 0.0,
            'pol': False
        }
    if 'chosen_config_C' not in st.session_state:
        st.session_state.chosen_config_C = {
            'delay': 0.0,
            'gain': 0.0,
            'pol': False
        }
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'theory_stage_completed' not in st.session_state:
        st.session_state.theory_stage_completed = False
    
    # --- A. ETAPA TEÓRICA ---
    st.markdown("""
    <div class='neon-panel'>
        <div class='panel-title'>ETAPA 0 · FUNDAMENTOS PARA LA INTERACCIÓN ENTRE FUENTES ACÚSTICAS</div>
        <p>
        Antes de comenzar el laboratorio de simulación, es necesario comprender qué ocurre cuando varias fuentes acústicas reproducen la misma señal dentro de un sistema de refuerzo sonoro. En aplicaciones reales esto sucede con arreglos principales, front-fills, delays o subwoofers que comparten una región del espectro.
        </p>
        <p>
        En un punto de escucha, el sonido no proviene de una única fuente, sino de la superposición de ondas de presión generadas por todos los elementos del sistema. El resultado depende de la distancia, el tiempo de llegada, la fase, la polaridad y la posición del oyente.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-grid">
        <div class="theory-card">
            <h4>Objetivo</h4>
            <p>Entender cómo se combinan varias fuentes que reproducen la misma señal y cómo esa interacción afecta la respuesta medida.</p>
        </div>
        <div class="theory-card">
            <h4>Idea central</h4>
            <p>La suma entre fuentes no depende solo del nivel: también depende del tiempo de llegada y de la fase en cada frecuencia.</p>
        </div>
        <div class="theory-card">
            <h4>Aplicación</h4>
            <p>Estos principios permiten interpretar mediciones y tomar decisiones de delay, ganancia y polaridad con criterio técnico.</p>
        </div>
        <div class="theory-card">
            <h4>Meta del laboratorio</h4>
            <p>Usar estos conceptos para analizar A, B y una posible fuente C dentro de un escenario interactivo de alineación.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    theory_tabs = st.tabs([
        "Propagación",
        "Tiempo y fase",
        "Suma e interferencia",
        "Filtro de peine",
        "Polaridad y delay",
        "Dependencia espacial"
    ])

    with theory_tabs[0]:
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Propagación del sonido y tiempo de llegada</div>
            <p>
            Cuando un altavoz reproduce una señal, genera variaciones de presión que se propagan a través del aire. En el régimen lineal y para fines de análisis de campo directo, esa propagación puede modelarse como una onda acústica cuya velocidad en condiciones normales se aproxima por <b>c ≈ 343 m/s</b>.
            </p>
            <p>
            Si una fuente se encuentra a una distancia <b>d</b> del punto de medición, el tiempo de llegada del frente de onda puede estimarse a partir del cociente entre distancia recorrida y velocidad de propagación.
            </p>
            <p>
            En un sistema con múltiples fuentes, cada trayecto geométrico suele ser diferente. Por lo tanto, aunque dos altavoces reproduzcan exactamente la misma señal eléctrica, sus contribuciones acústicas no llegan simultáneamente al punto de observación.
            </p>
            <p>
            Esa diferencia de trayecto es el origen físico de la desalineación temporal entre fuentes y constituye la base de muchos fenómenos de interacción. Antes de evaluar ecualización, nivel o procesamiento, es necesario entender la geometría de propagación del sistema.
            </p>
            <p>
            En términos rigurosos, la propagación fija la referencia temporal sobre la cual luego se interpreta la fase relativa entre señales. Si una fuente recorre una trayectoria mayor, la coincidencia temporal se pierde aun cuando no exista ningún retardo digital aplicado.
            </p>
            <p>
            Este principio es especialmente relevante en arreglos distribuidos, sistemas main-fill, configuraciones con delays y combinaciones top-sub, donde pequeñas variaciones geométricas pueden producir diferencias medibles y audibles en la suma total del sistema.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"t = \frac{d}{c}")
        st.latex(r"\Delta t = \frac{\Delta d}{c}")
        st.plotly_chart(create_time_of_arrival_chart(), use_container_width=True)
        st.markdown("""
        <div class="theory-grid">
            <div class="theory-card">
                <h4>Si aumenta d</h4>
                <p>Aumenta el tiempo de llegada. La señal llega más tarde al punto de medición.</p>
            </div>
            <div class="theory-card">
                <h4>Si aumenta Δd</h4>
                <p>Aumenta la diferencia temporal entre fuentes y cambia su relación de fase.</p>
            </div>
            <div class="theory-card">
                <h4>Interpretación práctica</h4>
                <p>Dos altavoces que parecen “juntos” visualmente pueden no estarlo acústicamente en un punto específico del público.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Implicación para la medición</div>
            <p>
            Cuando se realiza una medición, el micrófono no registra únicamente el nivel radiado por cada fuente; registra también la historia de propagación asociada a cada trayecto. En consecuencia, la posición del micrófono determina qué diferencia temporal se está observando realmente.
            </p>
            <p>
            Una variación pequeña de posición puede modificar la relación entre distancias y alterar de forma apreciable el resultado medido, sobre todo cuando varias fuentes comparten el mismo rango espectral y contribuyen con niveles comparables.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with theory_tabs[1]:
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Relación entre tiempo y fase</div>
            <p>
            La fase describe el estado instantáneo de una oscilación periódica dentro de su ciclo. Si dos señales llegan en instantes distintos, la diferencia temporal entre ambas se traduce en una diferencia de fase cuyo valor depende explícitamente de la frecuencia.
            </p>
            <p>
            Un mismo retardo equivale a una fracción pequeña de ciclo a baja frecuencia y a múltiples fracciones de ciclo a frecuencias más altas. Por ello, un delay fijo no produce un desfase uniforme en todo el espectro.
            </p>
            <p>
            Esta distinción es fundamental: el tiempo es una magnitud absoluta, mientras que la fase es una magnitud relativa al periodo. En consecuencia, una misma diferencia temporal puede implicar comportamientos radicalmente distintos en 80 Hz, 500 Hz o 4 kHz.
            </p>
            <p>
            Desde un punto de vista práctico, esto explica por qué no basta con afirmar que una señal fue “adelantada” o “atrasada” sin especificar la banda de análisis. El mismo delay puede mejorar la relación de fase en una región del espectro y deteriorarla en otra.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"\phi(f) = -2 \pi f \Delta t")
        st.latex(r"\phi_{deg}(f) = -360 f \Delta t")
        st.plotly_chart(create_phase_delay_chart(delay_ms=2.0), use_container_width=True)
        st.warning("La gráfica compara una referencia temporal ideal con una señal retrasada y muestra cómo el retardo se manifiesta como pendiente de fase y como incremento acumulado del desfase.")
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Lectura física de la fase</div>
            <p>
            Si dos señales presentan una diferencia de fase cercana a <b>0°</b> en una frecuencia dada, sus contribuciones tienden a sumarse de manera eficiente en esa frecuencia.
            </p>
            <p>
            Si la diferencia se aproxima a <b>180°</b>, las señales tienden a cancelarse. Entre ambos extremos aparecen sumas parciales cuya magnitud depende del ángulo relativo y de la relación de niveles.
            </p>
            <p>
            Por esta razón, una única diferencia temporal puede producir simultáneamente suma favorable en unas frecuencias y cancelación en otras. Ese comportamiento mixto es una consecuencia directa de la dependencia entre fase y frecuencia.
            </p>
            <p>
            En sistemas reales también intervienen filtros, cruces, procesamiento interno y características electroacústicas del transductor. Todo ello modifica la fase de cada fuente incluso antes de considerar la contribución geométrica de la distancia.
            </p>
            <p>
            Por esa razón, la interpretación de la fase debe hacerse de forma contextual: una pendiente puede estar asociada a un retardo, pero también puede combinarse con el comportamiento propio del sistema bajo análisis.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with theory_tabs[2]:
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Superposición de ondas e interferencia</div>
            <p>
            Cuando dos ondas llegan al mismo punto, las presiones se suman. Si las fases son similares, la suma es constructiva. Si son opuestas, aparecen cancelaciones parciales o totales.
            </p>
            <p>
            Este fenómeno se describe mediante el principio de superposición: el campo acústico total es la suma de los aportes individuales de cada fuente. En audio, no “gana” una fuente sobre la otra; ambas contribuyen al resultado final.
            </p>
            <p>
            Cuando se habla de suma entre fuentes en refuerzo sonoro, lo que realmente se está sumando es la presión acústica que cada una produce en el punto de observación. El resultado puede ser mayor, menor o simplemente diferente al esperado intuitivamente si no se considera la fase.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"p_{total}(t) = p_1(t) + p_2(t)")
        st.plotly_chart(create_superposition_chart(), use_container_width=True)
        st.success("En la práctica, el espectro final suele contener zonas con refuerzo y otras con cancelación.")
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Constructiva vs destructiva</div>
            <p>
            La interferencia constructiva ocurre cuando las variaciones de presión de ambas señales tienen signo similar en el mismo instante. La destructiva ocurre cuando una aumenta la presión mientras la otra la reduce.
            </p>
            <p>
            En señales reales y de banda ancha, esto no sucede igual en todo el espectro. Por eso las mediciones muestran respuestas complejas y no una simple suma uniforme.
            </p>
            <p>
            Esto explica por qué dos cajas que por separado “suenan bien” pueden generar una respuesta irregular al trabajar juntas. El problema no necesariamente está en cada fuente individual, sino en la forma en que ambas interactúan en el espacio.
            </p>
            <p>
            Comprender esta diferencia entre comportamiento individual y comportamiento combinado es clave para interpretar correctamente una medición y decidir si hace falta ajustar delay, polaridad, nivel o incluso replantear la geometría del sistema.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="theory-grid">
            <div class="theory-card">
                <h4>0° aprox.</h4>
                <p>Tendencia a suma eficiente.</p>
            </div>
            <div class="theory-card">
                <h4>90° aprox.</h4>
                <p>Suma parcial; no hay máxima coherencia.</p>
            </div>
            <div class="theory-card">
                <h4>180° aprox.</h4>
                <p>Tendencia a cancelación.</p>
            </div>
            <div class="theory-card">
                <h4>Resultado real</h4>
                <p>Combinación simultánea de refuerzos y cancelaciones según la frecuencia.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with theory_tabs[3]:
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Filtro de peine</div>
            <p>
            Si la diferencia temporal entre dos señales es constante, la relación de fase cambia con la frecuencia y aparecen picos y valles periódicos en la magnitud. Este patrón se conoce como <b>filtro de peine</b>.
            </p>
            <p>
            El nombre proviene de la forma de la curva, que presenta múltiples dientes o muescas. Este es uno de los fenómenos más típicos cuando dos fuentes cubren la misma banda y llegan con un pequeño desfase temporal.
            </p>
            <p>
            Cuanto mayor es la diferencia temporal, más juntas aparecen las cancelaciones en frecuencia. Cuanto menor es el retardo, más separadas aparecen esas muescas.
            </p>
            <p>
            Este fenómeno no debe entenderse como una curiosidad gráfica, sino como una consecuencia directa de la coexistencia entre suma y cancelación a lo largo del espectro. Es uno de los indicios más claros de que dos señales similares están llegando desalineadas en el tiempo.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"f_n = \frac{2n + 1}{2 \Delta t}")
        st.plotly_chart(create_comb_filter_chart(delay_ms=2.5), use_container_width=True)
        st.info("El filtro de peine explica por qué un sistema puede sonar muy diferente con pequeños cambios de distancia o delay.")
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Interpretación de la fórmula de cancelaciones</div>
            <p>
            La expresión de <b>f<sub>n</sub></b> permite estimar las frecuencias donde se esperan las cancelaciones principales. No reemplaza una medición real, pero ofrece una referencia muy útil para anticipar el comportamiento del sistema.
            </p>
            <p>
            Si el retardo es constante, el patrón de picos y valles se repite de manera periódica. Este patrón suele observarse con claridad en respuestas de magnitud cuando dos fuentes reproducen el mismo contenido.
            </p>
            <p>
            En la práctica, el filtro de peine puede degradar la claridad, alterar el balance tonal y dificultar que el público perciba una cobertura homogénea. Por eso se considera un problema central en zonas donde confluyen varias fuentes con material correlacionado.
            </p>
            <p>
            Su presencia también sirve como herramienta diagnóstica: cuando aparecen muescas periódicas bien definidas, suele haber una diferencia temporal estable entre dos contribuciones relevantes en el punto medido.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with theory_tabs[4]:
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Polaridad y delay: diferencias clave</div>
            <p>
            Invertir la polaridad equivale a multiplicar la señal por <b>−1</b>. En términos de fase, esa operación representa un desplazamiento de <b>180°</b> constante para todas las frecuencias del espectro.
            </p>
            <p>
            En cambio, un delay produce un desplazamiento de fase proporcional a la frecuencia. Esta diferencia conceptual es crítica: una inversión de polaridad no compensa un retardo, y un retardo no equivale a una inversión de polaridad.
            </p>
            <p>
            Esta distinción es una de las más importantes en alineación de sistemas. Con frecuencia se observa una cancelación intensa y se asume erróneamente que invertir polaridad resolverá el problema. Sin embargo, si la causa principal es temporal, esa inversión solo modificará la relación angular, pero no corregirá el origen físico del desfase.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.latex(r"x(t) \rightarrow -x(t)")
        polarity_fig_signals, polarity_fig_sum = create_polarity_chart()
        st.plotly_chart(polarity_fig_signals, use_container_width=True)
        st.plotly_chart(polarity_fig_sum, use_container_width=True)
        st.markdown("""
        <div class="theory-grid">
            <div class="theory-card">
                <h4>Polaridad invertida</h4>
                <p>Desplazamiento de 180° en todas las frecuencias.</p>
            </div>
            <div class="theory-card">
                <h4>Delay</h4>
                <p>Desplazamiento de fase variable con la frecuencia.</p>
            </div>
            <div class="theory-card">
                <h4>Consecuencia</h4>
                <p>No son herramientas equivalentes y no corrigen el mismo tipo de problema.</p>
            </div>
            <div class="theory-card">
                <h4>Aplicación</h4>
                <p>La polaridad puede resolver casos específicos; el delay busca alinear tiempos de llegada.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Criterio de uso</div>
            <p>
            Si dos señales están razonablemente alineadas en tiempo pero una presenta orientación opuesta respecto de la otra, una inversión de polaridad puede mejorar la interacción.
            </p>
            <p>
            Si el problema principal es una diferencia de trayecto entre fuentes, el ajuste más lógico suele ser el delay. En la práctica, ambos recursos deben interpretarse conjuntamente con las mediciones de magnitud y fase.
            </p>
            <p>
            En sistemas complejos, la decisión rara vez puede tomarse a partir de una sola gráfica o una sola frecuencia. Lo correcto es observar cómo varía la interacción en la banda de interés y evaluar si el ajuste mejora la coherencia en la región espectral relevante para la aplicación.
            </p>
            <p>
            Por ello, polaridad y delay deben entenderse como herramientas distintas dentro de una estrategia de alineación, no como soluciones intercambiables.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with theory_tabs[5]:
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Ajuste temporal y dependencia espacial</div>
            <p>
            En refuerzo sonoro se usan delays digitales para compensar diferencias de propagación entre fuentes. El objetivo es mejorar la relación de fase en una región útil del espectro, no necesariamente en todas las frecuencias.
            </p>
            <p>
            También es importante entender que la interacción entre fuentes cambia con la posición del oyente. Una alineación favorable en un punto no garantiza el mismo resultado en toda el área de cobertura.
            </p>
            <p>
            Esto ocurre porque las distancias relativas entre las fuentes y cada asiento del público cambian constantemente. Por lo tanto, también cambia la diferencia de tiempo y, con ella, la fase.
            </p>
            <p>
            El resultado es que la respuesta del sistema no es idéntica en toda el área. Algunas posiciones pueden presentar una suma muy favorable, mientras que otras muestran cancelaciones importantes en bandas específicas.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.plotly_chart(create_spatial_dependency_chart(), use_container_width=True)
        st.markdown("""
        <div class="theory-grid">
            <div class="theory-card">
                <h4>Delay</h4>
                <p>Corrige diferencias temporales entre fuentes para mejorar la suma en un rango de frecuencias.</p>
            </div>
            <div class="theory-card">
                <h4>Ganancia</h4>
                <p>Controla cuánto aporta cada fuente a la respuesta total en el punto de medición.</p>
            </div>
            <div class="theory-card">
                <h4>Polaridad</h4>
                <p>Puede resolver o agravar cancelaciones cuando las señales están temporalmente alineadas.</p>
            </div>
            <div class="theory-card">
                <h4>Geometría</h4>
                <p>La posición relativa entre fuentes y oyente modifica trayectos, tiempos de llegada y fase.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class='neon-panel'>
            <div class='panel-title'>Límite práctico de la alineación</div>
            <p>
            Una alineación no debe entenderse como una solución universal para toda el área, sino como una optimización en una zona o condición de referencia. Cuanto más grande es el sistema y más extensa el área de cobertura, más evidente se vuelve esta limitación.
            </p>
            <p>
            Por eso en aplicaciones reales se eligen cuidadosamente los puntos de medición, se priorizan bandas críticas y se acepta que no siempre puede lograrse coherencia completa en todas las posiciones.
            </p>
            <p>
            Esta realidad obliga a trabajar con criterios de compromiso. La meta no es una perfección imposible en todo el recinto, sino una mejora controlada y técnicamente defendible en la zona donde el sistema necesita rendir mejor.
            </p>
            <p>
            Entender esta limitación evita conclusiones erróneas durante el laboratorio: si una optimización mejora claramente un punto de referencia, eso no significa que el problema haya desaparecido en todo el espacio, sino que la interacción fue reorganizada de forma más conveniente en la región evaluada.
            </p>
        </div>
        """, unsafe_allow_html=True)

    col_theory = st.columns([1, 1, 1])[1]
    with col_theory:
        if st.button("CONTINUAR AL LABORATORIO", type="primary", key="continue_to_lab", use_container_width=True):
            st.session_state.theory_stage_completed = True
            st.rerun()

    if not st.session_state.theory_stage_completed:
        st.stop()
    
    # --- B. BIENVENIDA AL LABORATORIO ---
    st.markdown("""
    <div class='neon-panel'>
        <div class='panel-title'>LABORATORIO DE SIMULACIÓN PARA ALINEACIÓN DE SISTEMAS DE SONIDO</div>
        <p>
        Ahora puedes construir el escenario de simulación. Selecciona las fuentes, define su disposición espacial y analiza cómo cambian magnitud y fase cuando ajustas delay, ganancia y polaridad.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- C. MENÚ (MARCO) ---
    with st.container(border=True):
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="medium")
        
        # COL 1: Fuente A
        with c1:
            st.subheader("FUENTE A")
            
            # Asegurar que catalog tiene datos
            if not catalog:
                st.error("No hay datos disponibles en el catálogo")
                ba = None
            else:
                # Obtener marcas disponibles
                marcas = list(catalog.keys())
                if not marcas:
                    st.error("No hay marcas disponibles")
                    ba = None
                else:
                    ba = st.selectbox("Marca A", marcas, key="ba", index=0)
            
            if ba and ba in catalog:
                # Filtrar tipos para excluir SUBWOOFER
                tipos_disponibles = list(catalog[ba].keys())
                ta_opts = [k for k in tipos_disponibles if "SUB" not in k.upper()]
                
                if not ta_opts:
                    st.warning("No hay tipos disponibles (excluyendo SUBWOOFER)")
                    ta = None
                else:
                    ta = st.selectbox("Tipo A", ta_opts, key="ta", index=0)
                
                if ta and ta in catalog[ba]:
                    modelos_disponibles = list(catalog[ba][ta].keys())
                    if not modelos_disponibles:
                        st.warning("No hay modelos disponibles para este tipo")
                        ma = None
                        pathA = None
                    else:
                        ma = st.selectbox("Modelo A", modelos_disponibles, key="ma", index=0)
                        pathA = catalog[ba][ta][ma]
                else:
                    ma = None
                    pathA = None
            else:
                ta = None
                ma = None
                pathA = None
            
            st.divider()
            
            # Solo mostrar sliders si tenemos una fuente válida
            if pathA:
                sep_x = st.slider("Separación A↔B en X (m)", 0.5, 8.0, 4.0, step=0.1, key="sep_x")
                yA = st.slider("Posición Y Fuente A (m)", 0.5, 15.0, 10.0, step=0.1, key="yA")
                xA = -sep_x / 2.0
            else:
                sep_x = 4.0
                yA = 10.0
                xA = -2.0
                st.warning("Selecciona una fuente A válida para habilitar controles")
        
        # COL 2: Fuente B
        with c2:
            st.subheader("FUENTE B")
            
            # Verificar si pathA está definido
            if pathA:
                mode_b = st.radio("Config B", ["Igual a A", "Independiente"], key="mode_b")
                
                if mode_b == "Igual a A":
                    pathB, lblB = pathA, f"{ma}"
                    st.info("Bloqueado (Igual a A)")
                else:
                    # Obtener marcas disponibles para B
                    marcas_b = list(catalog.keys())
                    if not marcas_b:
                        st.error("No hay marcas disponibles")
                        bb = None
                    else:
                        bb = st.selectbox("Marca B", marcas_b, key="bb", index=0)
                    
                    if bb and bb in catalog:
                        # Filtrar tipos para excluir SUBWOOFER
                        tipos_disponibles_b = list(catalog[bb].keys())
                        tb_opts = [k for k in tipos_disponibles_b if "SUB" not in k.upper()]
                        
                        if not tb_opts:
                            st.warning("No hay tipos disponibles (excluyendo SUBWOOFER)")
                            tb = None
                        else:
                            tb = st.selectbox("Tipo B", tb_opts, key="tb", index=0)
                        
                        if tb and tb in catalog[bb]:
                            modelos_disponibles_b = list(catalog[bb][tb].keys())
                            if not modelos_disponibles_b:
                                st.warning("No hay modelos disponibles para este tipo")
                                mb = None
                                pathB = None
                            else:
                                mb = st.selectbox("Modelo B", modelos_disponibles_b, key="mb", index=0)
                                pathB = catalog[bb][tb][mb]
                                lblB = mb
                        else:
                            mb = None
                            pathB = None
                            lblB = ""
                    else:
                        tb = None
                        mb = None
                        pathB = None
                        lblB = ""
            else:
                mode_b = "Independiente"
                pathB = None
                lblB = "No disponible"
                st.warning("Primero selecciona una fuente A")
            
            st.divider()
            
            # Controles para B si tenemos pathB
            if pathB:
                gain_B = st.slider("Ganancia B (dB)", -6.0, 6.0, 0.0, step=0.1, key="gain_B_db")
                delay_B = st.slider("Delay B (ms)", -30.0, 30.0, 0.0, step=0.1, key="delay_B_ms")
                pol_B = st.checkbox("Invertir polaridad B", key="pol_B")
                yB = st.slider("Posición Y Fuente B (m)", 0.5, 15.0, 10.0, step=0.1, key="yB")
            else:
                gain_B = 0.0
                delay_B = 0.0
                pol_B = False
                yB = 10.0
            
            xB = sep_x / 2.0 if 'sep_x' in locals() else 2.0
        
        # COL 3: Fuente C
        with c3:
            st.subheader("FUENTE C")
            
            # Solo permitir activar tercera fuente si tenemos A y B válidas
            if pathA and pathB:
                use_third = st.checkbox("Activar tercera fuente", key="use_third")
            else:
                use_third = False
                st.warning("Selecciona fuentes A y B válidas para habilitar fuente C")
            
            pathC, lblC = None, ""
            
            if use_third:
                source_type = st.radio("Tipo de fuente C", ["Subwoofer", "Top adicional"], key="source_type")
                
                # Obtener marcas disponibles para C
                marcas_c = list(catalog.keys())
                if not marcas_c:
                    st.error("No hay marcas disponibles")
                    bc = None
                else:
                    bc = st.selectbox("Marca C", marcas_c, key="bc", index=0)
                
                if bc and bc in catalog:
                    if source_type == "Subwoofer":
                        # Buscar tipos que contengan "SUB"
                        tc_opts = [k for k in catalog[bc].keys() if "SUB" in k.upper()]
                        if not tc_opts:
                            tc_opts = list(catalog[bc].keys())
                            st.warning("No se encontraron subwoofers específicos, mostrando todos los tipos")
                    else:
                        # Excluir SUBWOOFER
                        tc_opts = [k for k in catalog[bc].keys() if "SUB" not in k.upper()]
                        if not tc_opts:
                            tc_opts = list(catalog[bc].keys())
                            st.warning("No hay tipos disponibles (excluyendo SUBWOOFER), mostrando todos")
                    
                    if not tc_opts:
                        st.error("No hay tipos disponibles para esta marca")
                        tc = None
                    else:
                        tc = st.selectbox("Tipo C", tc_opts, key="tc", index=0)
                    
                    if tc and tc in catalog[bc]:
                        modelos_disponibles_c = list(catalog[bc][tc].keys())
                        if not modelos_disponibles_c:
                            st.warning("No hay modelos disponibles para este tipo")
                            mc = None
                            pathC = None
                        else:
                            mc = st.selectbox("Modelo C", modelos_disponibles_c, key="mc", index=0)
                            pathC = catalog[bc][tc][mc]
                            lblC = mc
                    else:
                        mc = None
                        pathC = None
                        lblC = ""
                else:
                    tc = None
                    mc = None
                    pathC = None
                    lblC = ""
                
                if source_type == "Subwoofer":
                    depth = st.slider("Profundidad SUB (m)", -5.0, 5.0, 0.0, step=0.1, key="depth")
                    posC = (0.0, max(yA, yB) + depth)
                else:
                    yC = st.slider("Posición Y Fuente C (m)", 0.5, 15.0, 5.0, step=0.1, key="yC")
                    posC = (0.0, yC)
            else:
                source_type = None
                depth = 0.0
                posC = (0.0, 0.0)
    
    # --- D. DIAGRAMA ---
    st.markdown("""
    <div class='neon-panel'>
        <div class='panel-title'>DIAGRAMA DE DISPOSICIÓN</div>
        <p>
        Con base en los parámetros que seleccionaste, el sistema ha generado un caso de estudio específico. A continuación verás una representación visual del sistema simulado, que te permitirá identificar la disposición de las fuentes y comprender el escenario que será analizado en los siguientes pasos.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar que tenemos posiciones válidas
    if 'xA' in locals() and 'yA' in locals():
        posA = (float(xA), float(yA))
        posB = (float(xB), float(yB))
        
        # Generar diagrama solo si tenemos al menos fuente A
        fig = generar_diagrama_neon(posA, posB, use_third, source_type, posC)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.pyplot(fig)
        
        # Tabla de leyenda
        st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
        <table style="margin: auto; border: 1px solid #00ffff; border-collapse: collapse; background-color: rgba(0,10,20,0.8);">
        <tr>
            <th style="border: 1px solid #00ffff; padding: 8px; color: #00ffff;">Elemento</th>
            <th style="border: 1px solid #00ffff; padding: 8px; color: #00ffff;">Símbolo</th>
            <th style="border: 1px solid #00ffff; padding: 8px; color: #00ffff;">Descripción</th>
        </tr>
        <tr>
            <td style="border: 1px solid #00ffff; padding: 8px;">Fuente A</td>
            <td style="border: 1px solid #00ffff; padding: 8px; color:#00ffff; font-weight: bold;">A</td>
            <td style="border: 1px solid #00ffff; padding: 8px;">{ma if ma else 'No seleccionada'}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #00ffff; padding: 8px;">Fuente B</td>
            <td style="border: 1px solid #00ffff; padding: 8px; color:#00ffff; font-weight: bold;">B</td>
            <td style="border: 1px solid #00ffff; padding: 8px;">{lblB if lblB else 'No seleccionada'}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #00ffff; padding: 8px;">Fuente C</td>
            <td style="border: 1px solid #00ffff; padding: 8px; color:#ff00ff; font-weight: bold;">C</td>
            <td style="border: 1px solid #00ffff; padding: 8px;">{lblC if use_third else 'No activada'}</td>
        </tr>
        <tr>
            <td style="border: 1px solid #00ffff; padding: 8px;">Micrófono</td>
            <td style="border: 1px solid #00ffff; padding: 8px; color:red; font-weight: bold;">●</td>
            <td style="border: 1px solid #00ffff; padding: 8px;">Punto de medición</td>
        </tr>
        </table>
        </div>
        """, unsafe_allow_html=True)
    
    # --- E. CARGAR DATOS ---
    @st.cache_data
    def load_initial_data(pathA, pathB, pathC=None):
        fA, mA, pA = load_clean_txt(pathA)
        f, Am, Ap = resample_to_bins(fA, mA, pA)
        
        fB, mB, pB = load_clean_txt(pathB)
        _, Bm, Bp = resample_to_bins(fB, mB, pB)
        
        Ac = magphase_deg_to_complex(Am, Ap)
        Bc = magphase_deg_to_complex(Bm, Bp)
        
        Cc, Cm, Cp = None, None, None
        if pathC:
            fC, mC, pC = load_clean_txt(pathC)
            _, Cm, Cp = resample_to_bins(fC, mC, pC)
            Cc = magphase_deg_to_complex(Cm, Cp)
        
        return {
            'f': f, 'Am': Am, 'Ap': Ap, 'Ac': Ac,
            'Bm': Bm, 'Bp': Bp, 'Bc': Bc,
            'Cc': Cc, 'Cm': Cm, 'Cp': Cp
        }
    
    # Botón para iniciar análisis
    st.markdown("---")
    col_start = st.columns([1, 1, 1])[1]
    with col_start:
        # Verificar que tenemos al menos fuente A y B para iniciar análisis
        if pathA and pathB:
            if st.button("INICIAR ANÁLISIS DE SIMULACIÓN", type="primary", key="start_analysis", use_container_width=True):
                st.session_state.analysis_started = True
                st.session_state.ia_recommendation_AB = None
                st.session_state.dsp_recommendation_C = None
                st.session_state.user_choice_AB = 'initial'
                st.session_state.user_choice_C = 'initial'
                st.session_state.step = 1
                st.rerun()
        else:
            st.button("INICIAR ANÁLISIS DE SIMULACIÓN", type="primary", key="start_analysis", 
                     use_container_width=True, disabled=True,
                     help="Selecciona fuentes A y B válidas para iniciar el análisis")
    
    # Solo mostrar análisis si se ha iniciado y tenemos fuentes válidas
    if st.session_state.analysis_started and pathA and pathB:
        try:
            # Cargar datos
            data = load_initial_data(pathA, pathB, pathC if use_third else None)
            f = data['f']
            
            # Calcular propagación geométrica
            c = float(SOUND_SPEED)
            dist_A = max(np.hypot(xA, yA), 1.0)
            dist_B = max(np.hypot(xB, yB), 1.0)
            
            att_A_db = -20.0 * np.log10(max(dist_A, 1e-6))
            att_B_db = -20.0 * np.log10(max(dist_B, 1e-6))
            
            delay_A_geom = (dist_A - 1.0) / c * 1000.0
            delay_B_geom = (dist_B - 1.0) / c * 1000.0
            
            # Aplicar propagación a A (solo geometría)
            A_bad = apply_dsp(data['Ac'], f, delay_A_geom, att_A_db, 0)
            Am_bad, Ap_bad = complex_to_magphase_deg(A_bad)
            
            # Aplicar propagación a B + ajustes iniciales del usuario
            B_initial = apply_dsp(data['Bc'], f, delay_B_geom + delay_B, att_B_db + gain_B, pol_B)
            Bm_initial, Bp_initial = complex_to_magphase_deg(B_initial)
            
            # Suma inicial A+B
            Sum_AB_initial_complex = A_bad + B_initial
            Sm_AB_initial, Sph_AB_initial = complex_to_magphase_deg(Sum_AB_initial_complex)
            
            # Procesar fuente C si existe
            if use_third and data['Cc'] is not None:
                dist_C = max(np.hypot(posC[0], posC[1]), 1.0)
                att_C_db = -20.0 * np.log10(max(dist_C, 1e-6))
                delay_C_geom = (dist_C - 1.0) / c * 1000.0
                C_initial = apply_dsp(data['Cc'], f, delay_C_geom, att_C_db, 0)
                Cm_initial, Cp_initial = complex_to_magphase_deg(C_initial)
            
            # ==========================================
            # PASO 1: ANÁLISIS DE FUENTES A y B
            # ==========================================
            if st.session_state.step >= 1:
                st.header("PASO 1: ANÁLISIS DE FUENTES A Y B")
                
                st.markdown("""
                <div class='neon-panel'>
                    <div class='panel-title'>FUNDAMENTOS DEL ANÁLISIS INDIVIDUAL DE FUENTES</div>
                    <p>
                    La optimización de un sistema de refuerzo sonoro es un <b>proceso analítico</b>. Antes de aplicar cualquier ajuste, es necesario comprender cómo se comporta cada fuente acústica de forma individual, ya que el resultado final que percibe el oyente es consecuencia directa de la interacción entre todas ellas. Por esta razón, el análisis del comportamiento individual de las fuentes constituye el primer paso real en cualquier proceso de alineación.
                    </p>
                    <p>
                    El comportamiento sonoro de cada fuente se describe, desde un punto de vista técnico, a través de dos respuestas fundamentales: la <b>respuesta en magnitud</b> y la <b>respuesta en fase</b>. La respuesta en magnitud indica cómo se relaciona el nivel de presión sonora generado por la fuente con respecto a la frecuencia, mientras que la fase describe la relación temporal de cada frecuencia.
                    </p>
                    <p>
                    En el contexto de la alineación de sistemas, la fase adquiere un papel crítico. Cuando varias fuentes reproducen el mismo contenido espectral, basta con que tengan diferencias temporales para que las señales se refuercen y/o se cancelen en diferentes frecuencias. Estos fenómenos no son fallos del sistema, sino consecuencias físicas de la superposición de ondas sonoras.
                    </p>
                    <p>
                    La optimización tiene como objetivo lograr una suma constructiva gestionando las diferencias de fase y magnitud así como la respuesta en frecuencia de todas las fuentes que intervienen en el sistema. Para este proceso se comienza <b>observando y comprendiendo</b> cómo responde cada fuente por separado y luego observando sus diferencias, primero con respecto al tiempo, y luego con respecto a la magnitud. Este análisis permite identificar qué parte del comportamiento del sistema es inherente a la fuente y qué parte es resultado de su interacción con otras.
                    </p>
                    <p>
                    A continuación, analizarás la respuesta en magnitud y en fase de cada fuente individual, estableciendo el punto de partida necesario para entender, más adelante, cómo estas respuestas se combinan cuando las fuentes operan simultáneamente.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Detectar tipo de fuentes
                same_file = (pathA == pathB)
                
                # --- Fuente A ---
                with st.expander(f"ANÁLISIS INDIVIDUAL - FUENTE A: {ma}", expanded=False):
                    figA = plot_fuente_bonita(f, Am_bad, Ap_bad, f"FUENTE A: {ma}", "#00ffff")
                    st.plotly_chart(figA, use_container_width=True)
                    st.markdown(analizar_fuente_detallado(f, Am_bad, Ap_bad, f"Fuente A ({ma})"))
                
                # --- Fuente B ---
                with st.expander(f"ANÁLISIS INDIVIDUAL - FUENTE B: {lblB}", expanded=False):
                    figB = plot_fuente_bonita(f, Bm_initial, Bp_initial, f"FUENTE B: {lblB}", "#ff00ff")
                    st.plotly_chart(figB, use_container_width=True)
                    st.markdown(analizar_fuente_detallado(f, Bm_initial, Bp_initial, f"Fuente B ({lblB})"))
                
                # --- Comparación A vs B ---
                st.markdown("""
                <div class='neon-panel'>
                    <div class='panel-title'>ANÁLISIS COMPARATIVO DE FUENTES</div>
                    <p>
                    A continuación observarás una gráfica en la que se superponen las respuestas individuales de cada fuente. Esta forma de visualización permite comparar directamente su comportamiento y facilita la identificación de diferencias en magnitud y fase que, más adelante, pueden generar interacciones destructivas cuando las fuentes operan de manera conjunta. Superponer respuestas es una práctica habitual en los procesos de medición y optimización, ya que ayuda a anticipar posibles inconvenientes antes de que ocurran en la suma del sistema. En herramientas de medición profesional, como Smaart, este recurso no solo es posible, sino fundamental, ya que permite analizar las fuentes de manera comparativa y tomar decisiones técnicas con mayor claridad y fundamento.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("ANÁLISIS COMPARATIVO - FUENTE A vs FUENTE B", expanded=False):
                    fig_mag_ab, fig_ph_ab = plot_comparison_mag_phase(
                        f,
                        [
                            (Am_bad, Ap_bad, f"Fuente A ({ma})", "#00ffff"),
                            (Bm_initial, Bp_initial, f"Fuente B ({lblB})", "#ff00ff")
                        ],
                        "ANÁLISIS COMPARATIVO: FUENTE A vs FUENTE B"
                    )
                    st.plotly_chart(fig_mag_ab, use_container_width=True)
                    st.plotly_chart(fig_ph_ab, use_container_width=True)
                    st.markdown(analizar_comparacion_detallada(f, Am_bad, Ap_bad, Bm_initial, Bp_initial, 
                                                            f"Fuente A ({ma})", f"Fuente B ({lblB})"))
                
                # --- Suma inicial A+B ---
                with st.expander("SUMA INICIAL - FUENTE A + FUENTE B", expanded=False):
                    fig_mag_sum, fig_ph_sum = plot_comparison_mag_phase(
                        f,
                        [
                            (Am_bad, Ap_bad, f"Fuente A ({ma})", "#00ffff"),
                            (Bm_initial, Bp_initial, f"Fuente B ({lblB})", "#ff00ff"),
                            (Sm_AB_initial, Sph_AB_initial, "Suma A+B (Inicial)", "#ffffff")
                        ],
                        "RESPUESTA EN MAGNITUD DE LAS FUENTES Y SU SUMA",
                        "RESPUESTA EN FASE DE LAS FUENTES Y SU SUMA"
                    )
                    st.plotly_chart(fig_mag_sum, use_container_width=True)
                    st.plotly_chart(fig_ph_sum, use_container_width=True)
                
                # Texto antes del botón
                st.markdown("""
                <div class='neon-panel'>
                    <div class='panel-title'>TRANSICIÓN AL AJUSTE</div>
                    <p>
                    Una vez analizado el comportamiento individual de las fuentes, y teniendo en cuenta el resultado de su sumatoria, se puede determinar si existe un problema en la alineación o no. Si se identifica un problema, es necesario ajustar el sistema modificando la respuesta en magnitud y fase de las fuentes por medio de la variación en parámetros como el delay, la ganancia y la polaridad.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Botón para avanzar al paso 2
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn2:
                    if st.button("AVANZAR A OPTIMIZACIÓN A-B", type="primary", key="step1_to_step2", use_container_width=True):
                        st.session_state.step = 2
                        st.rerun()
            
            # ==========================================
            # PASO 2: OPTIMIZACIÓN DE A Y B
            # ==========================================
            if st.session_state.step >= 2:
                st.markdown("---")
                st.header("PASO 2: OPTIMIZACIÓN DE A Y B")
                
                st.markdown(f"""
                <div class='neon-panel'>
                    <div class='panel-title'>OPTIMIZACIÓN CON INTELIGENCIA ARTIFICIAL</div>
                    <p>
                    En este laboratorio podrás encontrar una recomendación de ajuste de los parámetros de Delay, Ganancia y Polaridad, proporcionados por un modelo de inteligencia artificial que fue entrenado con el fin de resolver problemas de ajuste básicos de sistemas de sonido conformados por dos y tres fuentes.
                    </p>
                    <p>
                    Cuando pulses el botón de abajo, encontrarás los valores de los tres parámetros recomendados por la inteligencia artificial para ajustar el escenario de simulación que definiste al inicio del laboratorio.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # --- RECOMENDACIÓN IA PARA A Y B ---
                col_ia1, col_ia2, col_ia3 = st.columns([1, 1, 1])
                with col_ia2:
                    if st.button("OBTENER RECOMENDACIÓN IA PARA A-B", type="secondary", key="get_ia_recommendation_ab", use_container_width=True):
                        with st.spinner(f"Procesando con modelo para fuentes {'iguales' if same_file else 'diferentes'}..."):
                            st.session_state.ia_recommendation_AB = get_ai_recommendation_AB(
                                Am_bad, Ap_bad, Bm_initial, Bp_initial, same_file
                            )
                            
                            if st.session_state.ia_recommendation_AB:
                                rec = st.session_state.ia_recommendation_AB
                                st.session_state.user_adjustments_AB = {
                                    'delay': rec['delay'],
                                    'gain': rec['gain'],
                                    'pol': bool(rec['pol'])
                                }
                
                # Mostrar recomendación si existe
                if st.session_state.ia_recommendation_AB:
                    rec = st.session_state.ia_recommendation_AB
                    
                    # Cajita neon para recomendaciones
                    st.markdown("""
                    <div class="recommendation-box">
                        <div class="recommendation-title">RECOMENDACIÓN DE INTELIGENCIA ARTIFICIAL</div>
                        <div class="row">
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        <div class="recommendation-metric">
                            <div class="metric-title">DELAY RECOMENDADO B</div>
                            <div class="metric-value">{:.2f} ms</div>
                        </div>
                        """.format(rec['delay']), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div class="recommendation-metric">
                            <div class="metric-title">GANANCIA RECOMENDADA B</div>
                            <div class="metric-value">{:.2f} dB</div>
                        </div>
                        """.format(rec['gain']), unsafe_allow_html=True)
                    
                    with col3:
                        pol_text = "INVERTIR" if rec['pol'] else "NORMAL"
                        st.markdown("""
                        <div class="recommendation-metric">
                            <div class="metric-title">POLARIDAD RECOMENDADA</div>
                            <div class="metric-value">{}</div>
                        </div>
                        """.format(pol_text), unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Aplicar recomendación IA
                    B_ia = apply_dsp(data['Bc'], f, 
                                    delay_B_geom + delay_B + rec['delay'],
                                    att_B_db + gain_B + rec['gain'],
                                    pol_B ^ rec['pol'])
                    Sum_AB_ia = A_bad + B_ia
                    Sm_AB_ia, Sph_AB_ia = complex_to_magphase_deg(Sum_AB_ia)
                    
                    with st.expander("RESULTADO CON RECOMENDACIÓN IA", expanded=False):
                        st.markdown("""
                        <div class='neon-panel'>
                            <div class='panel-title'>COMPARATIVA DE SUMATORIAS</div>
                            <p>
                            A continuación podrás ver una comparativa de la sumatoria inicial de las fuentes (suma natural del sistema definido) y la sumatoria optimizada (aplicando los parámetros recomendados por la inteligencia artificial). Analiza detalladamente qué cambios hay en estas sumatorias y reflexiona acerca de si la recomendación de la IA contribuye al sistema o por el contrario lo afecta más.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        fig_mag_ia, fig_ph_ia = plot_comparison_mag_phase(
                            f,
                            [
                                (Sm_AB_initial, Sph_AB_initial, "Suma inicial", "#ff0000"),
                                (Sm_AB_ia, Sph_AB_ia, "Suma con IA", "#00ffcc"),
                            ],
                            "COMPARACIÓN: SUMA INICIAL vs SUMA CON IA"
                        )
                        st.plotly_chart(fig_mag_ia, use_container_width=True)
                        st.plotly_chart(fig_ph_ia, use_container_width=True)
                
                # --- AJUSTE MANUAL PARA A Y B ---
                with st.expander("AJUSTE MANUAL PARA A-B", expanded=False):
                    st.markdown("""
                    <div class='neon-panel'>
                        <div class='panel-title'>EXPLORACIÓN MANUAL DE PARÁMETROS</div>
                        <p>
                    El modelo de inteligencia artificial tiene un porcentaje de acierto superior al 90% de acuerdo con la validación técnica realizada, sin embargo, al no tener un 100% de precisión, el ajuste puede estar errado por unos pocos decimales. Por ende, a continuación podrás realizar un ajuste manual de los tres parámetros mencionados con el fin de que puedas analizar cómo se afecta la sumatoria conforme cambian los valores de ajuste. De esta manera, puedes llegar incluso a un ajuste mucho mejor que el proporcionado por la IA. <b>EXPLORA Y ANALIZA, ENTIENDE Y PREDICE AL SISTEMA.</b>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.ia_recommendation_AB:
                        default_delay = st.session_state.user_adjustments_AB['delay']
                        default_gain = st.session_state.user_adjustments_AB['gain']
                        default_pol = st.session_state.user_adjustments_AB['pol']
                    else:
                        default_delay = 0.0
                        default_gain = 0.0
                        default_pol = False
                    
                    col_adj1, col_adj2, col_adj3 = st.columns(3)
                    
                    with col_adj1:
                        st.markdown("**Delay adicional B**")
                        user_delay_text = st.text_input(
                            "Ingresa valor (ms):",
                            value=f"{default_delay:.2f}",
                            key="user_delay_text_ab",
                            label_visibility="collapsed"
                        )
                        try:
                            user_delay_adj = float(user_delay_text)
                        except:
                            user_delay_adj = default_delay
                            st.warning("Valor inválido, usando valor por defecto")
                    
                    with col_adj2:
                        st.markdown("**Ganancia adicional B**")
                        user_gain_text = st.text_input(
                            "Ingresa valor (dB):",
                            value=f"{default_gain:.2f}",
                            key="user_gain_text_ab",
                            label_visibility="collapsed"
                        )
                        try:
                            user_gain_adj = float(user_gain_text)
                        except:
                            user_gain_adj = default_gain
                            st.warning("Valor inválido, usando valor por defecto")
                    
                    with col_adj3:
                        user_pol_adj = st.checkbox(
                            "Invertir polaridad B (adicional)",
                            value=default_pol,
                            key="user_pol_checkbox_ab"
                        )
                    
                    st.session_state.user_adjustments_AB = {
                        'delay': user_delay_adj,
                        'gain': user_gain_adj,
                        'pol': user_pol_adj
                    }
                    
                    B_manual = apply_dsp(data['Bc'], f, 
                                        delay_B_geom + delay_B + user_delay_adj,
                                        att_B_db + gain_B + user_gain_adj,
                                        pol_B ^ user_pol_adj)
                    Sum_AB_manual = A_bad + B_manual
                    Sm_AB_manual, Sph_AB_manual = complex_to_magphase_deg(Sum_AB_manual)
                    
                    # Incluir también la recomendación IA en la gráfica si existe
                    if st.session_state.ia_recommendation_AB:
                        series = [
                            (Sm_AB_initial, Sph_AB_initial, "Suma inicial", "#ff0000"),
                            (Sm_AB_ia, Sph_AB_ia, "Suma con IA", "#00ff00"),
                            (Sm_AB_manual, Sph_AB_manual, "Suma con ajuste manual", "#ffff00")
                        ]
                    else:
                        series = [
                            (Sm_AB_initial, Sph_AB_initial, "Suma inicial", "#ff0000"),
                            (Sm_AB_manual, Sph_AB_manual, "Suma con ajuste manual", "#ffff00")
                        ]
                    
                    st.subheader("Comparación: Inicial vs IA vs Manual")
                    
                    fig_mag_manual, fig_ph_manual = plot_comparison_mag_phase(
                        f,
                        series,
                        "COMPARATIVA COMPLETA"
                    )
                    st.plotly_chart(fig_mag_manual, use_container_width=True)
                    st.plotly_chart(fig_ph_manual, use_container_width=True)
                
                # --- ELECCIÓN DEL USUARIO PARA A Y B ---
                st.markdown("---")
                st.subheader("ELECCIÓN DE CONFIGURACIÓN PARA A Y B")
                
                st.markdown("""
                <div class='neon-panel'>
                    <div class='panel-title'>TOMA DE DECISIÓN</div>
                    <p>
                    Ya has visto el comportamiento del sistema y cómo este varía conforme se cambian los parámetros de delay, ganancia y polaridad de las fuentes. De acuerdo a la última gráfica comparativa observada, ¿Cuál crees que es el ajuste más adecuado para ajustar el sistema de sonido simulado en el laboratorio?
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
                
                st.markdown('<div class="election-container">', unsafe_allow_html=True)
                
                col_choice1, col_choice2, col_choice3 = st.columns(3, gap="small")
                
                with col_choice1:
                    if st.button("**CONFIGURACIÓN INICIAL**", 
                               use_container_width=True,
                               help="Mantener la configuración original sin ajustes",
                               type="primary" if st.session_state.user_choice_AB == 'initial' else "secondary"):
                        st.session_state.user_choice_AB = 'initial'
                        st.session_state.chosen_config_AB = {
                            'delay': 0.0,
                            'gain': 0.0,
                            'pol': 0
                        }
                        st.rerun()
                
                with col_choice2:
                    if st.session_state.ia_recommendation_AB:
                        if st.button("**CONFIGURACIÓN INTELIGENCIA ARTIFICIAL**", 
                                   use_container_width=True,
                                   help="Usar los valores recomendados por la IA",
                                   type="primary" if st.session_state.user_choice_AB == 'ia' else "secondary"):
                            st.session_state.user_choice_AB = 'ia'
                            st.session_state.chosen_config_AB = {
                                'delay': st.session_state.ia_recommendation_AB['delay'],
                                'gain': st.session_state.ia_recommendation_AB['gain'],
                                'pol': int(st.session_state.ia_recommendation_AB['pol'])
                            }
                            st.rerun()
                
                with col_choice3:
                    if st.button("**CONFIGURACIÓN MANUAL**", 
                               use_container_width=True,
                               help="Usar los valores ajustados manualmente",
                               type="primary" if st.session_state.user_choice_AB == 'manual' else "secondary"):
                        st.session_state.user_choice_AB = 'manual'
                        st.session_state.chosen_config_AB = {
                            'delay': st.session_state.user_adjustments_AB['delay'],
                            'gain': st.session_state.user_adjustments_AB['gain'],
                            'pol': int(st.session_state.user_adjustments_AB['pol'])
                        }
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Determinar qué ajuste se eligió
                ajuste_elegido = {
                    'initial': 'INICIAL',
                    'ia': 'INTELIGENCIA ARTIFICIAL', 
                    'manual': 'MANUAL'
                }.get(st.session_state.user_choice_AB, 'INICIAL')
                
                # Mostrar resultado final para 2 fuentes
                if not use_third:
                    st.markdown("---")
                    st.header("RESULTADO FINAL DEL SISTEMA (2 FUENTES)")
                    
                    # Aplicar configuración elegida
                    chosen_config = st.session_state.chosen_config_AB
                    B_optimized = apply_dsp(data['Bc'], f, 
                                           delay_B_geom + delay_B + chosen_config['delay'],
                                           att_B_db + gain_B + chosen_config['gain'],
                                           pol_B ^ bool(chosen_config['pol']))
                    
                    Sum_AB_final = A_bad + B_optimized
                    Sm_AB_final, Sph_AB_final = complex_to_magphase_deg(Sum_AB_final)
                    
                    # Mostrar resumen mejorado
                    st.markdown(f"""
                    <div class="recommendation-box" style="background: linear-gradient(135deg, rgba(0, 40, 80, 0.9), rgba(0, 0, 40, 0.9));">
                        <div class="recommendation-title">CONFIGURACIÓN FINAL DEL SISTEMA</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
                            <div class="recommendation-metric">
                                <div class="metric-title">AJUSTE ELEGIDO</div>
                                <div class="metric-value">{ajuste_elegido}</div>
                            </div>
                            <div class="recommendation-metric">
                                <div class="metric-title">DELAY APLICADO</div>
                                <div class="metric-value">{chosen_config['delay']:.2f} ms</div>
                            </div>
                            <div class="recommendation-metric">
                                <div class="metric-title">GANANCIA APLICADA</div>
                                <div class="metric-value">{chosen_config['gain']:.2f} dB</div>
                            </div>
                            <div class="recommendation-metric">
                                <div class="metric-title">POLARIDAD</div>
                                <div class="metric-value">{"INVERTIDA" if chosen_config['pol'] else "NORMAL"}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Gráfica final
                    with st.expander("RESULTADO FINAL DEL SISTEMA", expanded=True):
                        fig_mag_final, fig_ph_final = plot_comparison_mag_phase(
                            f,
                            [
                                (Sm_AB_initial, Sph_AB_initial, "Suma A+B inicial", "#ff0000"),
                                (Sm_AB_final, Sph_AB_final, "Suma A+B optimizada", "#00ff00")
                            ],
                            "EVOLUCIÓN: A+B INICIAL vs OPTIMIZADA"
                        )
                        st.plotly_chart(fig_mag_final, use_container_width=True)
                        st.plotly_chart(fig_ph_final, use_container_width=True)
                    
                    # Mensaje final
                    st.markdown("""
                    <div class='neon-panel'>
                        <div class='panel-title'>LABORATORIO COMPLETADO</div>
                        <p>
                        ¡Felicidades! Has completado exitosamente el laboratorio de simulación de alineación de sistemas de sonido con 2 fuentes. A través de este ejercicio has podido:
                        </p>
                        <ul>
                        <li>Analizar el comportamiento individual de fuentes acústicas</li>
                        <li>Comprender cómo interactúan múltiples fuentes en un sistema</li>
                        <li>Experimentar con ajustes de delay, ganancia y polaridad</li>
                        <li>Comparar recomendaciones de IA con ajustes manuales</li>
                        <li>Tomar decisiones técnicas fundamentadas</li>
                        </ul>
                        <p>
                        Este conocimiento es fundamental para cualquier profesional del sonido que busque optimizar sistemas de refuerzo sonoro.
                        </p>
                        <p style="text-align: center; font-size: 1.2rem; color: #00ffff;">
                        <b>¡Continúa explorando y aprendiendo!</b>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Botón para avanzar al paso 3 (solo si hay tercera fuente)
                elif use_third:
                    st.markdown(f"""
                    <div class='neon-panel'>
                        <div class='panel-title'>INTEGRACIÓN DE LA TERCERA FUENTE</div>
                        <p>
                        Ya tenemos el ajuste final para el sistema conformado por las fuentes A y B. Es momento de integrar a la fuente C. Para ello, vamos a tomar la respuesta de la sumatoria optimizada de A y B como una sola fuente, y a la fuente C, como otra fuente independiente. De esta manera, se repite el proceso analítico realizado entre las fuentes A y B.
                        </p>
                        <p>
                        <b>Has elegido quedarte con el ajuste {ajuste_elegido}</b>. Vamos a tomar esta respuesta como si fuese una sola fuente, la cual vamos a alinear con otra fuente denominada C.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_adv1, col_adv2, col_adv3 = st.columns([1, 1, 1])
                    with col_adv2:
                        if st.button("AVANZAR A OPTIMIZACIÓN CON FUENTE C", type="primary", key="step2_to_step3", use_container_width=True):
                            st.session_state.step = 3
                            st.rerun()
            
            # ==========================================
            # PASO 3: OPTIMIZACIÓN CON FUENTE C (si existe)
            # ==========================================
            if use_third and st.session_state.step >= 3:
                st.markdown("---")
                st.header(f"PASO 3: OPTIMIZACIÓN CON FUENTE C ({lblC})")
                
                if source_type == "Subwoofer":
                    st.markdown(f"""
                    <div class='neon-panel'>
                        <div class='panel-title'>INCORPORACIÓN DEL SUBWOOFER</div>
                        <p>
                        Ahora incorporamos el subwoofer ({lblC}) al sistema ya optimizado de A y B. Para SUBWOOFER se usará <b>DSP</b> para calcular frecuencia de cruce y delay óptimo.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Determinar si C es igual a A/B
                    same_as_A = (pathC == pathA)
                    same_as_B = (pathC == pathB)
                    same_as_AB = same_as_A or same_as_B
                    
                    st.markdown(f"""
                    <div class='neon-panel'>
                        <div class='panel-title'>INCORPORACIÓN DE LA TERCERA FUENTE</div>
                        <p>
                        Ahora incorporamos la fuente C ({lblC}) al sistema ya optimizado de A y B.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # --- Configuración de A+B ya optimizada ---
                chosen_config = st.session_state.chosen_config_AB
                B_optimized = apply_dsp(data['Bc'], f, 
                                       delay_B_geom + delay_B + chosen_config['delay'],
                                       att_B_db + gain_B + chosen_config['gain'],
                                       pol_B ^ bool(chosen_config['pol']))
                
                Sum_AB_optimized = A_bad + B_optimized
                Sm_AB_optimized, Sph_AB_optimized = complex_to_magphase_deg(Sum_AB_optimized)
                
                # --- Suma inicial de A+B+C ---
                Sum_ABC_initial_complex = Sum_AB_optimized + C_initial
                Sm_ABC_initial, Sph_ABC_initial = complex_to_magphase_deg(Sum_ABC_initial_complex)
                
                with st.expander("SUMA INICIAL A+B+C", expanded=False):
                    st.markdown("""
                    <div class='neon-panel'>
                        <div class='panel-title'>ANÁLISIS DE LA SUMATORIA INICIAL CON C</div>
                        <p>
                        En la gráfica de abajo, puedes encontrar y comparar la respuesta de la optimización de A y B, la respuesta de la fuente C y la respuesta de la sumatoria entre A y B optimizados y la fuente C. Analiza las diferencias más importantes entre las fuentes y trata de predecir el comportamiento que tendrá la sumatoria.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    series_abc = [
                        (Sm_AB_optimized, Sph_AB_optimized, "Suma A+B (optimizada)", "#00ffff"),
                        (Cm_initial, Cp_initial, f"Fuente C ({lblC})", "#ffff00" if source_type == "Subwoofer" else "#00ff00"),
                        (Sm_ABC_initial, Sph_ABC_initial, "Suma A+B+C (inicial)", "#ffffff")
                    ]
                    
                    fig_mag_abc, fig_ph_abc = plot_comparison_mag_phase(
                        f,
                        series_abc,
                        "SUMA INICIAL A+B+C"
                    )
                    st.plotly_chart(fig_mag_abc, use_container_width=True)
                    st.plotly_chart(fig_ph_abc, use_container_width=True)
                
                # --- OPTIMIZACIÓN DE C ---
                st.markdown("---")
                st.subheader(f"Optimización de C ({source_type})")
                
                if source_type == "Subwoofer":
                    col_dsp1, col_dsp2, col_dsp3 = st.columns([1, 1, 1])
                    with col_dsp2:
                        if st.button("CALCULAR DSP PARA SUBWOOFER", type="secondary", key="calculate_dsp_sub", use_container_width=True):
                            with st.spinner("Calculando frecuencia de cruce y delay óptimo..."):
                                try:
                                    # Para DSP, necesitamos arrays de frecuencia
                                    f_array = f  # Ya tenemos el array de frecuencias
                                    
                                    # Calcular características para DSP
                                    st.session_state.dsp_recommendation_C = get_dsp_recommendation_C(
                                        f_array, Sm_AB_optimized, Sph_AB_optimized, Cm_initial, Cp_initial
                                    )
                                    
                                    if st.session_state.dsp_recommendation_C:
                                        rec_c = st.session_state.dsp_recommendation_C
                                        st.session_state.user_adjustments_C = {
                                            'delay': rec_c['delay'],
                                            'gain': rec_c['gain'],
                                            'pol': rec_c['pol']
                                        }
                                    
                                except Exception as e:
                                    st.error(f"Error al calcular DSP: {str(e)}")
                else:
                    col_ia_c1, col_ia_c2, col_ia_c3 = st.columns([1, 1, 1])
                    with col_ia_c2:
                        if st.button(f"OBTENER RECOMENDACIÓN IA PARA C", type="secondary", key="get_ai_recommendation_c", use_container_width=True):
                            with st.spinner(f"Procesando con modelo para fuentes {'iguales' if same_as_AB else 'diferentes'}..."):
                                try:
                                    st.session_state.dsp_recommendation_C = get_ai_recommendation_C(
                                        Sm_AB_optimized, Sph_AB_optimized,
                                        Cm_initial, Cp_initial,
                                        same_as_AB
                                    )
                                    
                                    if st.session_state.dsp_recommendation_C:
                                        rec_c = st.session_state.dsp_recommendation_C
                                        st.session_state.user_adjustments_C = {
                                            'delay': rec_c['delay'],
                                            'gain': rec_c['gain'],
                                            'pol': bool(rec_c['pol'])
                                        }
                                    
                                except Exception as e:
                                    st.error(f"Error al generar recomendación IA para C: {str(e)}")
                
                # Mostrar recomendación si existe
                if st.session_state.dsp_recommendation_C:
                    rec_c = st.session_state.dsp_recommendation_C
                    
                    # Cajita neon para recomendaciones
                    method_label = 'DSP' if source_type == 'Subwoofer' else 'IA'
                    st.markdown(f"""
                    <div class="recommendation-box">
                        <div class="recommendation-title">RECOMENDACIÓN {method_label} PARA FUENTE C</div>
                        <div class="row">
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("""
                        <div class="recommendation-metric">
                            <div class="metric-title">DELAY RECOMENDADO C</div>
                            <div class="metric-value">{:.2f} ms</div>
                        </div>
                        """.format(rec_c['delay']), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown("""
                        <div class="recommendation-metric">
                            <div class="metric-title">GANANCIA RECOMENDADA C</div>
                            <div class="metric-value">{:.2f} dB</div>
                        </div>
                        """.format(rec_c['gain']), unsafe_allow_html=True)
                    
                    with col3:
                        pol_text = "INVERTIR" if rec_c['pol'] else "NORMAL"
                        st.markdown("""
                        <div class="recommendation-metric">
                            <div class="metric-title">POLARIDAD RECOMENDADA</div>
                            <div class="metric-value">{}</div>
                        </div>
                        """.format(pol_text), unsafe_allow_html=True)
                    
                    if source_type == "Subwoofer" and 'crossover_freq' in rec_c:
                        st.markdown("""
                        <div class="recommendation-metric" style="grid-column: span 3;">
                            <div class="metric-title">FRECUENCIA DE CRUCE CALCULADA</div>
                            <div class="metric-value">{:.1f} Hz</div>
                        </div>
                        """.format(rec_c['crossover_freq']), unsafe_allow_html=True)
                    
                    st.markdown("</div></div>", unsafe_allow_html=True)
                    
                    # Aplicar recomendación a C
                    C_recommended = apply_dsp(data['Cc'], f, delay_C_geom + rec_c['delay'],
                                             att_C_db + rec_c['gain'], rec_c['pol'])
                    
                    Sum_ABC_recommended_complex = Sum_AB_optimized + C_recommended
                    Sm_ABC_recommended, Sph_ABC_recommended = complex_to_magphase_deg(Sum_ABC_recommended_complex)
                    
                    with st.expander("RESULTADO CON RECOMENDACIÓN", expanded=False):
                        fig_mag_rec_c, fig_ph_rec_c = plot_comparison_mag_phase(
                            f,
                            [
                                (Sm_ABC_initial, Sph_ABC_initial, "Suma A+B+C inicial", "#ff0000"),
                                (Sm_ABC_recommended, Sph_ABC_recommended, f"Suma A+B+C con {method_label}", "#00ffcc"),
                            ],
                            f"ANTES vs DESPUÉS ({method_label} para C)"
                        )
                        st.plotly_chart(fig_mag_rec_c, use_container_width=True)
                        st.plotly_chart(fig_ph_rec_c, use_container_width=True)
                
                # --- AJUSTE MANUAL PARA C ---
                with st.expander("AJUSTE MANUAL PARA C", expanded=False):
                    st.markdown("""
                    <div class='neon-panel'>
                        <div class='panel-title'>EXPLORACIÓN MANUAL DE PARÁMETROS PARA C</div>
                        <p>
                        Realiza ajustes manuales para la fuente C y observa cómo cambia la sumatoria total del sistema.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.session_state.dsp_recommendation_C:
                        default_delay_c = st.session_state.user_adjustments_C['delay']
                        default_gain_c = st.session_state.user_adjustments_C['gain']
                        default_pol_c = st.session_state.user_adjustments_C['pol']
                    else:
                        default_delay_c = 0.0
                        default_gain_c = 0.0
                        default_pol_c = False
                    
                    col_adj_c1, col_adj_c2, col_adj_c3 = st.columns(3)
                    
                    with col_adj_c1:
                        st.markdown("**Delay adicional C**")
                        user_delay_text_c = st.text_input(
                            "Ingresa valor (ms):",
                            value=f"{default_delay_c:.2f}",
                            key="user_delay_text_c",
                            label_visibility="collapsed"
                        )
                        try:
                            user_delay_adj_c = float(user_delay_text_c)
                        except:
                            user_delay_adj_c = default_delay_c
                            st.warning("Valor inválido, usando valor por defecto")
                    
                    with col_adj_c2:
                        st.markdown("**Ganancia adicional C**")
                        user_gain_text_c = st.text_input(
                            "Ingresa valor (dB):",
                            value=f"{default_gain_c:.2f}",
                            key="user_gain_text_c",
                            label_visibility="collapsed"
                        )
                        try:
                            user_gain_adj_c = float(user_gain_text_c)
                        except:
                            user_gain_adj_c = default_gain_c
                            st.warning("Valor inválido, usando valor por defecto")
                    
                    with col_adj_c3:
                        user_pol_adj_c = st.checkbox(
                            "Invertir polaridad C (adicional)",
                            value=default_pol_c,
                            key="user_pol_checkbox_c"
                        )
                    
                    st.session_state.user_adjustments_C = {
                        'delay': user_delay_adj_c,
                        'gain': user_gain_adj_c,
                        'pol': user_pol_adj_c
                    }
                    
                    C_manual = apply_dsp(data['Cc'], f, delay_C_geom + user_delay_adj_c,
                                        att_C_db + user_gain_adj_c, user_pol_adj_c)
                    
                    Sum_ABC_manual_complex = Sum_AB_optimized + C_manual
                    Sm_ABC_manual, Sph_ABC_manual = complex_to_magphase_deg(Sum_ABC_manual_complex)
                    
                    # Incluir también la recomendación si existe
                    if st.session_state.dsp_recommendation_C:
                        series_c = [
                            (Sm_ABC_initial, Sph_ABC_initial, "Suma A+B+C inicial", "#ff0000"),
                            (Sm_ABC_recommended, Sph_ABC_recommended, f"Suma con {'DSP' if source_type == 'Subwoofer' else 'IA'}", "#00ff00"),
                            (Sm_ABC_manual, Sph_ABC_manual, "Suma con ajuste manual", "#ffff00")
                        ]
                    else:
                        series_c = [
                            (Sm_ABC_initial, Sph_ABC_initial, "Suma A+B+C inicial", "#ff0000"),
                            (Sm_ABC_manual, Sph_ABC_manual, "Suma con ajuste manual", "#ffff00")
                        ]
                    
                    st.subheader("Comparación: Inicial vs Recomendación vs Manual")
                    
                    fig_mag_manual_c, fig_ph_manual_c = plot_comparison_mag_phase(
                        f,
                        series_c,
                        "COMPARATIVA COMPLETA PARA C"
                    )
                    st.plotly_chart(fig_mag_manual_c, use_container_width=True)
                    st.plotly_chart(fig_ph_manual_c, use_container_width=True)
                
                # --- ELECCIÓN DEL USUARIO PARA C ---
                st.markdown("---")
                st.subheader("ELECCIÓN DE CONFIGURACIÓN PARA C")
                
                st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
                
                st.markdown('<div class="election-container">', unsafe_allow_html=True)
                
                col_choice_c1, col_choice_c2, col_choice_c3 = st.columns(3, gap="small")
                
                with col_choice_c1:
                    if st.button("**C SIN AJUSTES**", 
                               use_container_width=True,
                               help="Mantener la configuración original de C sin ajustes",
                               type="primary" if st.session_state.user_choice_C == 'initial' else "secondary"):
                        st.session_state.user_choice_C = 'initial'
                        st.session_state.chosen_config_C = {
                            'delay': 0.0,
                            'gain': 0.0,
                            'pol': 0
                        }
                        st.rerun()
                
                with col_choice_c2:
                    if st.session_state.dsp_recommendation_C:
                        method_text = 'DSP' if source_type == 'Subwoofer' else 'IA'
                        if st.button(f"**C CON {method_text}**", 
                                   use_container_width=True,
                                   help=f"Usar los valores recomendados por {method_text}",
                                   type="primary" if st.session_state.user_choice_C == 'dsp' else "secondary"):
                            
                            st.session_state.user_choice_C = 'dsp'
                            st.session_state.chosen_config_C = {
                                'delay': st.session_state.dsp_recommendation_C['delay'],
                                'gain': st.session_state.dsp_recommendation_C['gain'],
                                'pol': int(st.session_state.dsp_recommendation_C['pol'])
                            }
                            st.rerun()
                
                with col_choice_c3:
                    if st.button("**C MANUAL**", 
                               use_container_width=True,
                               help="Usar los valores ajustados manualmente para C",
                               type="primary" if st.session_state.user_choice_C == 'manual' else "secondary"):
                        st.session_state.user_choice_C = 'manual'
                        st.session_state.chosen_config_C = {
                            'delay': st.session_state.user_adjustments_C['delay'],
                            'gain': st.session_state.user_adjustments_C['gain'],
                            'pol': int(st.session_state.user_adjustments_C['pol'])
                        }
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # --- RESULTADO FINAL DEL SISTEMA ---
                st.markdown("---")
                st.header("RESULTADO FINAL DEL SISTEMA (3 FUENTES)")
                
                chosen_config_C = st.session_state.chosen_config_C
                
                C_final = apply_dsp(data['Cc'], f, delay_C_geom + chosen_config_C['delay'],
                                   att_C_db + chosen_config_C['gain'], bool(chosen_config_C['pol']))
                
                Sum_ABC_final_complex = Sum_AB_optimized + C_final
                Sm_ABC_final, Sph_ABC_final = complex_to_magphase_deg(Sum_ABC_final_complex)
                
                # Mostrar resumen de configuraciones
                col_sum1, col_sum2 = st.columns(2)
                
                with col_sum1:
                    method_c = 'DSP' if source_type == 'Subwoofer' else 'IA'
                    choice_c = st.session_state.user_choice_C
                    choice_c_text = {
                        'initial': 'SIN AJUSTES',
                        'dsp': f'CON {method_c}',
                        'manual': 'MANUAL'
                    }.get(choice_c, 'SIN AJUSTES')
                    
                    st.markdown(f"""
                    <div class="recommendation-box" style="background: linear-gradient(135deg, rgba(0, 40, 80, 0.9), rgba(0, 0, 40, 0.9));">
                        <div class="recommendation-title">CONFIGURACIÓN FINAL A+B</div>
                        <div class="recommendation-metric">
                            <div class="metric-title">AJUSTE ELEGIDO</div>
                            <div class="metric-value">{ajuste_elegido}</div>
                        </div>
                        <div class="recommendation-metric">
                            <div class="metric-title">DELAY ADICIONAL B</div>
                            <div class="metric-value">{chosen_config['delay']:.2f} ms</div>
                        </div>
                        <div class="recommendation-metric">
                            <div class="metric-title">GANANCIA ADICIONAL B</div>
                            <div class="metric-value">{chosen_config['gain']:.2f} dB</div>
                        </div>
                        <div class="recommendation-metric">
                            <div class="metric-title">POLARIDAD ADICIONAL B</div>
                            <div class="metric-value">{"INVERTIDA" if chosen_config['pol'] else "NORMAL"}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sum2:
                    st.markdown(f"""
                    <div class="recommendation-box" style="background: linear-gradient(135deg, rgba(80, 0, 40, 0.9), rgba(40, 0, 0, 0.9));">
                        <div class="recommendation-title">CONFIGURACIÓN FINAL C</div>
                        <div class="recommendation-metric">
                            <div class="metric-title">AJUSTE ELEGIDO</div>
                            <div class="metric-value">{choice_c_text}</div>
                        </div>
                        <div class="recommendation-metric">
                            <div class="metric-title">DELAY ADICIONAL C</div>
                            <div class="metric-value">{chosen_config_C['delay']:.2f} ms</div>
                        </div>
                        <div class="recommendation-metric">
                            <div class="metric-title">GANANCIA ADICIONAL C</div>
                            <div class="metric-value">{chosen_config_C['gain']:.2f} dB</div>
                        </div>
                        <div class="recommendation-metric">
                            <div class="metric-title">POLARIDAD ADICIONAL C</div>
                            <div class="metric-value">{"INVERTIDA" if chosen_config_C['pol'] else "NORMAL"}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Mostrar resultado final
                with st.expander("RESULTADO FINAL DEL SISTEMA", expanded=True):
                    # Gráfica 1: A+B inicial vs optimizada
                    fig_mag_ab_final, fig_ph_ab_final = plot_comparison_mag_phase(
                        f,
                        [
                            (Sm_AB_initial, Sph_AB_initial, "Suma A+B inicial", "#ff0000"),
                            (Sm_AB_optimized, Sph_AB_optimized, "Suma A+B optimizada", "#00ff00")
                        ],
                        "EVOLUCIÓN: A+B INICIAL vs OPTIMIZADA"
                    )
                    st.plotly_chart(fig_mag_ab_final, use_container_width=True)
                    
                    # Gráfica 2: A+B+C inicial vs optimizada
                    fig_mag_abc_final, fig_ph_abc_final = plot_comparison_mag_phase(
                        f,
                        [
                            (Sm_ABC_initial, Sph_ABC_initial, "Suma A+B+C inicial", "#ff0000"),
                            (Sm_ABC_final, Sph_ABC_final, "Suma A+B+C optimizada", "#00ff00")
                        ],
                        "EVOLUCIÓN: A+B+C INICIAL vs OPTIMIZADA"
                    )
                    st.plotly_chart(fig_mag_abc_final, use_container_width=True)
                
                # --- MENSAJE FINAL DE CIERRE ---
                st.markdown("""
                <div class='neon-panel'>
                    <div class='panel-title'>LABORATORIO COMPLETADO</div>
                    <p>
                    ¡Felicidades! Has completado exitosamente el laboratorio de simulación de alineación de sistemas de sonido con 3 fuentes. A través de este ejercicio has podido:
                    </p>
                    <ul>
                    <li>Analizar el comportamiento individual de fuentes acústicas</li>
                    <li>Comprender cómo interactúan múltiples fuentes en un sistema</li>
                    <li>Experimentar con ajustes de delay, ganancia y polaridad</li>
                    <li>Comparar recomendaciones de IA/DSP con ajustes manuales</li>
                    <li>Tomar decisiones técnicas fundamentadas</li>
                    </ul>
                    <p>
                    Este conocimiento es fundamental para cualquier profesional del sonido que busque optimizar sistemas de refuerzo sonoro. Recuerda que la práctica constante y el análisis crítico son clave para dominar el arte de la alineación de sistemas.
                    </p>
                    <p style="text-align: center; font-size: 1.2rem; color: #00ffff;">
                    <b>¡Continúa explorando y aprendiendo!</b>
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        except Exception as e:
            st.error(f"Error durante el análisis: {str(e)}")
            st.info("Verifica que todas las fuentes seleccionadas tengan archivos válidos en la base de datos.")

if __name__ == "__main__":
    main()
