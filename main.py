# -- LIBRARIES
import os
import configparser
import zipfile
import shutil
from glob import glob

import wx
import wx.adv

# --- GLOBAL VARIABLES
APP_VERSION = "0.01"

PROJECT_64_DIR = ""
TEXTUREPATH1 = "SUPER MARIO 64#6B8D43C4#0#2_all"
TEXTUREPATH2 = "SUPER MARIO 64#9FBECEF9#0#2_all"
TEXTUREPATH3 = "SUPER MARIO 64#5D6B0678#0#2_all"

# --- CONFIG
config = configparser.ConfigParser()

# save the current settings
def saveConfig():
    config.read('config.ini')

    config["CONFIG"] = {"PROJECT_64_DIR": PROJECT_64_DIR}
    config["ADV"] = {"TEXTUREPATH1": TEXTUREPATH1, "TEXTUREPATH2": TEXTUREPATH2, "TEXTUREPATH3": TEXTUREPATH3}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# load from config.ini
def loadConfig():
    global PROJECT_64_DIR, TEXTUREPATH1, TEXTUREPATH2, TEXTUREPATH3

    config.read('config.ini')

    if ("CONFIG" in config):
        configSec = config["CONFIG"]

        PROJECT_64_DIR = configSec.get("PROJECT_64_DIR")

    if ("ADV" in config):
        configSec = config["ADV"]

        paths = [TEXTUREPATH1, TEXTUREPATH2, TEXTUREPATH3]
        
        i = 0
        while i < len(paths):
            i = i + 1

            finalVal = configSec.get("TEXTUREPATH" + str(i))

            if (finalVal == ""): continue
            paths[i - 1] = finalVal

loadConfig()

# --- OTHER FUNCTIONS
def getEyes():
    list = glob("Eyes/*/")
    newlist = []
    i = 0

    while i < len(list):
        newlist.append(list[i].replace("\\", "").replace("Eyes", "", 1))
        i += 1

    return newlist

# run when user first starts the app
# detection system may need to be changed later
def FirstTimeSetup(self):
    global PROJECT_64_DIR
    dialog = wx.MessageDialog(self, "It seems this is your first time using SM64EC.\nPlease select the folder Project64 is stored in. (This can be changed later in settings)", "Welcome!", style=wx.OK | wx.ICON_INFORMATION)
    dialog.ShowModal()

    pj64 = wx.DirDialog(self, "Project 64 Path", style=wx.DD_DIR_MUST_EXIST | wx.RESIZE_BORDER)
    pj64.ShowModal()

    PROJECT_64_DIR = pj64.GetPath()

    saveConfig()

# -------------------------------- WINDOW CODE --------------------------------

