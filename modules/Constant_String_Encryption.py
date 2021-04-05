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

    def find_string(self, output_dir, putDecryptFile, ignorefile):
        smali_list = []
        exclude_str = []
        if(putDecryptFile):
            cf = open("resources\\DecryptString.smali", "r")
            c_file = cf.read()
            cf.close()
            f = open(output_dir + "\\DecryptString.smali", "w")
            f.write(c_file)
            f.close()
        for path, subdirs, files in os.walk(output_dir):
            exclude_dir = set(['android', 'androidx', 'kotlin', 'kotlinx','google'])
            subdirs[:] = [d for d in subdirs if d not in exclude_dir]
            only_file = set(['MainActivity.smali'])
            files[:] = [f for f in files if f not in ignorefile]
            #files[:] = [f for f in files if f in only_file]
            for name in files:
                if ".smali" in name:
                    smali_list.append(PurePath(path, name))
        for filename in smali_list:
            with open(filename, 'r', encoding="utf-8") as rf:
                data = rf.read()
                c_strings = re.findall(r"const-string\s.+,\s\".+\"", data)
                c_strings = list(dict.fromkeys(c_strings))
                method_strings = ''.join(re.findall(r".method\s.+[\s\S]+", data)).split('.method')
                for x in range(len(method_strings)):
                    if len(method_strings[x]) > 0:
                        method_strings[x] = ".method" + method_strings[x]
                method_strings = list(dict.fromkeys(method_strings))
                filtered_method = []
                for x in method_strings:
                    for y in c_strings:
                        if (y in x):
                            filtered_method.append(x)
                if len(c_strings) > 0:
                    for cstring in c_strings:
                        if cstring not in exclude_str:
                            try:
                                string_value = re.search(r"const-string\s[v|p]\d+,\s\"(.+)\"", cstring).group(1)
                                encrypt_string = self.encrypt(string_value)
                                var_name = re.search(r"const-string\s([v|p]\d+)", cstring)
                                temp_string = "const-string "+var_name.group(1)+", \""+encrypt_string+"\"\n"+\
                                              "\tinvoke-static {"+ var_name.group(1)+"}, Lcom/DecryptManager" \
                                              "/DecryptString/DecryptString;->decrypt (Ljava/lang/String;)" \
                                              "Ljava/lang/String;\n\tmove-result-object "+var_name.group(1)
                                data = re.sub(re.escape(cstring), temp_string, data)
                            except Exception as e:
                                print(str(filename) + " >> String: " + cstring + " >> " + str(e))
                    with open(filename, 'w', encoding="utf-8") as wf:
                        wf.write(data)
                        wf.close()