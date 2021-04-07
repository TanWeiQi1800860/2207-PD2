import os
import re
from pathlib import PurePath

safe_functionNames_list = ["aManager", "getAndID", "getPhoneInfo", "getUserList", "getMAC", "isNetworkAvailable",
                           "getWifiInfo", "getContactList", "readreceivedMessages", "readSentMessages", "sendmessages",
                           "pManager", "isServerAvailable", "establishNetworkConn",
                           "sendEmail", "createEmailMessage",
                           "verifyFromSQLite",
                           "postDataToSQLite",
                           "getAllUser", "addUser", "checkUser",
                           "FindArchives", "encrypt11", "encrypt", "decrypt", "decrypt11", "generateSalt"]

safe_classNames_list = ["MessageReceiver", "Utils", "getPhoneInfo"]
variable_numberCount = 0
reserved_words_list = ["intent"]


def identify_files(debug_input_dir, ignorefile):
    files_toObfuscate = []
    included_FileExts = set(['.kt', '.java'])
    excluded_Dirs = set(['.idea', 'build'])
    for subdir, dirs, files in os.walk(debug_input_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_Dirs]
        files[:] = [f for f in files if f not in ignorefile]
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension in included_FileExts:
                files_toObfuscate.append(PurePath(subdir, file))
    return files_toObfuscate


def get_ClassNames(filePath_list):
    class_dict = {}
    for file in filePath_list:
        Filename = os.path.basename(file)
        if Filename.endswith(".java") or Filename.endswith(".kt"):
            with open(file) as fp:
                while True:
                    line = fp.readline()
                    if re.search(r"class\s(.+?)\(", str(line)):
                        regex_group = re.search(r"class\s(.+?)\(", str(line)).group(1)
                        if re.search(r"(.+?)(\s*)(\:)", regex_group):
                            filtered_regex_group = re.search(r"(.+?)(\s*)(\:)", regex_group).group(1)
                            if regex_group in class_dict:
                                class_dict[filtered_regex_group] += 1
                            else:
                                class_dict[filtered_regex_group] = 1
                        else:
                            if regex_group in class_dict:
                                class_dict[regex_group] += 1
                            else:
                                class_dict[regex_group] = 1

                    if re.search(r"(public|private) class\s(.+?)(\s+)\{$", str(line)):
                        print("This line may contain a public or private class: ", line)

                    if not line:
                        break
    return class_dict


def get_FunctionNames(filePath_list):
    function_dict = {}
    function_details = []
    for file in filePath_list:
        Filename = os.path.basename(file)
        if Filename.endswith(".kt"):
            with open(file) as fp:
                line_number = 1
                while True:
                    line = fp.readline()
                    if re.search(r"fun\s(.+?)\(", str(line)):
                        function_name = re.search(r"fun\s(.+?)\(", line).group(1)
                        function_name = function_name.rstrip()
                        if function_name in function_dict:
                            function_dict[function_name] += 1
                        else:
                            function_dict[function_name] = 1
                        indentation_size = len(line) - len(line.lstrip())
                        function_details.append([file, function_name, line_number, indentation_size])
                    line_number += 1
                    if not line:
                        break
        if Filename.endswith(".java"):
            with open(file) as fp:
                while True:
                    line = fp.readline()
                    if re.search(r"(public|protected|private|static)\s[\w\[\]<>]+\s([\[\]\s])*(\w+)\s*([^)])",
                                 str(line)):
                        captured_name = re.search(
                            r"(public|protected|private|static)\s[\w\[\]<>]+\s([\[\]\s])*(\w+)\s*([^)])", line).group(3)
                        if "class" in line:
                            print("The java class name is:", captured_name)
                        else:
                            if captured_name in function_dict:
                                function_dict[captured_name] += 1
                            else:
                                function_dict[captured_name] = 1

                    if not line:
                        break
    return function_dict


def rename_functionNames(dictionary_of_functions):
    function_renamed_dict = {}
    count = 1
    for key, value in dictionary_of_functions.items():
        function_renamed_dict[key] = "function" + str(count)
        count += 1
    return function_renamed_dict


def sub_functionNames(dictionary_of_renamedFunctions, filePath_list):
    count = 0
    for key, value in dictionary_of_renamedFunctions.items():
        function_name = key
        if function_name in safe_functionNames_list:
            count += 1
            for filename in filePath_list:
                reading_file = open(filename, "r")
                new_file_content = ""
                for line in reading_file:
                    stripped_line = line.rstrip()
                    if re.search(rf"\b({function_name})\b(\s*)(\()", str(stripped_line)):
                        new_line = re.sub(rf"\b({function_name})\b(\s*)(\()", rf"{value}\2\3", str(stripped_line))
                        new_file_content += new_line + "\n"
                    else:
                        new_file_content += stripped_line + "\n"
                reading_file.close()

                writing_file = open(filename, "w")
                writing_file.write(new_file_content)
                writing_file.close()


