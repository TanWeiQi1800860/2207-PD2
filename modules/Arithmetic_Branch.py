import os
import random
import re
from pathlib import PurePath


def Arithmetic():
    left_ari = random.randrange(1, 10)
    right_ari = random.randrange(11, 20)
    operations = ['add-int/lit8', '-', 'div-int/lit8', 'mul-int/lit8']
    operator = operations[random.randrange(1, len(operations))]
    equal_ari = random.randrange(1000, 2000)
    if_string = "\n\tconst/16 v2, " + hex(equal_ari) + "\n\tif-ne v1, v2, :cond_0"
    if(operator== '-'):
        return "const/4 v0, " + hex(left_ari) + "\n\tadd-int/lit8" + " v1,v0, -" + hex(right_ari) + if_string
    else:
        return "const/4 v0, " + hex(left_ari) + "\n\t" + operator + " v1,v0, " + hex(right_ari) + if_string


def Find_method(output_dir):
    smali_list = []
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
            c_strings = [ x for x in c_strings if "<init>" not in x and "<clinit>" not in x]
            method_strings = ''.join(re.findall(r".method\s.+[\s\S]+", data)).split('.method')
            for x in range(len(method_strings)):
                if(len(method_strings[x]) > 0):
                    method_strings[x] = ".method" + method_strings[x]
            method_strings = list(dict.fromkeys(method_strings))
            filtered_method = []
            for x in method_strings:
                for y in c_strings:
                    if(y in x):
                        filtered_method.append(x)
            if (len(c_strings) > 0):
                for cstring in c_strings:
                    try:
                        line_start = ""
                        line_no = 2
                        for x in method_strings:
                            if x in filtered_method:
                                line_start = re.search(".line\s\d+", x).group()
                        line_list = re.findall(r".line\s\d+", temp_string, data)
                        for lines in line_list:
                            if int(lines.split(' ')[1]) >= int(line_start.split(' ')[1]):
                                data = re.sub(lines, lines.split(' ')[0] + str(int(lines.split(' ')[1]) + line_no),data)
                        temp_string = cstring + "\n\t" + Arithmetic() + "\n\n\t" + Arithmetic() + "\n"
                        data = re.sub(re.escape(cstring), temp_string, data)
                    except Exception as e:
                        print(str(filename) + " >> String: " + cstring + " >> " + str(e))
                with open(filename, 'w', encoding="utf-8") as wf:
                    wf.write(data)
                    wf.close()