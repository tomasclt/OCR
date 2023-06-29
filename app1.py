import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

st.title("Reconocimiento óptico de Caracteres")

img_file_buffer = st.camera_input("Toma una Foto")

if img_file_buffer is not None:
    # To read image file buffer with OpenCV:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    pil_image = Image.open(bytes_data)
    text = pytesseract.image_to_string(pil_image)
    st.write(text)

    # Check the type of cv2_img:
    # Should output: <class 'numpy.ndarray'>
    #st.write(type(cv2_img))

    # Check the shape of cv2_img:
    # Should output shape: (height, width, channels)
    #st.write(cv2_img.shape)

    #img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    #st.write(pytesseract.image_to_string(img_rgb))

    #img_rgb = Image.frombytes('RGB', cv2_img.shape[:2], cv2_img, 'raw', 'BGR', 0, 0)
    #text_in=pytesseract.image_to_string(img_rgb)
    #st.write(text_in)


