import wave
import streamlit as st

def encode_aud_data():
    nameoffile = st.text_input("Enter the name of the audio file (with .wav extension):")
    data = st.text_input("Enter the secret message:")
    
    if not nameoffile or not data:
        return
    
    if st.button("Encode"):
        res = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))
        st.write("\nThe string after binary conversion:", res)
        length = len(res)
        st.write("\nLength of binary after conversion:", length)

        song = wave.open(nameoffile, mode='rb')
        nframes = song.getnframes()
        frames = song.readframes(nframes)
        frame_list = list(frames)
        frame_bytes = bytearray(frame_list)

        data = data + '*^*^*'

        result = []
        for c in data:
            bits = bin(ord(c))[2:].zfill(8)
            result.extend([int(b) for b in bits])

        j = 0
        for i in range(len(result)):
            res = bin(frame_bytes[j])[2:].zfill(8)
            if res[-4] == str(result[i]):
                frame_bytes[j] = frame_bytes[j] & 253
            else:
                frame_bytes[j] = (frame_bytes[j] & 253) | 2
                frame_bytes[j] = (frame_bytes[j] & 254) | result[i]
            j += 1
        
        frame_modified = bytes(frame_bytes)

        stegofile = nameoffile
        with wave.open(stegofile, 'wb') as fd:
            fd.setparams(song.getparams())
            fd.writeframes(frame_modified)

        st.success("Data encoded successfully in the audio file.")
        song.close()

def decode_aud_data():
    nameoffile = st.text_input("Enter the name of the file to be decoded (with .wav extension):")
    
    if not nameoffile:
        st.warning("Please enter the filename.")
        return
    
    song = wave.open(nameoffile, mode='rb')

    nframes = song.getnframes()
    frames = song.readframes(nframes)
    frame_list = list(frames)
    frame_bytes = bytearray(frame_list)

    extracted = ""
    p = 0
    for i in range(len(frame_bytes)):
        if p == 1:
            break
        res = bin(frame_bytes[i])[2:].zfill(8)
        if res[-2] == '0':
            extracted += res[-4]
        else:
            extracted += res[-1]
    
        all_bytes = [extracted[i: i+8] for i in range(0, len(extracted), 8)]
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "*^*^*":
                st.success("The decoded data was: " + decoded_data[:-5])
                p = 1
                break  

def aud_steg():
    st.header("Audio Steganography")

    choice = st.sidebar.selectbox("Choose an option", ["Encode Text Message", "Decode Text Message"])

    if choice == "Encode Text Message":
        st.subheader("Encode Text Message in Audio File")
        encode_aud_data()

    elif choice == "Decode Text Message":
        st.subheader("Decode Text Message from Audio File")
        decode_aud_data()

if __name__ == "__main__":
    aud_steg()
