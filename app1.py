# -*- coding: utf-8 -*-
import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image
from io import BytesIO

# -----------------------------------------------------------------------------
# Configuración de página
# -----------------------------------------------------------------------------
st.set_page_config(page_title="OCR Cam", page_icon="🔎", layout="centered")

# -----------------------------------------------------------------------------
# Estilos (Dark theme alto contraste, SOLO estética)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
:root{
  --radius: 16px;
  /* Paleta con contraste real */
  --bgA: #0b1120;        /* fondo base */
  --bgB: #0f172a;        /* fondo gradiente */
  --panel: #111827;      /* panel sólido */
  --panel-border: #1f2937;
  --text: #f8fafc;       /* texto principal */
  --muted: #cbd5e1;      /* texto secundario */
  --input: #0f172a;      /* fondo inputs */
  --input-border: #334155;
  --focus: #22d3ee;      /* foco visible */
  --primaryA: #2563eb;   /* azul 600 */
  --primaryB: #1d4ed8;   /* azul 700 */
}

/* Fondo oscuro del contenedor raíz */
[data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg, var(--bgA) 0%, var(--bgB) 100%) !important;
  color: var(--text) !important;
}
html, body{
  color: var(--text) !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
}
main .block-container{padding-top: 2rem; padding-bottom: 3rem; max-width: 900px;}

/* Tarjetas (manteniendo tu clase .card) */
.card {
  background: var(--panel);
  border: 1px solid var(--panel-border);
  border-radius: 18px;
  padding: 18px 20px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.45);
}

/* Encabezado + badge */
.header { display:flex; align-items:center; gap:.6rem; margin-bottom:.5rem; }
.badge {
  font-size: .75rem; padding: .25rem .55rem; border-radius: 999px;
  background: linear-gradient(90deg, var(--primaryA), var(--primaryB));
  color:#ffffff; border: 0; font-weight: 600;
}
h1, h2, h3 { letter-spacing: -0.02em; color:#f9fafb !important; }
footer {visibility: hidden;}
/* Asegurar color de textos y labels en todo el main */
[data-testid="stMarkdownContainer"], 
[data-testid="stMarkdownContainer"] *, 
label, label *, 
.stRadio, .stRadio *, 
.stCheckbox, .stCheckbox * {
  color: var(--text) !important;
  opacity: 1 !important;
}

/* Sidebar oscuro consistente */
section[data-testid="stSidebar"] > div:first-child {
  background: #0c1324;
  border-right: 1px solid var(--panel-border);
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Inputs/controles */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect > div > div {
  background: var(--input) !important;
  border: 1px solid var(--input-border) !important;
  color: var(--text) !important;
  border-radius: 12px !important;
}
.stTextArea textarea::placeholder,
.stTextInput input::placeholder{ color: #94a3b8 !important; }
div[role="radiogroup"] label { color: var(--text) !important; }
input[type="radio"], input[type="checkbox"]{ accent-color: var(--primaryA) !important; }

/* Estados de foco visibles */
:focus, :focus-visible,
.stTextInput input:focus,
.stTextArea textarea:focus,
.stSelectbox div[data-baseweb="select"] > div:focus{
  outline: 2px solid var(--focus) !important;
  outline-offset: 2px !important;
  box-shadow: none !important;
}

/* Caja tipo terminal para el texto OCR */
.codebox {
  background:#0b1220; color:#e5e7eb; border-radius:14px; padding:14px 16px;
  border:1px solid #1f2937;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  line-height: 1.5; overflow-x: auto; white-space: pre-wrap;
}

/* Botones sólidos y legibles (incluye download button) */
.stButton > button, .stDownloadButton > button{
  border-radius: 999px;
  padding: .72rem 1.15rem;
  border: 1px solid var(--panel-border);
  background: linear-gradient(90deg, var(--primaryA), var(--primaryB)) !important;
  color: #ffffff !important;
  box-shadow: 0 14px 36px rgba(37,99,235,.35);
  transition: transform .15s ease, box-shadow .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 18px 48px rgba(37,99,235,.45);
}

/* Imagen */
div[data-testid="stImage"] img{
  border-radius: 14px !important;
  box-shadow: 0 22px 60px rgba(0,0,0,.55);
}

/* Pequeños */
.small { opacity:.9; font-size:.9rem; color: var(--muted) !important; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Título
# -----------------------------------------------------------------------------
st.markdown(
    '<div class="header"><h1>🔎 Reconocimiento Óptico de Caracteres</h1>'
    '<span class="badge">Cámara + OCR</span></div>',
    unsafe_allow_html=True,
)
st.markdown("Convierte lo que ves en **texto**. Toma una foto, aplica el filtro si lo necesitas y listo.")

# -----------------------------------------------------------------------------
# Sidebar (opciones)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Ajustes rápidos")
    filtro = st.radio("Aplicar Filtro", ('Con Filtro', 'Sin Filtro'))
    st.markdown("---")
    st.markdown("#### Tips")
    st.markdown("- Usa buena luz.\n- Acerca el texto y evita inclinaciones.\n- Si el fondo es oscuro y el texto claro, **Con Filtro** ayuda.")

# -----------------------------------------------------------------------------
# Cámara
# -----------------------------------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)
img_file_buffer = st.camera_input("📷 Toma una foto del texto")

# -----------------------------------------------------------------------------
# Procesamiento (misma lógica original)
# -----------------------------------------------------------------------------
texto_ocr = ""
preview_image = None

if img_file_buffer is not None:
    # Leer buffer a OpenCV
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Filtro (invertir colores si 'Con Filtro')
    if filtro == 'Con Filtro':
        cv2_img = cv2.bitwise_not(cv2_img)

    # Convertir a RGB para Tesseract y preview
    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)

    # OCR (igual que tu versión)
    texto_ocr = pytesseract.image_to_string(img_rgb)

    # Imagen para vista previa
    preview_image = Image.fromarray(img_rgb)

# -----------------------------------------------------------------------------
# UI de resultados
# -----------------------------------------------------------------------------
if img_file_buffer is None:
    st.markdown('<div class="small">Aún no has tomado una foto. Dale al botón de la cámara 👆</div>', unsafe_allow_html=True)
else:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("#### 👁️ Vista previa")
        st.image(
            preview_image if preview_image is not None else img_file_buffer,
            use_container_width=True,
            caption="Imagen procesada" if filtro == "Con Filtro" else "Imagen original"
        )

    with c2:
        st.markdown("#### 🧾 Texto detectado")
        if texto_ocr and texto_ocr.strip():
            # Escapar HTML y convertir saltos de línea SIN usar backslashes dentro del f-string
            safe_text = (
                texto_ocr.replace("&", "&amp;")
                         .replace("<", "&lt;")
                         .replace(">", "&gt;")
                         .replace("\n", "<br>")
            )
            st.markdown(f"<div class='codebox'>{safe_text}</div>", unsafe_allow_html=True)

            # Botón para descargar el resultado como .txt
            buffer_txt = BytesIO(texto_ocr.encode('utf-8'))
            st.download_button(
                label="⬇️ Descargar TXT",
                data=buffer_txt,
                file_name="resultado_ocr.txt",
                mime="text/plain",
                use_container_width=True
            )
        else:
            st.info("No se detectó texto. Acerca más la cámara, mejora la luz o prueba con **Con Filtro**.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Footer minimal
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='small' style='text-align:center; margin-top:24px;'>"
    "Hecho con Streamlit + OpenCV + Tesseract • Tema oscuro legible ✨"
    "</div>",
    unsafe_allow_html=True
)


