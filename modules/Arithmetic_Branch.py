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


def Arithmetic(if_cond, v0, v1, v2):
    left_ari = random.randrange(1, 10)
    right_ari = random.randrange(11, 20)
    operations = ['add-int/lit8', '-', 'div-int/lit8', 'mul-int/lit8']
    operator = operations[random.randrange(1, len(operations))]
    equal_ari = random.randrange(1000, 2000)
    if_string = "\n\tconst/16 v" + v2 + ", " + hex(equal_ari) + "\n\tif-ne v" + v1 + ", v" + v2 + ", :cond_" + str(
        if_cond) + "\n"
    if operator == '-':
        return "const/16 v" + v0 + ", " + hex(left_ari) + "\n\tadd-int/lit8 v" + v1 + ",v" + v0 + ", -" + hex(
            right_ari) + if_string
    else:
        return "const/16 v" + v0 + ", " + hex(left_ari) + "\n\t" + operator + " v" + v1 + ",v" + v0 + ", " + hex(
            right_ari) + if_string


def PrintFunction(if_cond):
    word_string = random.choice(word_list) + random.choice(word_list) + random.choice(word_list)
    return "sget-object v1, Ljava/lang/System;->out:Ljava/io/PrintStream;\n\tconst-string v2, \"" + word_string + \
           "\"\n\tinvoke-virtual {v1, v2}, Ljava/io/PrintStream;->print(Ljava/lang/Object;)V\n\t:cond_" + str(if_cond)


def Find_method(output_dir, allow_Ari_Branch ,allow_nop_code):
    smali_list = []
    if (allow_nop_code):
        print("[+] Adding Nop Code")
    for path, subdirs, files in os.walk(output_dir):
        exclude = set(['android', 'androidx', 'kotlin', 'kotlinx', 'google'])
        subdirs[:] = [d for d in subdirs if d not in exclude]
        exclude_file = set(['DecryptString.smali', 'BuildConfig.smali', 'Grid$GridIterator.smali'])
        files[:] = [f for f in files if f not in exclude_file]
        for name in files:
            if ".smali" in name:
                smali_list.append(PurePath(path, name))
    for filename in smali_list:
        with open(filename, 'r', encoding="utf-8") as rf:
            cond_exist_found = False
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
                if(allow_Ari_Branch):
                    for cstring in c_strings:
                        try:
                            cond_exist = v0 = v1 = v2 = -1
                            for method in filtered_method:
                                if cstring in method and "$" not in cstring:
                                    if (re.search(".line\s\d+", method) != None):
                                        if (re.search(":cond_(\d+)", data) != None):
                                            cond_list = re.findall(":cond_(\d+)", data)
                                            for i in range(0, len(cond_list)):
                                                cond_list[i] = int(cond_list[i])
                                            cond_list.sort()
                                            cond_exist = cond_list[len(cond_list) - 1]
                                        if (re.search(".locals\s(\d+)", method) != None):
                                            local_list = re.findall("v(\d+)", method)
                                            for i in range(0, len(local_list)):
                                                local_list[i] = int(local_list[i])
                                            local_list.sort()
                                            if (len(local_list) < 1):
                                                local_last = 0
                                            else:
                                                local_last = local_list[len(local_list) - 1] + 1
                                        if(local_last < 10):
                                            v0 = str(local_last)
                                            v1 = str(local_last + 1)
                                            v2 = str(local_last + 2)
                                            data = re.sub(re.escape(cstring) + "\s+.locals\s\d+", cstring +
                                                          "\n\t.locals " + str(local_last + 3), data)
                                            if cond_exist != -1 and cond_exist_found == False:
                                                if_cond = int(cond_exist) + 1
                                                cond_exist_found = True
                                            next_line_after_line_start = re.search(".line\s\d+\s+[a-zA-Z]+.+", method).group()
                                            temp_string = Arithmetic(if_cond, v0, v1, v2) + "\t\n\t" + \
                                                          Arithmetic(if_cond, v0, v1, v2) + "\n\t" + \
                                                          PrintFunction(if_cond) + "\n\n\t" + next_line_after_line_start
                                            data = re.sub(re.escape(next_line_after_line_start), temp_string, data)
                                            if_cond = if_cond + 1
                                        break;
                        except Exception as e:
                            print(str(filename) + " >> String: " + cstring + " >> " + str(e))
                if allow_nop_code:
                    data = re.sub(r".end\smethod", "\tnop\n.end method", data)
                with open(filename, 'w', encoding="utf-8") as wf:
                    wf.write(data)
                    wf.close()


if (not os.path.exists(nop_py_path)):
    with open(nop_py_path, 'w', encoding="utf-8") as wf:
        data = "#This is a empty python file"
        wf.write(data)
        wf.close()
