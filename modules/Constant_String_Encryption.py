import os
from pathlib import PurePath
import re

from Crypto.Cipher import AES
from base64 import b64encode

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

class AESCipher(object):
    def __init__(self, key):
        self.block_size = AES.block_size
        self.key = key

    def encrypt(self, plain_text):
        plain_text = pad(plain_text)
        #iv = Random.new().read(self.block_size)
        iv = b'0000000000000000'
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted_text = cipher.encrypt(plain_text.encode())
        return b64encode(encrypted_text).decode("utf-8")

    def find_string(self, output_dir, putDecryptFile):
        smali_list = []
        if(putDecryptFile):
            cf = open("resources\\DecryptString.smali", "r")
            c_file = cf.read()
            cf.close()
            f = open(output_dir + "\\DecryptString.smali", "w")
            f.write(c_file)
            f.close()
        for path, subdirs, files in os.walk(output_dir):
            exclude = set(['android', 'androidx', 'kotlin', 'kotlinx','google'])
            subdirs[:] = [d for d in subdirs if d not in exclude]
            exclude_file = set(['DecryptString.smali', 'BuildConfig.smali'])
            files[:] = [f for f in files if f not in exclude_file]
            for name in files:
                if ".smali" in name:
                    smali_list.append(PurePath(path, name))
        for filename in smali_list:
            with open(filename, 'r', encoding="utf-8") as rf:
                data = rf.read()
                c_strings = re.findall(r"const-string\s.+,\s\"(.+)\"", data)
                c_strings = list(dict.fromkeys(c_strings))
                if (len(c_strings) > 0):
                    for cstring in c_strings:
                        try:
                            encrypt_string = self.encrypt(cstring)
                            var_name = re.search(r"const-string\s(.+),\s\"" + re.escape(cstring) +"\"", data)
                            temp_string = "const-string "+var_name.group(1)+", \""+encrypt_string+"\"\n"+\
                                          "\tinvoke-static {"+ var_name.group(1)+"}, Lcom/DecryptManager" \
                                          "/DecryptString/DecryptString;->decrypt (Ljava/lang/String;)Ljava/lang/Str" \
                                          "ing;\n\tmove-result-object "+var_name.group(1)
                            data = re.sub(r"const-string\s(.+),\s\"" + re.escape(cstring) +"\"", temp_string, data)
                        except Exception as e:
                            print(str(filename) + " >> String: " + cstring + " >> " + str(e))
                    with open(filename, 'w', encoding="utf-8") as wf:
                        wf.write(data)
                        wf.close()