# --- FRAME
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(610,520), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        self.defaultWindowStyle = self.GetWindowStyle()

        if (PROJECT_64_DIR == ""): FirstTimeSetup(self)

        # status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("v" + APP_VERSION)

        # create a panel
        self.panel = PanelOne(self)

        # menu
        self.InitMenuBar(self)

    def InitMenuBar(self, e):
        menuFile = wx.Menu()
        menuCreateEye = menuFile.Append(wx.ID_NEW,"&New","Create a new eye texture.")
        menuFile.AppendSeparator()
        menuExportEye = menuFile.Append(wx.ID_SAVE,"&Export...","Export your current textures to a .zip file for sharing.")
        menuImportEye = menuFile.Append(wx.ID_OPEN,"&Import...","Import other peoples texture files.")
        menuFile.AppendSeparator()
        menuRefresh = menuFile.Append(wx.ID_REFRESH,"&Refresh List","Refresh")
        menuFile.AppendSeparator()
        menuExit = menuFile.Append(wx.ID_EXIT,"&Exit","Exit the program.")

        menuOptions = wx.Menu()
        self.menuAlwaysTop = menuOptions.AppendCheckItem(wx.ID_TOP,"&Always On Top", "Makes the program show above all windows.")
        menuOptions.AppendSeparator()
        menuSettings = menuOptions.Append(wx.ID_PREFERENCES,"&Settings...","Configure the program to your liking.")

        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, "&About","Information about this program")

        menuBar = wx.MenuBar()
        menuBar.Append(menuFile,"&File")
        menuBar.Append(menuOptions,"&Options")
        menuBar.Append(menuHelp,"&Help")
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnNew, menuCreateEye)
        self.Bind(wx.EVT_MENU, self.OnExport, menuExportEye)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportEye)
        self.Bind(wx.EVT_MENU, self.OnRefresh, menuRefresh)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Bind(wx.EVT_MENU, self.OnOptions, menuSettings)
        self.Bind(wx.EVT_MENU, self.AlwaysOnTop, self.menuAlwaysTop)

        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)

    def OnAbout(self, e):
        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName("MyApp")
        aboutInfo.SetVersion(APP_VERSION)
        aboutInfo.SetDescription("My wxPython-based application!")
        aboutInfo.SetCopyright("(C) 1992-2012")
        aboutInfo.SetWebSite("http:#myapp.org")
        aboutInfo.AddDeveloper("My Self")

        wx.adv.AboutBox(aboutInfo)

    def OnNew(self, e):
        self.panel.createNewEye(self)

    def OnExport(self, e):
        dialog = wx.FileDialog(self, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard="SM64EC zip files (*.zip)|*.zip")
        dialog.ShowModal()

        zipTo = dialog.GetPath()
        shutil.make_archive(zipTo, "zip", "Eyes")
        self.panel.refreshList(self)

    def OnImport(self, e):
        dialog = wx.FileDialog(self, style=wx.FD_OPEN, wildcard="SM64EC zip files (*.zip)|*.zip")
        dialog.ShowModal()

        zipFrom = dialog.GetPath()
        shutil.unpack_archive(zipFrom, "Eyes", "zip") 
        self.panel.refreshList(self)

    def OnRefresh(self, e):
        self.panel.refreshList(self)

    def OnExit(self, e):
        self.Close()

    def OnOptions(self, e):
        self.dialog = Options(self)

    def AlwaysOnTop(self, e):
        val = self.menuAlwaysTop.IsChecked()
        
        if (val == True):
            windowStyle = self.GetWindowStyle()
            self.SetWindowStyle(windowStyle | wx.STAY_ON_TOP)
        else:
            windowStyle = self.defaultWindowStyle
            self.SetWindowStyle(windowStyle)

