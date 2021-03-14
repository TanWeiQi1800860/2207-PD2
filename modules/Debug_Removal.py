import re
import os

from pathlib import PurePath

debug_op_codes = [
                ".source ",
                ".line ",
                ".prologue",
                ".epilogue",
                ".local ",
                ".end local",
                ".restart local",
                ".param ",
            ]

def Find_method_debug(output_dir):
    smali_list = []
    for path, subdirs, files in os.walk(output_dir):
        exclude = set(['android', 'androidx', 'kotlin', 'kotlinx', 'google'])
        subdirs[:] = [d for d in subdirs if d not in exclude]
        exclude_file = set([])
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
                        data = re.sub(re.escape(line_start), '', data)
                        if_cond = if_cond + 1
                    except Exception as e:
                        print(str(filename) + " >> String: " + cstring + " >> " + str(e))
                with open(filename, 'w', encoding="utf-8") as wf:
                    wf.write(data)
                    wf.close()

Find_method_debug(output_dir)