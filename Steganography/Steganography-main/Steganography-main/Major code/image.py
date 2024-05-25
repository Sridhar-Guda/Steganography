import streamlit as st
import cv2
import numpy as np

# IMAGE STEGANOGRAPHY FUNCTIONS

def msgtobinary(msg):
    if isinstance(msg, str):
        return ''.join([format(ord(i), "08b") for i in msg])
    elif isinstance(msg, bytes) or isinstance(msg, np.ndarray):
        return [format(i, "08b") for i in msg]
    elif isinstance(msg, int) or isinstance(msg, np.uint8):
        return format(msg, "08b")
    else:
        raise TypeError("Input type is not supported in this function")

def encode_img_data(text, img_name):
    img = cv2.imread("Sample_cover_files/cover_image.jpg")
    if img is None:
        st.error("Failed to read the image.")
        return

    data = text
    if len(data) == 0:
        st.error('Data entered to be encoded is empty')
        return

    no_of_bytes = len(img) * len(img[0]) * 3 // 8
    st.text("\t\nMaximum bytes to encode in Image : {}".format(no_of_bytes))

    if len(data) > no_of_bytes:
        st.error("Insufficient bytes Error, Need Bigger Image or give Less Data !!")
        return

    data += '*^*^*'
    binary_data = msgtobinary(data)

    length_data = len(binary_data)
    st.text("\nThe Length of Binary data: {}".format(length_data))

    index_data = 0
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
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
    cv2.imwrite(img_name, img)
    st.success("\nEncoded the data successfully in the Image and the image is successfully saved with name " + img_name)
    st.write("Number of bits encoded:", index_data)
    st.image(img_name, caption="Encoded Image", use_column_width=True)

def decode_img_data(img):
    data_binary = ""
    for row in img:
        for pixel in row:
            r, g, b = msgtobinary(pixel)
            data_binary += r[-1]
            data_binary += g[-1]
            data_binary += b[-1]

    decoded_data = ""
    for i in range(0, len(data_binary), 8):
        byte = data_binary[i:i + 8]
        decoded_data += chr(int(byte, 2))
        if decoded_data[-5:] == "*^*^*":
            return decoded_data[:-5]

    return None

# STREAMLIT INTERFACE

def img_steg():
    st.title("Image Steganography")

    st.sidebar.title("Choose Operation")
    operation = st.sidebar.radio("Operation", ["Encode", "Decode"])

    if operation == "Encode":
        st.header("Encode Message into Image")

        text = st.text_area("Enter Message to Encode")
        img_name = st.text_input("Enter the name of the New Image (Stego Image) after Encoding (with extension)", value="encoded_image.png")
        if st.button("Encode"):
            try:  
                encode_img_data(text, img_name)
                
            except Exception as e:
                st.error(f"Error: {e}")

    elif operation == "Decode":
        st.header("Decode Message from Image")
        image_path = st.file_uploader("Upload decoded Image", type=["jpg", "png", "jpeg"])
        if image_path is not None:
            #encoded_image = cv2.imdecode(np.frombuffer(image_path.read(), np.uint8), 1)
            encoded_image = cv2.imdecode(np.fromstring(image_path.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            encoded_image_bgr = cv2.cvtColor(encoded_image, cv2.COLOR_RGB2BGR)
            
            if st.button("Decode"):
                try:
                    decoded_message = decode_img_data(encoded_image)
                    if decoded_message:
                        st.image(encoded_image_bgr, caption="Encoded Image", use_column_width=True)
                        st.success(f"Decoded Message: {decoded_message}")
                    else:
                        st.warning("No hidden message found in the image.")
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
   img_steg()