# --- MAIN PANEL
class PanelOne(wx.Panel):
    def __init__(self, parent):
        super(PanelOne, self).__init__(parent)

        self.eyes = getEyes()

        organizer = wx.StaticBox(self, label="Eye Selection", size=(230, 420), pos=(10, 5))

        self.listBox = wx.ListBox(self, style=wx.LB_SORT | wx.LB_SINGLE, size=(200, 330), pos=(25, 25), choices=self.eyes)
        self.listBox.Bind(wx.EVT_LISTBOX, self.selectEye)

        createBitmap = wx.Image("Assets/createEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        self.buttonCreate = wx.BitmapButton(self, bitmap=createBitmap, pos=(25, 365))
        self.buttonCreate.Bind(wx.EVT_BUTTON, self.createNewEye)

        deleteBitmap = wx.Image("Assets/deleteEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        self.buttonDelete = wx.BitmapButton(self, bitmap=deleteBitmap, pos=(80, 365))
        self.buttonDelete.Bind(wx.EVT_BUTTON, self.deleteEye)
        
        # unused as of now
        #editBitmap = wx.Image("Assets/editEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        #self.buttonEdit = wx.BitmapButton(self, bitmap=editBitmap, pos=(135, 365), name="Edit")
        #self.buttonEdit.Bind(wx.EVT_BUTTON, self.createNewEye)

        organizer = wx.StaticBox(self, label="Eye Preview", size=(310, 365), pos=(275, 5))

        eyePreviewBitmap = wx.Image("Assets/Unknown/1.png", type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
        self.eyePreview = wx.StaticBitmap(self, bitmap=eyePreviewBitmap, pos=(280,20))

        self.slider = wx.Slider(self, value=1, minValue=1, maxValue=3, pos=(280, 325), size=(300, 40))
        self.slider.Bind(wx.EVT_SLIDER, self.previewFrame)


        applyButton = wx.Button(self, label="APPLY", pos=(485, 385), size=(100,30))
        applyButton.Bind(wx.EVT_BUTTON, self.applyEyes)

    def selectEye(self, e):
        val = self.slider.GetValue()
        selection = self.listBox.GetSelection()
        path = "Eyes/" + self.listBox.GetString(selection) + "/" + str(val) + ".png"

        if (os.path.isfile(path) == False):
            dialog = wx.MessageDialog(self, "Could not load from the path:\n" + path, "ERROR CODE 0", style=wx.OK | wx.ICON_ERROR)
            selection = self.listBox.GetSelection()
            shutil.rmtree("Eyes/" + self.listBox.GetString(selection))

            self.refreshList(self)
            dialog.ShowModal()
        else:
            newBitmap = wx.Image(path, type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
            self.eyePreview.SetBitmap(newBitmap)
    
    def createNewEye(self, e):
        edit = False
        if (e.GetEventObject().GetName() == "Edit"): edit = True

        self.dialog = NewEyeDialog(self, edit)

    def deleteEye(self, e):
        selection = self.listBox.GetSelection()
        shutil.rmtree("Eyes/" + self.listBox.GetString(selection))

        self.refreshList(self)

    def previewFrame(self, e):
        val = self.slider.GetValue()
        selection = self.listBox.GetSelection()
        path = "Assets/Unknown/" + str(val) + ".png"
        if (selection != wx.NOT_FOUND): path = "Eyes/" + self.listBox.GetString(selection) + "/" + str(val) + ".png"

        newBitmap = wx.Image(path, type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
        self.eyePreview.SetBitmap(newBitmap)

    def applyEyes(self, e): 
        pathTo = PROJECT_64_DIR + "/Plugin/hires_texture/SUPER MARIO 64/png_all"

        if (os.path.isdir(PROJECT_64_DIR) == False):
            dialog = wx.MessageDialog(self, "Please enter a valid Project 64 path.", "ERROR CODE 1", style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        if (os.path.isdir(pathTo) == False):
            os.makedirs(pathTo)

        # replace eye textures
        if (self.listBox.GetSelection() == wx.NOT_FOUND):
            dialog = wx.MessageDialog(self, "Please select a eye texture to apply.", "ERROR CODE 2", style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        selection = self.listBox.GetSelection()
        pathFrom = "Eyes/" + self.listBox.GetString(selection)

        eyeFinalNames = [TEXTUREPATH1, TEXTUREPATH2, TEXTUREPATH3]

        i = 0
        while i < len(eyeFinalNames):
            if (os.path.isfile(pathTo + "/" + eyeFinalNames[i] + ".png")): os.remove(pathTo + "/" + eyeFinalNames[i] + ".png")
            shutil.copy(pathFrom + "/" + str(i + 1) + ".png", pathTo + "/" + eyeFinalNames[i] + ".png")
            i += 1

        dialog = wx.MessageDialog(self, "Applied the '" + self.listBox.GetString(selection) + "' eye texture.\nPlease restart the game or load a savestate.", "APPLIED", style=wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()

    def refreshList(self, e):
        self.eyes = getEyes()
        self.listBox.SetItems(self.eyes)
        
# --- NEW EYE DIALOG
class NewEyeDialog(wx.Frame):
    def __init__(self, parent, edit):
        super(NewEyeDialog, self).__init__(parent, title="Create New Eye", size=(530,340), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        
        panel = wx.Panel(self, size=(530, 300))

        finishButton = wx.Button(panel, label="Finish", pos=(430, 270))
        finishButton.Bind(wx.EVT_BUTTON, self.finish)
        cancelButton = wx.Button(panel, label="Cancel", pos=(345, 270))
        cancelButton.Bind(wx.EVT_BUTTON, self.cancel)

        noEye1Bitmap = wx.Image("Assets/Unknown/1.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()
        noEye2Bitmap = wx.Image("Assets/Unknown/2.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()
        noEye3Bitmap = wx.Image("Assets/Unknown/3.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()

        self.openLabel = wx.StaticText(panel, label="Opened", pos=(20,55))
        self.midLabel = wx.StaticText(panel, label="Middle", pos=(180,55))
        self.closedLabel = wx.StaticText(panel, label="Closed", pos=(340,55))

        self.eyeOpenPreview = wx.StaticBitmap(panel, bitmap=noEye1Bitmap, pos=(20,70))
        self.eyeMidPreview = wx.StaticBitmap(panel, bitmap=noEye2Bitmap, pos=(180,70))
        self.eyeClosedPreview = wx.StaticBitmap(panel, bitmap=noEye3Bitmap, pos=(340,70))

        self.fileOpen = wx.FilePickerCtrl(panel, pos=(20,225),style=wx.FLP_OPEN, name="Open")
        self.fileMid = wx.FilePickerCtrl(panel, pos=(180,225),style=wx.FLP_OPEN, name="Mid")
        self.fileClosed = wx.FilePickerCtrl(panel, pos=(340,225),style=wx.FLP_OPEN, name="Closed")

        self.fileOpen.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)
        self.fileMid.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)
        self.fileClosed.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)

        self.eyeNameLabel = wx.StaticText(panel, label="Name", pos=(20,10))
        self.eyeName = wx.TextCtrl(panel, pos=(60, 10), size=(100,20))

        self.Show()

    def browseEye(self, e):
        name = e.GetEventObject().GetName()
        imagePath = e.GetEventObject().GetPath()
        bitmap = wx.Image(imagePath, type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()

        #python does not have switch statements...
        if (name == "Open"): previewChange = self.eyeOpenPreview
        elif (name == "Mid"): previewChange = self.eyeMidPreview
        else: previewChange = self.eyeClosedPreview

        previewChange.SetBitmap(bitmap)

    def finish(self, e):
        if (self.eyeName.GetValue() == ""):
            dialog = wx.MessageDialog(self, "A name cannot be blank, silly. :P", "COULD NOT CREATE", style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        newpath = "Eyes/" + self.eyeName.GetValue()

        if (os.path.exists(newpath)):
            dialog = wx.MessageDialog(self, "An eye texture with this name already exists.\nPlease choose a different name.", "COULD NOT CREATE", style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        os.makedirs(newpath)
        shutil.copy(self.fileOpen.GetPath(), newpath + "/1.png")
        shutil.copy(self.fileMid.GetPath(), newpath + "/2.png")
        shutil.copy(self.fileClosed.GetPath(), newpath + "/3.png")

        self.GetParent().refreshList(self)
        self.Close()

    def cancel(self, e):
        self.Close()

# --- OPTIONS DIALOG
class Options(wx.Frame):
    def __init__(self, parent):
        super(Options, self).__init__(parent, title="Settings", size=(350,200), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        panel = wx.Panel(self)

        apply = wx.Button(panel, label="Save", pos=(250, 130), name="Save")
        apply.Bind(wx.EVT_BUTTON, self.updateConfigFunc)

        notebook = wx.Notebook(panel)


        tab1 = wx.Panel(notebook)
        notebook.AddPage(tab1, "General")

        project64Label = wx.StaticText(tab1, label="Project64 Path", pos=(10,15))
        self.project64Dir = wx.DirPickerCtrl(tab1, pos=(100, 10), style=wx.DIRP_USE_TEXTCTRL | wx.DIRP_DIR_MUST_EXIST, size=(220,30), path=PROJECT_64_DIR)
        self.project64Dir.Bind(wx.EVT_DIRPICKER_CHANGED, self.updateConfigFunc)

        tab2 = wx.Panel(notebook)
        notebook.AddPage(tab2, "Advanced")

        textureOpenLabel = wx.StaticText(tab2, label="Texture Eye Open Path", pos=(10,15))
        self.textureOpenPath = wx.TextCtrl(tab2, pos=(135, 12), size=(180,22), value=TEXTUREPATH1)

        textureMidLabel = wx.StaticText(tab2, label="Texture Eye Mid Path", pos=(10,45))
        self.textureMidPath = wx.TextCtrl(tab2, pos=(135, 42), size=(180,22), value=TEXTUREPATH2)

        textureClosedLabel = wx.StaticText(tab2, label="Texture Eye Close Path", pos=(10,75))
        self.textureClosedPath = wx.TextCtrl(tab2, pos=(135, 72), size=(180,22), value=TEXTUREPATH3)


        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Show()

    def updateConfigFunc(self, e):
        global PROJECT_64_DIR, TEXTUREPATH1, TEXTUREPATH2, TEXTUREPATH3
        PROJECT_64_DIR = self.project64Dir.GetPath()
        if (self.textureOpenPath.GetValue() != ""): TEXTUREPATH1 = self.textureOpenPath.GetValue()
        if (self.textureOpenPath.GetValue() != ""): TEXTUREPATH2 = self.textureOpenPath.GetValue()
        if (self.textureOpenPath.GetValue() != ""): TEXTUREPATH3 = self.textureOpenPath.GetValue()

        saveConfig()

        if (e.GetEventObject().GetName() == "Save"): self.Close()

# --- APP
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, "64 EYE CHANGER")
        self.frame.Show()
        self.frame.Center()

        #self.Bind(wx.EVT_IDLE, self.onIdle)

        return True

app = MyApp()
app.MainLoop()