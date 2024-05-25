import streamlit as st
from text import txt_steg
from image import img_steg
from audio import aud_steg
from video import vid_steg

# Title of the main application
st.title("Multi-media Steganography toolkit using python")

# Sidebar to navigate between different sections
option = st.sidebar.selectbox("Select an option", ["","TEXT", "IMAGE", "AUDIO", "VIDEO"])

# Conditionally execute the selected application 
if option == "":
    st.header("Types of steganography ")
    st.write("Text steganography- Involves hiding data within text documents")
    st.write("Image steganography- Conceals data within image files")
    st.write("Audio steganography- Hides information within audio files")
    st.write("Video steganography- Conceals data within video files")

if option == "TEXT":
    txt_steg()
elif option == "IMAGE":
    img_steg()
elif option == "AUDIO":
    aud_steg()
elif option == "VIDEO":
    vid_steg()
