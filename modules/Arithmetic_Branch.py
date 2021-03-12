import os
import random
import re
from pathlib import PurePath

word_list_path = "resources\\words_list.txt"
nop_py_path = "modules\\Nop_Code.py"

def get_word_list():
    with open(word_list_path, 'r', encoding="utf-8") as wl:
        w_list = wl.read().split()
        wl.close()
    return w_list
word_list = get_word_list()

def Arithmetic(if_cond):
    left_ari = random.randrange(1, 10)
    right_ari = random.randrange(11, 20)
    operations = ['add-int/lit8', '-', 'div-int/lit8', 'mul-int/lit8']
    operator = operations[random.randrange(1, len(operations))]
    equal_ari = random.randrange(1000, 2000)
    if_string = "\n\tconst/16 v2, " + hex(equal_ari) + "\n\tif-ne v1, v2, :cond_" + str(if_cond) + "\n"
    if operator == '-':
        return "\n\tconst/16 v0, " + hex(left_ari) + "\n\tadd-int/lit8 v1,v0, -" + hex(right_ari) + if_string
    else:
        return "\n\tconst/16 v0, " + hex(left_ari) + "\n\t" + operator + " v1,v0, " + hex(right_ari) + if_string


def PrintFunction(if_cond):
    word_string = random.choice(word_list) + random.choice(word_list) + random.choice(word_list)
    return "sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;\n\tconst-string v2, \""+ word_string + "\"" \
           "\n\tinvoke-virtual {v1, v2}, Ljava/io/PrintStream;->print(Ljava/lang/Object;)V\n\t:cond_" + str(if_cond)


def Find_method(output_dir, allow_nop_code):
    smali_list = []
    if(allow_nop_code):
        print("[+] Adding Nop Code")
    for path, subdirs, files in os.walk(output_dir):
        exclude = set(['android', 'androidx', 'kotlin', 'kotlinx', 'google'])
        subdirs[:] = [d for d in subdirs if d not in exclude]
        exclude_file = set(['DecryptString.smali', 'BuildConfig.smali'])
        files[:] = [f for f in files if f not in exclude_file]
        for name in files:
            if ".smali" in name:
                smali_list.append(PurePath(path, name))
    for filename in smali_list:
        with open(filename, 'r', encoding="utf-8") as rf:
            data = rf.read()
            c_strings = re.findall(r".method\s.+\)V", data)
            c_strings = list(dict.fromkeys(c_strings))
            c_strings = [x for x in c_strings if
                         "<init>" not in x and "<clinit>" not in x and "android/widget/" not in x]
            method_strings = ''.join(re.findall(r".method\s.+[\s\S]+", data)).split('.method')
            for x in range(len(method_strings)):
                if (len(method_strings[x]) > 0):
                    method_strings[x] = ".method" + method_strings[x]
            method_strings = list(dict.fromkeys(method_strings))
            filtered_method = []
            for x in method_strings:
                for y in c_strings:
                    if (y in x):
                        filtered_method.append(x)
            if (len(c_strings) > 0):
                if_cond = 0
                for cstring in c_strings:
                    try:
                        line_start = ""
                        cond_exist = ""
                        for x in method_strings:
                            if x in filtered_method:
                                line_start = re.search(".line\s\d+", x).group()
                                cond_exist = re.search(":cond_(\d+)", x).group(1)
                                local_count = int(re.search(".locals\s(\d+)", x).group(1))
                                if local_count < 3:
                                    data = re.sub(re.escape(cstring) + "\s+.locals\s\d+",cstring + "\n\t.locals 3",data)
                        if cond_exist != None:
                            if_cond = int(cond_exist) + 1
                        temp_string = "\t" + Arithmetic(if_cond) + "\n\n\t" + Arithmetic(if_cond) + "\n\t" +\
                                      PrintFunction(if_cond) + "\n\n\t" + line_start
                        data = re.sub(re.escape(line_start), temp_string, data)
                        if allow_nop_code:
                            data = re.sub(r".end\smethod", "\tnop\n.end method", data)
                        if_cond = if_cond + 1
                    except Exception as e:
                        print(str(filename) + " >> String: " + cstring + " >> " + str(e))
                with open(filename, 'w', encoding="utf-8") as wf:
                    wf.write(data)
                    wf.close()

if(not os.path.exists(nop_py_path)):
    with open(nop_py_path, 'w', encoding="utf-8") as wf:
        data = "#This is a empty python file"
        wf.write(data)
        wf.close()