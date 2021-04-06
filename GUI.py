import threading
import wx
import glob, sys, os
import ctypes
import json

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
try:
    from modules import Debug_Removal
except:
    print("Debug_Removal.py cannot be found")
try:
    from modules import Renaming
except:
    print("Renaming.py cannot be found")

sys.path.insert(0, '/modules')
ICON_PATH = os.getcwd() + "/resources/team22.ico"
my_app_id = r'team22'
ob_options = {}
default_unchecked = ["Renaming"]
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
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.doubleclick, self.list)
        self.Bind(wx.EVT_CHECKLISTBOX, self.OnTicked, self.list)

        ob_py_modules = self.get_ob_py_module()
        try:
            ob_py_modules.remove("__ init __.py")
        except:
            True
        for i in ob_py_modules:
            str_name = i.replace('_', ' ').replace('.py', '')
            self.list.Insert(str_name, ob_py_modules.index(i))
            if str_name not in default_unchecked:
                self.list.Check(ob_py_modules.index(i))
        self.update_options()

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

    def doubleclick(self, event):
        try:
            clb_selection = self.list.GetItems()[event.GetSelection()]
            win = OptionsPop(self.GetTopLevelParent(), wx.SIMPLE_BORDER, clb_selection)
            win.Center()
            win.Show(True)
        except Exception as e:
            print(e)

    def on_btn_obfuscate_click(self, e):
        self.gauge.SetValue(0)
        progress_max = len(self.list.CheckedStrings)
        self.gauge.SetRange(progress_max)
        self.progressValue = 0
        apk_only = True
        if verify_tools():
            if not os.path.exists(self.txt_fileoutput.GetValue()):
                try:
                    os.mkdir(self.txt_fileoutput.GetValue())
                    print("Directory ", self.txt_fileoutput.GetValue(), " Created ")
                except:
                    md = wx.MessageDialog(self, "Output folder not found/valid",
                                          "Error", wx.OK | wx.STAY_ON_TOP | wx.CENTRE)
                    md.ShowModal()
                    print("Output folder not found/valid")
                    return
            else:
                print("Directory ", self.txt_fileoutput.GetValue(), " already exists")
            inputdir = self.txt_fileinput.GetValue()
            if os.path.exists(inputdir):
                filename = os.path.basename(inputdir)
                apk_name = \
                    inputdir.split('\\')[len(inputdir.split('\\')) - 1].split(
                        '.')[0]
                if filename.endswith(".apk"):
                    if all(item in self.list.CheckedStrings for item in default_unchecked) and apk_only:
                        md = wx.MessageDialog(self, "Technique chosen is for folder containing source code",
                                              "Invalid Input", wx.OK | wx.STAY_ON_TOP | wx.CENTRE)
                        md.ShowModal()
                        print("Technique chosen is for folder containing source code")
                        return
                    try:
                        decompile_apk(inputdir, self.txt_fileoutput.GetValue(), self, True)
                    except Exception as e:
                        print(e)
                else:
                    apk_only = False
                if not all(item in self.list.CheckedStrings for item in default_unchecked) and not apk_only:
                    md = wx.MessageDialog(self, "APK file not detected",
                                          "Invalid Input", wx.OK | wx.STAY_ON_TOP | wx.CENTRE)
                    md.ShowModal()
                    print("APK file not detected")
                    return
                AB = 'Arithmetic Branch' in self.list.CheckedStrings
                NoC = 'Nop Code' in self.list.CheckedStrings
                CSE = 'Constant String Encryption' in self.list.CheckedStrings
                DeRe = 'Debug Removal' in self.list.CheckedStrings
                Ren = 'Renaming' in self.list.CheckedStrings
                output_dir = self.txt_fileoutput.GetValue() + apk_name
                if AB or NoC:
                    if AB:
                        print("[+] Running Arithmetic Branch")
                    Arithmetic_Branch.Find_method(output_dir, AB, NoC,
                                                  ob_options.get("Arithmetic Branch")['ignore_file'])
                    self.updatebar()
                if CSE:
                    print("[+] Constant String Encryption")
                    AES_C = Constant_String_Encryption.AESCipher(b"Thereisnospoon68")
                    try:
                        Constant_String_Encryption.AESCipher.find_string(AES_C, output_dir + "\\smali", True,
                                                                         ob_options.get("Constant String Encryption")
                                                                         ['ignore_file'])
                        self.updatebar()
                    except Exception as e:
                        print(e)
                if DeRe:
                    print("[+] Removing Debug information")
                    Debug_Removal.Find_method_debug(output_dir, ob_options.get("Debug Removal")['ignore_file'])
                if Ren:
                    print("[+] Renaming Variable and functions")
                    if os.path.exists(output_dir):
                        try:
                            shutil.rmtree(output_dir, ignore_errors=False, onerror=self.handleRemoveReadonly)
                        except Exception as e:
                            print(e)
                            return
                    shutil.copytree(inputdir, output_dir)
                    full_FilePath_list = Renaming.identify_files(output_dir, ob_options.get("Renaming")['ignore_file'])
                    Renaming.get_VarNames(full_FilePath_list)
                if not all(item in self.list.CheckedStrings for item in default_unchecked):
                    compile_apk(self.txt_fileoutput.GetValue(), self.txt_fileinput.GetValue())
            else:
                print("Input file not found")

    def update_options(self):
        try:
            with open("options.json") as file:
                data = file.read()
                temp_options = json.loads(data)
                ob_options.update(temp_options)
        except IOError:
            f = open("options.json", "a")
            size = len(self.list.GetStrings())
            count = 1
            f.write("{\n")
            for item in self.list.GetStrings():
                if item == "Constant String Encryption":
                    if count < size:
                        f.writelines(
                            "\t\"" + item + "\": {\n\t\t\"ignore_file\":[\"DecryptString.smali\","
                                            "\"BuildConfig.smali\"]\n\t},\n")
                    elif count == size:
                        f.writelines(
                            "\t\"" + item + "\": {\n\t\t\"ignore_file\":[\"DecryptString.smali\","
                                            "\"BuildConfig.smali\"]\n\t}\n")
                elif item == "Arithmetic Branch":
                    if count < size:
                        f.writelines(
                            "\t\"" + item + "\": {\n\t\t\"ignore_file\":[\"DecryptString.smali\",\"BuildConfig.smali\","
                                            "\"Grid$GridIterator.smali\"]\n\t},\n")
                    elif count == size:
                        f.writelines(
                            "\t\"" + item + "\": {\n\t\t\"ignore_file\":[\"DecryptString.smali\",\"BuildConfig.smali\","
                                            "\"Grid$GridIterator.smali\"]\n\t}\n")
                else:
                    if count < size:
                        f.writelines("\t\"" + item + "\": {\n\t\t\"ignore_file\":[]\n\t},\n")
                    elif count == size:
                        f.writelines("\t\"" + item + "\": {\n\t\t\"ignore_file\":[]\n\t}\n")
                count = count + 1
            f.write("\n}")
            f.close()

    def save_options(self):
        try:
            with open('options.json', 'w') as file:
                json.dump(ob_options, file)
        except Exception as e:
            print(e)
            print("Error Saving file")

    def OnTicked(self, event):
        if self.list.GetItems()[event.GetSelection()] in default_unchecked:
            for items in self.list.CheckedItems:
                if self.list.GetItems()[items] not in default_unchecked:
                    self.list.Check(items, False)
        if self.list.GetItems()[event.GetSelection()] not in default_unchecked:
            for items in self.list.CheckedItems:
                if self.list.GetItems()[items] in default_unchecked:
                    self.list.Check(items, False)

    def handleRemoveReadonly(self, func, path, exc):
        import errno, os, stat, shutil
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        func(path)


