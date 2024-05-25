import streamlit as st
import os

def txt_encode(text, nameoffile):
    l = len(text)
    i = 0
    add = ''
    while i < l:
        t = ord(text[i])
        if 32 <= t <= 64:
            t1 = t + 48
            t2 = t1 ^ 170       # 170: 10101010
            res = bin(t2)[2:].zfill(8)
            add += "0011" + res
        else:
            t1 = t - 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0110" + res
        i += 1
    res1 = add + "111111111111"
    length = len(res1)
    HM_SK = ""
    ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}
    word = []
    for line in open("Sample_cover_files/cover_text.txt", "r+"):
        word += line.split()
    i = 0
    if nameoffile:
        with open(nameoffile, "w+", encoding="utf-8") as file3:
            while i < len(res1):
                s = word[int(i / 12)]
                j = 0
                x = ""
                HM_SK = ""
                while j < 12:
                    x = res1[j + i] + res1[i + j + 1]
                    HM_SK += ZWC[x]
                    j += 2
                s1 = s + HM_SK
                file3.write(s1)
                file3.write(" ")
                i += 12
            t = int(len(res1) / 12)
            while t < len(word):
                file3.write(word[t])
                file3.write(" ")
                t += 1
        st.success("Stego file has successfully generated")
        st.write("The string after binary conversion applying all the transformation:", res1)
        st.write("Length of binary after conversion:", length)
    else:
        st.warning("Please enter the name of the Stego file.")

def txt_decode():
    ZWC_reverse = {u'\u200C': "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
    stego = st.text_input("Enter the name of the stego file to decode (with extension): ")
    if stego:
        if os.path.exists(stego):
            temp = ''
            with open(stego, "r", encoding="utf-8") as file4:
                for line in file4:
                    for words in line.split():
                        T1 = words
                        binary_extract = ""
                        for letter in T1:
                            if letter in ZWC_reverse:
                                binary_extract += ZWC_reverse[letter]
                        if binary_extract == "111111111111":
                            break
                        else:
                            temp += binary_extract
            i = 0
            a = 0
            b = 4
            c = 4
            d = 12
            final = ''
            while i < len(temp):
                t3 = temp[a:b]
                a += 12
                b += 12
                i += 12
                t4 = temp[c:d]
                c += 12
                d += 12
                if t3 == '0110':
                    decimal_data = int(t4, 2)
                    final += chr((decimal_data ^ 170) + 48)
                elif t3 == '0011':
                    decimal_data = int(t4, 2)
                    final += chr((decimal_data ^ 170) - 48)
            st.success("Message decoded from the stego file")
            st.write(final)
        else:
            st.error("File not found. Please make sure you provide the correct filename.")

def txt_steg():
    st.header("TEXT STEGANOGRAPHY")
    choice = st.sidebar.radio("Choose Operation", ("Encode the Text message", "Decode the Text message"))
    
    if choice == "Encode the Text message":
        st.subheader("Encode Text Message")
        text_to_encode = st.text_input("Enter data to be encoded:")
        nameoffile = st.text_input("Enter the name of the Stego file after Encoding (with extension): ")
        if st.button("Encode"):
            if text_to_encode:
                txt_encode(text_to_encode, nameoffile)
            else:
                st.warning("Please enter data to encode.")
    
    elif choice == "Decode the Text message":
        st.subheader("Decode Text Message")
        txt_decode()
if __name__ == "__main__":
    txt_steg()
