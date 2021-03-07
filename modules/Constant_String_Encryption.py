import os
from pathlib import PurePath
import re
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode, b64decode


class AESCipher(object):
    def __init__(self, key):
        self.block_size = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def __pad(self, plain_text):
        number_of_bytes_to_pad = self.block_size - len(plain_text) % self.block_size
        ascii_string = chr(number_of_bytes_to_pad)
        padding_str = number_of_bytes_to_pad * ascii_string
        padded_plain_text = plain_text + padding_str
        return padded_plain_text

    @staticmethod
    def __unpad(plain_text):
        last_character = plain_text[len(plain_text) - 1:]
        bytes_to_remove = ord(last_character)
        return plain_text[:-bytes_to_remove]

    def encrypt(self, plain_text):
        plain_text = self.__pad(plain_text)
        iv = Random.new().read(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return b64encode(iv + encrypted_text).decode("utf-8")

    def decrypt(self, encrypted_text):
        encrypted_text = b64decode(encrypted_text)
        iv = encrypted_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        plain_text = cipher.decrypt(encrypted_text[self.block_size:]).decode("utf-8")
        return self.__unpad(plain_text)

    def find_string(self, output_dir):
        smali_list = []
        cf = open("resources\\DecryptString.smali", "r")
        c_file = cf.read()
        cf.close()
        f = open(output_dir + "\\DecryptString.smali", "w")
        f.write(c_file)
        f.close()
        for path, subdirs, files in os.walk(output_dir):
            exclude = set(['android', 'androidx', 'kotlin', 'kotlinx'])
            subdirs[:] = [d for d in subdirs if d not in exclude]
            for name in files:
                if ".smali" in name:
                    smali_list.append(PurePath(path, name))
        for filename in smali_list:
            with open(filename, 'r', encoding="utf-8") as rf:
                data = rf.read()
                c_strings = re.findall(r"const-string\s.+\s\"(.+)\"", data)
                if (len(c_strings) > 0):
                    for cstring in c_strings:
                        try:
                            data = re.sub(r"{}".format(cstring), r"{}".format(self.encrypt(cstring)), data)
                        except Exception as e:
                            print(str(filename) + " >> Line: " + cstring + " >> " + str(e))
                    with open(filename, 'w', encoding="utf-8") as wf:
                        wf.write(data)
                        wf.close()