class OptionsPop(wx.PopupWindow):
    def __init__(self, parent, style, title):
        wx.PopupWindow.__init__(self, parent, style)

        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        optionless = ["Nop Code"]

        self.listbox = wx.ListCtrl(panel, style=wx.LC_REPORT)
        if title not in optionless:
            self.listbox.InsertColumn(0, 'Files to ignore', width=345)
        else:
            self.listbox.Disable()
        for file in ob_options.get(title)['ignore_file']:
            self.listbox.InsertItem(0, file)
        hbox.Add(self.listbox, wx.ID_ANY, wx.EXPAND | wx.ALL, 20)

        btnPanel = wx.Panel(panel)
        vbox = wx.BoxSizer(wx.VERTICAL)
        newBtn = wx.Button(btnPanel, wx.ID_ANY, 'New', size=(90, 30))
        renBtn = wx.Button(btnPanel, wx.ID_ANY, 'Rename', size=(90, 30))
        delBtn = wx.Button(btnPanel, wx.ID_ANY, 'Delete', size=(90, 30))
        clrBtn = wx.Button(btnPanel, wx.ID_ANY, 'Clear', size=(90, 30))
        savBtn = wx.Button(btnPanel, wx.ID_ANY, 'Save', size=(90, 30))
        cloBtn = wx.Button(btnPanel, wx.ID_ANY, 'Close', size=(90, 30))
        if (title in optionless):
            newBtn.Disable()
            renBtn.Disable()
            delBtn.Disable()
            clrBtn.Disable()
            savBtn.Disable()
        self.Bind(wx.EVT_BUTTON, self.NewItem, id=newBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnRename, id=renBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnDelete, id=delBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.OnClear, id=clrBtn.GetId())
        self.Bind(wx.EVT_BUTTON, self.onClose, id=cloBtn.GetId())
        self.Bind(wx.EVT_BUTTON, lambda event: self.onSave(event, title), id=savBtn.GetId())
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnRename)

        vbox.Add((-1, 20))
        vbox.Add(newBtn)
        vbox.Add(renBtn, 0, wx.TOP, 5)
        vbox.Add(delBtn, 0, wx.TOP, 5)
        vbox.Add(clrBtn, 0, wx.TOP, 5)
        vbox.Add(savBtn, 0, wx.TOP, 5)
        vbox.Add(cloBtn, 0, wx.TOP, 5)

        btnPanel.SetSizer(vbox)
        hbox.Add(btnPanel, 0.6, wx.EXPAND | wx.RIGHT, 20)
        panel.SetSizer(hbox)

        self.Centre()

        panel.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        panel.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        panel.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        panel.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)

        self.SetSize((500, 500))
        panel.SetSize((500, 500))
        wx.CallAfter(self.Refresh)

    def OnMouseLeftDown(self, evt):
        try:
            self.Refresh()
            self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            self.wPos = self.ClientToScreen((0, 0))
            self.panel.CaptureMouse()
        except:
            True

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            try:
                dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
                nPos = (self.wPos.x + (dPos.x - self.ldPos.x),
                        self.wPos.y + (dPos.y - self.ldPos.y))
                self.Move(nPos)
            except:
                True

    def OnMouseLeftUp(self, evt):
        try:
            if self.panel.HasCapture():
                self.panel.ReleaseMouse()
        except:
            True

    def onClose(self, event):
        self.Show(False)

    def OnRightUp(self, evt):
        self.Show(False)
        self.Destroy()

    def NewItem(self, event):
        text = wx.GetTextFromUser('Enter a new item', 'Insert dialog')
        if text != '':
            self.listbox.InsertItem(0, text)

    def OnRename(self, event):
        sel = self.listbox.GetFirstSelected()
        if sel >= 0:
            text = self.listbox.GetItemText(sel, 0)
            renamed = wx.GetTextFromUser('Rename item', 'Rename dialog', text, self)

            if renamed != '':
                self.listbox.DeleteItem(sel)
                item_id = self.listbox.InsertItem(0, renamed)
                self.listbox.Select(item_id)
    
    def OnDelete(self, event):
        sel = self.listbox.GetFirstSelected()
        if sel != -1:
            self.listbox.DeleteItem(sel)

    def OnClear(self, event):
        self.listbox.DeleteAllItems()

    def onSave(self, event, title):
        del ob_options.get(title)['ignore_file']
        temp_list = []
        for x in range(self.listbox.GetItemCount()):
            temp_list.append(self.listbox.GetItemText(x))
        ob_options.get(title)['ignore_file'] = temp_list
        MainFrame.save_options(self)
        self.Show(False)


if __name__ == '__main__':
    app = wx.App()
    frame = MainFrame()
    app.SetTopWindow(frame)
    icon = wx.Icon()
    icon.CopyFromBitmap(wx.Bitmap(ICON_PATH, wx.BITMAP_TYPE_ANY))
    MainFrame.SetIcon(frame, icon)
    app.MainLoop()
