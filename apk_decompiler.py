import os
import shutil
import zipfile
import threading

from subprocess import call, DEVNULL

from GUI import MainFrame

tools_path = "tools"
dex2jar_path = tools_path + "\\dex2jar\\d2j-dex2jar.bat"
jd_path = tools_path + "\\jd-cli\\jd-cli.bat"
apktool_path = tools_path + "\\apktool\\apktool.jar"

def decompile_apk(apk_path, output_path,mainframe, verbose, odex_file=None):
    print("[+] Decompiling the apk\n")

    if verbose:
        stdout = None
        stderr = None
    else:
        stdout = DEVNULL
        stderr = DEVNULL

    if not os.path.exists(apk_path):
        print("[-] Error: couldn't find the apk!")
        return

    apk_name = os.path.splitext(os.path.basename(apk_path))[0]

    if os.path.exists("temp"):
        print("[~] Removing old temp directory")
        shutil.rmtree("temp")

    MainFrame.updatebar(mainframe)
    print("[+] Creating temp directory")
    os.makedirs("temp")
    print(os.getcwd())
    apk_zip = "temp/" + apk_name + ".zip"
    shutil.copy2(apk_path, apk_zip)

    apk_unziped_dir = "temp/" + apk_name + "_unziped"
    os.makedirs(apk_unziped_dir)

    zip_ref = zipfile.ZipFile(apk_zip, 'r')
    zip_ref.extractall(apk_unziped_dir)
    zip_ref.close()

    apk_classes = apk_unziped_dir + "/classes.dex"
    if odex_file is not None:
        apk_classes = odex_file

    if not os.path.exists(apk_classes):
        print("[-] Error: the apk doesn't have the classes.dex")
        return

    print("[+] Getting the jar")
    apk_jar = "temp/" + apk_name + ".jar"
    call(dex2jar_path + " " + apk_classes + " -o " + apk_jar, shell=True)

    apk_java = "temp/" + apk_name + "_java/src"
    t1 = threading.Thread(target=decom_jar, args=(apk_name, apk_jar,))
    t1.start()

    apk_re = "temp/" + apk_name + "_re"
    t2 = threading.Thread(target=re_apk, args=(apk_name, apk_path))
    t2.start()

    print("[+] Organizing everything")
    output_dir = os.path.join(output_path, apk_name)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    t1.join()
    MainFrame.updatebar(mainframe)
    t2.join()
    MainFrame.updatebar(mainframe)

    print("[+] Moving reverse engineering files")
    re_list = os.listdir(apk_re)
    for re_files in re_list:
        shutil.move(os.path.join(apk_re, re_files), output_dir)

    print("[+] Moving java files")
    shutil.move(apk_java, output_dir)

    if os.path.exists("temp"):
        print("[~] Removing temp directory")
        shutil.rmtree("temp")

    print("\n[+] Done decompiling the apk")

def verify_tools():
    if not os.path.exists(tools_path):
        print("[-] Error: 'tools' folder is missing")
        return False

    if not os.path.exists(dex2jar_path):
        print("[-] Error: 'dex2jar' it's missing from the tools directory")
        return False

    if not os.path.isfile(jd_path):
        print("[-] Error: 'jd-cli' it's missing from the tools directory")
        return False

    if not os.path.isfile(apktool_path):
        print("[-] Error: 'apktool' it's missing from the tools directory")
        return False

    return True

def decom_jar(apk_name, apk_jar):
    print("[+] Decompiling the jar")
    apk_java = "temp/" + apk_name + "_java/src"
    call(jd_path + " " + apk_jar + " -od " + apk_java, shell=False)

def re_apk(apk_name, apk_path):
    print("[+] Reverse engineering the apk")
    apk_re = "temp/" + apk_name + "_re"
    call("java -jar " + apktool_path + " d " + apk_path + " -o " + apk_re, shell=False)

def compile_apk(output_dir, apk_path):
    print("[+] Compiling the APK")
    apk_name = os.path.splitext(os.path.basename(apk_path))[0]
    call("java -jar " + apktool_path + " b " + output_dir+ "/"+apk_name, shell=False)
    if os.path.exists(output_dir+"/"+apk_name+".apk"):
        os.remove(output_dir+"/"+apk_name+".apk")
    shutil.move(output_dir+ "/"+apk_name+"/dist/"+apk_name+".apk", output_dir)
