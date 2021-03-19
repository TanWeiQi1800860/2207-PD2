import threading
import wx
import glob, sys, os
import ctypes

from pathlib import Path

try:
    from apk_decompiler import *
except:
    print("apk_decompiler.py cannot be found")
try:
    from modules import Constant_String_Encryption
except:
    print("Constant_String_Encryption.py cannot be found")
try:
    from modules import Arithmetic_Branch
except:
    print("Arithmetic_Branch.py cannot be found")

sys.path.insert(0, '/modules')
ICON_PATH = os.getcwd() + "/resources/team22.ico"
my_app_id = r'team22'
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
except:
    True


class DragandDrop(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.SetInsertionPointEnd()
        for filepath in filenames:
            self.window.updateText(filepath)
        return True


class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='APK Obuscator', style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX
                                                                   ^ wx.RESIZE_BORDER, size=(900, 600))
        self.main_panel = wx.Panel(self, size=(800, 100))

        ver_Sizer = wx.BoxSizer(wx.VERTICAL)
        hor_Sizer = wx.BoxSizer(wx.HORIZONTAL)
        file_drop_target = DragandDrop(self)

        lbl_fileinput = wx.StaticText(self.main_panel, 1, size=(121, 25))
        lbl_fileinput.SetLabel("Input file:")
        font = wx.Font(15, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        lbl_fileinput.SetFont(font)
        hor_Sizer.Add(lbl_fileinput, 2, wx.ALL | wx.LEFT, 10)

        self.txt_fileinput = wx.TextCtrl(self.main_panel, size=(600, -1))
        self.txt_fileinput.SetDropTarget(file_drop_target)
        hor_Sizer.Add(self.txt_fileinput, 3, wx.ALL | wx.EXPAND, 10)

        self.btn_findfile = wx.Button(self.main_panel, 4, label='Find')
        hor_Sizer.Add(self.btn_findfile, 101, wx.ALL | wx.RIGHT, 5)
        self.btn_findfile.Bind(wx.EVT_BUTTON, self.on_btn_find_click)

        ver_Sizer.Add(hor_Sizer)

        hor_Sizer_02 = wx.BoxSizer(wx.HORIZONTAL)
        lbl_fileoutput = wx.StaticText(self.main_panel, 5, size=(121, 25))
        lbl_fileoutput.SetLabel("Output folder:")
        font = wx.Font(15, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        lbl_fileoutput.SetFont(font)
        hor_Sizer_02.Add(lbl_fileoutput, 6, wx.ALL | wx.LEFT, 10)

        self.txt_fileoutput = wx.TextCtrl(self.main_panel, size=(600, -1))
        hor_Sizer_02.Add(self.txt_fileoutput, 7, wx.ALL | wx.EXPAND, 10)

        self.btn_finddir = wx.Button(self.main_panel, 8, label='Find')
        hor_Sizer_02.Add(self.btn_finddir, 102, wx.ALL | wx.RIGHT, 5)
        self.btn_finddir.Bind(wx.EVT_BUTTON, self.on_btn_find_out_click)

        ver_Sizer.Add(hor_Sizer_02)

        hor_Sizer_03 = wx.BoxSizer(wx.HORIZONTAL)
        self.list = wx.CheckListBox(self.main_panel, size=(500, 400))
        hor_Sizer_03.Add(self.list, 102, wx.ALL | wx.RIGHT, 5)
        font2 = wx.Font(16, wx.SWISS, wx.FONTSTYLE_NORMAL, wx.NORMAL)
        self.list.SetFont(font2)
        ob_py_modules = self.get_ob_py_module()
        try:
            ob_py_modules.remove("__ init __.py")
        except:
            True
        for i in ob_py_modules:
            str_name = i.replace('_', ' ').replace('.py', '')
            self.list.Insert(str_name, ob_py_modules.index(i))
            self.list.Check(ob_py_modules.index(i))

        ver_Sizer.Add(hor_Sizer_03)

        hor_Sizer_04 = wx.BoxSizer(wx.HORIZONTAL)
        self.btn_obfuscate = wx.Button(self.main_panel, 9, label='Obfuscate')
        hor_Sizer_04.Add(self.btn_obfuscate, 101, wx.ALL | wx.RIGHT, 5)
        self.btn_obfuscate.Bind(wx.EVT_BUTTON, self.on_btn_obfuscate_click)
        self.gauge = wx.Gauge(self.main_panel, range=4, size=(400, 25), style=wx.GA_HORIZONTAL)
        hor_Sizer_04.Add(self.gauge, proportion=1, border=10)
        self.progressValue = 0

        ver_Sizer.Add(hor_Sizer_04)

        self.main_panel.SetSizer(ver_Sizer)
        self.Show()

    def on_btn_find_click(self, e):
        title = "Choose a directory:"
        fileinput = self.txt_fileinput.GetValue()
        temp = fileinput.split('\\')
        temp.pop()
        file_dir = '\\'.join(temp)
        path = Path(file_dir)
        raw_string = r"{}".format(path)
        dlg = wx.FileDialog(self, title, raw_string, "", "APK files (*.apk)|*.apk|All Files (*.*)|*.*",
                            style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.txt_fileinput.Clear()
            self.txt_fileinput.write(dlg.GetPath())
            self.txt_fileoutput.Clear()
            self.txt_fileoutput.write(self.get_parent_folder(dlg.GetPath()) + "\\Obfuscate")
        dlg.Destroy()

    def on_btn_find_out_click(self, e):
        title = "Choose a directory:"
        fileoutput = self.txt_fileoutput.GetValue()
        path = Path(fileoutput)
        raw_string = r"{}".format(path)
        dlg = wx.DirDialog(self, title, raw_string, style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.txt_fileoutput.Clear()
            self.txt_fileoutput.write(dlg.GetPath())
        dlg.Destroy()

    def SetInsertionPointEnd(self):
        self.txt_fileinput.SetInsertionPointEnd()

    def updateText(self, text):
        self.txt_fileinput.Clear()
        self.txt_fileinput.WriteText(text)
        self.txt_fileoutput.Clear()
        self.txt_fileoutput.write(self.get_parent_folder(text) + "\\Obfuscate\\")

    def get_parent_folder(self, path):
        temp = path.split('\\')
        temp.pop()
        return '\\'.join(temp)

    def get_ob_py_module(self):
        module_path = "modules"
        if not os.path.exists(module_path):
            print("[-] Error: 'module' folder is missing")
            return False
        temp_list = []
        os.chdir(module_path)
        for file in glob.glob("*.py"):
            temp_list.append(file)
        os.chdir("..")
        return temp_list

    def updatebar(self):
        self.progressValue = self.progressValue + 1
        self.gauge.SetValue(self.progressValue)
        if self.progressValue >= 20:
            return

    def on_btn_obfuscate_click(self, e):
        self.gauge.SetValue(0)
        progress_max = 3 + len(self.list.CheckedStrings)
        self.gauge.SetRange(progress_max)
        self.progressValue = 0
        if verify_tools():
            if not os.path.exists(self.txt_fileoutput.GetValue()):
                try:
                    os.mkdir(self.txt_fileoutput.GetValue())
                    print("Directory ", self.txt_fileoutput.GetValue(), " Created ")
                except:
                    print("Output folder not found/valid")
                    return
            else:
                print("Directory ", self.txt_fileoutput.GetValue(), " already exists")
            if os.path.exists(self.txt_fileinput.GetValue()):
                apk_name = \
                    self.txt_fileinput.GetValue().split('\\')[len(self.txt_fileinput.GetValue().split('\\')) - 1].split(
                        '.')[0]
                try:
                    decompile_apk(self.txt_fileinput.GetValue(), self.txt_fileoutput.GetValue(), self, True)
                except Exception as e:
                    print(e)
                AB = 'Arithmetic Branch' in self.list.CheckedStrings
                NoC = 'Nop Code' in self.list.CheckedStrings
                CSE = 'Constant String Encryption' in self.list.CheckedStrings
                if AB or NoC:
                    if AB:
                        print("[+] Running Arithmetic Branch")
                    Arithmetic_Branch.Find_method(self.txt_fileoutput.GetValue() + "\\" + apk_name, AB, NoC)
                    self.updatebar()
                if CSE:
                    print("[+] Constant String Encryption")
                    AES_C = Constant_String_Encryption.AESCipher(b"Thereisnospoon68")
                    try:
                        Constant_String_Encryption.AESCipher.find_string(AES_C, self.txt_fileoutput.GetValue() +
                                                                         apk_name + "\\smali", True)
                        self.updatebar()
                    except Exception as e:
                        print(e)
                compile_apk(self.txt_fileoutput.GetValue(), self.txt_fileinput.GetValue())
            else:
                print("Input file not found")


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.SetTopWindow(frame)
    icon = wx.Icon()
    icon.CopyFromBitmap(wx.Bitmap(ICON_PATH, wx.BITMAP_TYPE_ANY))
    MainFrame.SetIcon(frame, icon)
    app.MainLoop()
