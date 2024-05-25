import cv2
import numpy as np
import streamlit as st
import tempfile
import os

global secret_data

def msg_to_binary(msg):
    if type(msg) == str:
        result = ''.join([format(ord(i), "08b") for i in msg])
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result = [format(i, "08b") for i in msg]
    elif type(msg) == int or type(msg) == np.uint8:
        result = format(msg, "08b")
    else:
        raise TypeError("Input type is not supported in this function")
    return result

def KSA(key):
    key_length = len(key)
    S = list(range(256))
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S

def PRGA(S, n):
    i = 0
    j = 0
    key = []
    while n > 0:
        n = n - 1
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        key.append(K)
    return key

def preparing_key_array(s):
    return [ord(c) for c in s]

def encryption(plaintext, key):
    S = KSA(key)
    keystream = np.array(PRGA(S, len(plaintext)))
    plaintext = np.array([ord(i) for i in plaintext])
    cipher = keystream ^ plaintext
    ctext = ''.join([chr(c) for c in cipher])
    return ctext

def decryption(ciphertext, key):
    S = KSA(key)
    keystream = np.array(PRGA(S, len(ciphertext)))
    ciphertext = np.array([ord(i) for i in ciphertext])
    decoded = keystream ^ ciphertext
    dtext = ''.join([chr(c) for c in decoded])
    return dtext

def embed_data(frame, data):
    if len(data) == 0:
        raise ValueError('Data entered to be encoded is empty')

    data += '*^*^*'
    binary_data = msg_to_binary(data)
    length_data = len(binary_data)

    index_data = 0

    for i in frame:
        for pixel in i:
            r, g, b = msg_to_binary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2)
                index_data += 1
            if index_data >= length_data:
                break
    return frame

def extract_data(frame):
    data_binary = ""
    for i in frame:
        for pixel in i:
            r, g, b = msg_to_binary(pixel)
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]

    total_bytes = [data_binary[i: i + 8] for i in range(0, len(data_binary), 8)]
    decoded_data = ""
    terminator = "*^*^*"
    terminator_index = 0

    for byte in total_bytes:
        char = chr(int(byte, 2))
        decoded_data += char
        if decoded_data.endswith(terminator):
            terminator_index = len(decoded_data) - len(terminator)
            break

    if terminator_index > 0:
        final_decoded_msg = decoded_data[:terminator_index]
        final_decoded_msg = decryption(final_decoded_msg)
        return final_decoded_msg
    else:
        return None

def encode_video_data(cover_video_path, secret_data, frame_number, key):
    cap = cv2.VideoCapture(cover_video_path)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('stego_video.mp4', fourcc, 25.0, (frame_width, frame_height))
    frame_number = min(frame_number, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    current_frame = 0

    while cap.isOpened() and current_frame < frame_number:
        ret, frame = cap.read()
        if not ret:
            break
        if current_frame == frame_number - 1:
            encrypted_data = encryption(secret_data, key)
            frame = embed_data(frame, encrypted_data)
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()

def decode_video_data(stego_video_path, frame_number, key):
    cap = cv2.VideoCapture(stego_video_path)
    frame_number = min(frame_number, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    current_frame = 0

    while cap.isOpened() and current_frame < frame_number:
        ret, frame = cap.read()
        if not ret:
            break
        if current_frame == frame_number - 1:
            secret_data = extract_data(frame)
            if secret_data is not None:
                secret_data = decryption(secret_data, key)
                cap.release()
                return secret_data
            else:
                return None

        current_frame += 1

    cap.release()
    return None

def vid_steg():
    st.header("Video Steganography")

    operation = st.sidebar.selectbox("Select Operation", ["Encode", "Decode"])

    if operation == "Encode":
        st.subheader("Encode Data into Video")
        cover_video_path = st.file_uploader("Upload Cover Video")
        if cover_video_path is not None:
            frame_number = st.number_input("Enter Frame Number to Embed Data", value=1, step=1)
            secret_data = st.text_area("Enter Data to be Encoded")
            
            # Add widget to input encryption key
            key = st.text_input("Enter Encryption Key")
            
            if st.button("Encode"):
                # Check if key is provided
                if not key:
                    st.error("Please provide an encryption key.")
                else:
                    encode_video_data(cover_video_path.name, secret_data, frame_number, preparing_key_array(key))
                    st.success("Data encoded successfully!")
                    st.write("Embedded Data:", secret_data)

                    # Display encoded video
                    st.write("Encoded Video:")
                    video_file=open('cover_video.mp4','rb')
                    video_bytes= video_file.read()
                    st.video(video_bytes)

    elif operation == "Decode":
        st.header("Decode Data from Video")
        stego_video = st.file_uploader("Upload Stego Video")
        if stego_video is not None:
            frame_number = st.number_input("Enter Frame Number to Extract Data", value=1, step=1)
            
            # Add widget to input decryption key
            key = st.text_input("Enter Decryption Key")
            
            if st.button("Decode"):
                # Check if key is provided
                if not key:
                    st.error("Please provide a decryption key.")
                else:
                    secret_data = decode_video_data('stego_video.mp4', frame_number, preparing_key_array(key))
                    if secret_data is not None:
                        st.success("Data extracted successfully!")
                        st.write("Extracted Data:", secret_data)
                    else:
                        st.success("Data extracted successfully")

                    # Display decoded video
                    st.write("Decoded Video:")
                    video_file=open('cover_video.mp4','rb')
                    video_bytes= video_file.read()
                    st.video(video_bytes)

if __name__ == "__main__":
   vid_steg()
