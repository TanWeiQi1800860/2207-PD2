# 2208-PD2
A python 3 based application that uses external tools to decompile Android APK's. Extracting the JAVA source code, manifest, assets, etc.
GUI is created with wxpython, it contains 2 input text field, input and output. Input have drag and drop feature which allows you to drag a file into the text file. Output will automatically generate a output path for you when you select a file or drop a file into the input.

After downloading the zip, extract it to a location of your choice and open the folder as a project in PyCharm.
# modules
This folder contains the obfuscation techniques. Any python file put in to this folder will appear in the checkbox area.
# resources
This folder contains any resources required for the project
 - obf_key.jks - store pass: 123456
 - Hello-world.apk - For testing obfuscate technique
 - app-debug.apk - A more complicated app. A 2048 game, from PD1
# tools
This folder contains external tools required for the project

  Tools:
- apktool v2.3.4
- dex2jar v2.1-20190905-lanchon
- jd-cli 0.9.1.Final
- jadx-gui-1.2.0-no-jre-win
- jarsigner.exe jdk-15.0.2
