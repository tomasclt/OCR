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
# Estilos (solo estética)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
/* Tipografía y container */
html, body, [class*="css"]  {
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji','Segoe UI Emoji';
}
main .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 900px;}

/* Tarjetas */
.card {
  background: #ffffff;
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 18px;
  padding: 18px 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.06);
}
.header { display:flex; align-items:center; gap:.6rem; margin-bottom:.5rem; }
.badge {
  font-size: .75rem; padding: .25rem .55rem; border-radius: 999px;
  background: #EEF2FF; color:#3730A3; border: 1px solid #E0E7FF; font-weight: 600;
}
h1, h2, h3 { letter-spacing: -0.02em; }
footer {visibility: hidden;}

/* Sidebar con gradiente */
section[data-testid="stSidebar"] > div:first-child {
  background: linear-gradient(180deg, #0EA5E9 0%, #6366F1 100%);
}
section[data-testid="stSidebar"] * { color: #f7faff !important; }
div[role="radiogroup"] label { color:#0f172a !important; } /* radios dentro del main */

/* Caja tipo terminal para el texto OCR */
.codebox {
  background:#0b1220; color:#e2e8f0; border-radius:14px; padding:14px 16px;
  border:1px solid rgba(255,255,255,.08);
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
}
.small { opacity:.85; font-size:.9rem; }
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
                mime="text/plain"
            )
        else:
            st.info("No se detectó texto. Acerca más la cámara, mejora la luz o prueba con **Con Filtro**.")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Footer minimal
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='small' style='text-align:center; margin-top:24px;'>"
    "Hecho con Streamlit + OpenCV + Tesseract • vEstética 💅"
    "</div>",
    unsafe_allow_html=True
)