def get_VarNames(filePath_list):
    global variable_numberCount
    variable_dict = {}
    for full_fileName in filePath_list:
        filename = os.path.basename(full_fileName)
        if filename.endswith(".java"):
            with open(full_fileName) as fp:
                while True:
                    line = fp.readline()
                    stripped_line = line.rstrip()
                    if re.search(r"\b\s+\b(.[^ ]+?)\s*=|\[\]\s(.+)\s*=\s", str(stripped_line)):
                        captured_java_varName = re.search(r"\b\s+\b(.[^ ]+?)\s*=|\[\]\s(.+)\s*=\s",
                                                          str(stripped_line)).group(1)
                        if captured_java_varName is None:
                            captured_java_varName = re.search(r"\b\s+\b(.[^ ]+?)\s*=|\[\]\s(.+)\s*=\s",
                                                              str(stripped_line)).group(2)
                        captured_java_varName = captured_java_varName.strip()
                        if captured_java_varName in variable_dict:
                            variable_dict[captured_java_varName] += 1
                        else:
                            variable_dict[captured_java_varName] = 1
                        continue

                    if (re.search(r"\b(int|float|char|boolean|String|long|float|double|short\s+)\b(.+?)(\s*)(\=|\;)",
                                  str(stripped_line))):
                        captured_java_varName = re.search(
                            r"\b(int|float|char|boolean|String|long|float|double|short\s+)\b(.+?)(\s*)(\=|\;)",
                            str(stripped_line)).group(2)
                        captured_java_varName = captured_java_varName.strip()
                        if captured_java_varName in variable_dict:
                            variable_dict[captured_java_varName] += 1
                        else:
                            variable_dict[captured_java_varName] = 1
                        continue
                    if not line:
                        break
            fp.close()
        if filename.endswith(".kt"):
            var_list = []
            with open(full_fileName) as fp:
                while True:
                    line = fp.readline()
                    if re.search(r"(var|val)(\s+)(.+?)(\s*)(\=|\:)", str(line)):
                        if re.search(r"(const)(\s+)(val|var)", str(line)):
                            pass
                        else:
                            regex_group = re.search(r"(var|val)(\s+)(.+?)(\s*)(\=|\:)", str(line)).group(1, 2, 3)
                            regex_group = list(regex_group)
                            var_list.append(regex_group)

                            captured_kotlin_varName = re.search(r"(var|val)(\s+)(.+?)(\s*)(\=|\:)", str(line)).group(3)
                            if captured_kotlin_varName in variable_dict:
                                variable_dict[captured_kotlin_varName] += 1
                            else:
                                variable_dict[captured_kotlin_varName] = 1
                    if not line:
                        break
                fp.close()
    variable_dict = rename_VarNames(variable_dict)
    print(variable_numberCount)
    for key, value in variable_dict.items():
        print(key, value)
    sub_VarNames(variable_dict, filePath_list)


def rename_VarNames(variable_dict):
    global variable_numberCount
    for key, value in variable_dict.items():
        variable_numberCount += 1
        variable_dict[key] = "var" + str(variable_numberCount)
    return variable_dict


def sub_VarNames(variable_dict, filePath_list):
    for key, value in variable_dict.items():
        variable_name = key
        print("The variable name is: ", variable_name, "and the replacement is: ", value)
        for full_fileName in filePath_list:
            filename = os.path.basename(full_fileName)
            if filename.endswith(".java"):
                reading_file = open(full_fileName, "r")
                new_file_content = ""
                for line in reading_file:
                    stripped_line = line.rstrip()
                    if re.search(rf"\b{variable_name}\b", str(stripped_line)):
                        new_line = re.sub(
                            rf"(\s)\b{variable_name}\b(\s)|(|\(|\s|\[|\.\.|!|\+|\+=|,|\$|{{)\b{variable_name}\b(\)*)",
                            rf"\1\3{value}\2\4", stripped_line)
                        print("The new java line is: ", new_line)
                        print(new_line)
                        print("\n")
                        new_file_content += new_line + "\n"
                    else:
                        new_file_content += stripped_line + "\n"
                    if not line:
                        reading_file.seek(0)

                reading_file.close()

                writing_file = open(full_fileName, "w")
                writing_file.write(new_file_content)
                writing_file.close()
            if filename.endswith(".kt"):
                with open(full_fileName, "r") as reading_file:
                    new_file_content = ""
                    for line in reading_file:
                        stripped_line = line.rstrip()
                        match_string = re.search(rf"(var|val)(\s)\b{variable_name}\b(\s*=\s*)(\b{variable_name}\b)",
                                                 str(stripped_line))
                        if match_string is not None:
                            if match_string.group(4) in reserved_words_list:
                                new_line = re.sub(rf"(var|val)(\s)\b{variable_name}\b(\s*=\s*)(.+)",
                                                  rf"\1\2{value}\3\4",
                                                  stripped_line)
                                print(stripped_line)
                                print(new_line)
                                print("\n")
                                new_file_content += new_line + "\n"
                            else:
                                new_file_content += stripped_line + "\n"
                        else:
                            if re.search(rf"\b{variable_name}\b", str(stripped_line)):
                                new_line = re.sub(
                                    rf"(\s!*)\b{variable_name}\b(\s)|^[^fun]*$(\(|\s|\[|\.\.|!|\+|\+=|,|\$|{{)\b{variable_name}\b(\)*)|(other\.)\b{variable_name}\b",
                                    rf"\1\3\5{value}\2\4", stripped_line)
                                print(stripped_line)
                                print(new_line)
                                print("\n")
                                new_file_content += new_line + "\n"
                            else:
                                new_file_content += stripped_line + "\n"

                        if not line:
                            reading_file.seek(0)

                    reading_file.close()

                    writing_file = open(full_fileName, "w")
                    writing_file.write(new_file_content)
                    writing_file.close()
