import re
import os

from pathlib import PurePath

debug_op_codes = [
                r".source\s.+",
                r".line\s\d+",
                ".prologue",
                ".epilogue",
                #r".local\sv\d+",
                #".end local",
                #".restart local",
                #".param\sp\d+,\s.+\s+"
            ]

def Find_method_debug(output_dir, ignorefile):
    smali_list = []
    for path, subdirs, files in os.walk(output_dir):
        exclude = set(['android', 'androidx', 'kotlin', 'kotlinx', 'google'])
        subdirs[:] = [d for d in subdirs if d not in exclude]
        if(len(ignorefile) > 0):
            files[:] = [f for f in files if f not in ignorefile]
        for name in files:
            if ".smali" in name:
                smali_list.append(PurePath(path, name))
    for filename in smali_list:
        with open(filename, 'r', encoding="utf-8") as rf:
            data = rf.read()
            for code in debug_op_codes:
                data = re.sub(code, '', data)
            with open(filename, 'w', encoding="utf-8") as wf:
                wf.write(data)
                wf.close()