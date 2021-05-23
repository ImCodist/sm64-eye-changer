# -- LIBRARIES
import os
import configparser
import zipfile
import shutil
from glob import glob

import wx
import wx.adv

# -- LANGUAGES
import lang.eng

lang = lang.eng.LANG()

# --- GLOBAL VARIABLES
APP_VERSION = "1.0.0"

class optionVars():
    PROJECT_64_DIR = ""
    TEXTUREPATH1 = "SUPER MARIO 64#6B8D43C4#0#2_all"
    TEXTUREPATH2 = "SUPER MARIO 64#9FBECEF9#0#2_all"
    TEXTUREPATH3 = "SUPER MARIO 64#5D6B0678#0#2_all"

option = optionVars()

# --- CONFIG
config = configparser.ConfigParser()

# save the current settings
def saveConfig():
    config.read('config.ini')

    config["CONFIG"] = {"PROJECT_64_DIR": option.PROJECT_64_DIR}
    config["ADV"] = {"TEXTUREPATH1": option.TEXTUREPATH1, "TEXTUREPATH2": option.TEXTUREPATH2, "TEXTUREPATH3": option.TEXTUREPATH3}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# load from config.ini
def loadConfig():
    config.read('config.ini')

    if ("CONFIG" in config):
        configSec = config["CONFIG"]

        option.PROJECT_64_DIR = configSec.get("PROJECT_64_DIR")

    if ("ADV" in config):
        configSec = config["ADV"]

        paths = [option.TEXTUREPATH1, option.TEXTUREPATH2, option.TEXTUREPATH3]
        
        i = 0
        while i < len(paths):
            i = i + 1

            finalVal = configSec.get("TEXTUREPATH" + str(i))

            if (finalVal == ""):
                continue
            paths[i - 1] = finalVal

loadConfig()

# --- OTHER FUNCTIONS
def getEyes():
    dirlist = glob("Eyes/*/")
    newlist = []
    i = 0

    while i < len(dirlist):
        newlist.append(dirlist[i].replace("\\", "").replace("Eyes", "", 1))
        i += 1

    return newlist

# run when user first starts the app
# detection system may need to be changed later
def FirstTimeSetup(self):
    firstDialog = wx.MessageDialog(self, lang.FIRST_TIME_WARNING, lang.FIRST_TIME_WELCOME, style=wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
    result = firstDialog.ShowModal()

    if (result == wx.ID_OK):
        pj64 = wx.DirDialog(self, lang.FIRST_TIME_PJ64DIR, style=wx.DD_DIR_MUST_EXIST | wx.RESIZE_BORDER)
        result = pj64.ShowModal()

        if (result == wx.ID_OK):
            option.PROJECT_64_DIR = pj64.GetPath()

            saveConfig()
        else:
            self.Close()

    else:
        self.Close()

# -------------------------------- WINDOW CODE --------------------------------

# --- FRAME
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(610,520), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        icon = wx.Icon("Assets/icon.ico")
        self.SetIcon(icon)
        
        self.defaultWindowStyle = self.GetWindowStyle()

        if (option.PROJECT_64_DIR == ""):
            FirstTimeSetup(self)

        # status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText("v" + APP_VERSION)

        # create a panel
        self.panel = PanelOne(self)

        # menu
        self.InitMenuBar(self)

    def InitMenuBar(self, e):
        menuFile = wx.Menu()
        menuCreateEye = menuFile.Append(wx.ID_NEW,lang.MENU_NEW, lang.MENU_NEW_TIP)
        menuFile.AppendSeparator()
        menuExportEye = menuFile.Append(wx.ID_SAVE,lang.MENU_EXPORT, lang.MENU_EXPORT_TIP)
        menuImportEye = menuFile.Append(wx.ID_OPEN,lang.MENU_IMPORT, lang.MENU_IMPORT_TIP)
        menuFile.AppendSeparator()
        menuRefresh = menuFile.Append(wx.ID_REFRESH,lang.MENU_REFRESH, lang.MENU_REFRESH_TIP)
        menuFile.AppendSeparator()
        menuExit = menuFile.Append(wx.ID_EXIT,lang.MENU_EXIT, lang.MENU_EXIT_TIP)

        menuOptions = wx.Menu()
        self.menuAlwaysTop = menuOptions.AppendCheckItem(wx.ID_TOP,lang.MENU_ALWAYS_ON_TOP, lang.MENU_ALWAYS_ON_TOP_TIP)
        menuOptions.AppendSeparator()
        menuSettings = menuOptions.Append(wx.ID_PREFERENCES,lang.MENU_SETTINGS, lang.MENU_SETTINGS_TIP)

        menuHelp = wx.Menu()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, lang.MENU_ABOUT, lang.MENU_ABOUT_TIP)

        menuBar = wx.MenuBar()
        menuBar.Append(menuFile,lang.MENU_BAR_FILE)
        menuBar.Append(menuOptions,lang.MENU_BAR_OPTIONS)
        menuBar.Append(menuHelp,lang.MENU_BAR_HELP)
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
        aboutInfo.SetName(lang.ABOUT_TITLE)
        aboutInfo.SetVersion(APP_VERSION)
        aboutInfo.SetDescription(lang.ABOUT_DESC)
        aboutInfo.SetWebSite("https://github.com/ImCodist/sm64-eye-changer")
        aboutInfo.AddDeveloper("@ImCodist / codist")
        aboutInfo.AddArtist("@GlitchyPSIX / GlitchyPSI (Default Eye Textures)")
        aboutInfo.SetLicence(lang.ABOUT_LICENCE + "\nGNU General Public License v3.0")

        wx.adv.AboutBox(aboutInfo)

    def OnNew(self, e):
        self.panel.createNewEye(self)

    def OnExport(self, e):
        dialog = wx.FileDialog(self, style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, wildcard="SM64EC zip files (*.sm64ec)|*.sm64ec")
        dialog.ShowModal()

        zipTo = dialog.GetPath()

        def zipdir(path, ziph):
            for root, dirs, files in os.walk(path):
                for file in files:
                    ziph.write(os.path.join(root, file), 
                            os.path.relpath(os.path.join(root, file), 
                                            os.path.join(path, '..')))
                
        zipf = zipfile.ZipFile(zipTo, 'w', zipfile.ZIP_DEFLATED)
        zipdir('Eyes/', zipf)
        zipf.close()
        
        self.panel.refreshList(self)

    def OnImport(self, e):
        dialog = wx.FileDialog(self, style=wx.FD_OPEN, wildcard="SM64EC zip files (*.sm64ec)|*.sm64ec")
        dialog.ShowModal()

        zipFrom = dialog.GetPath()
        
        with zipfile.ZipFile(zipFrom, 'r') as zip_ref:
            zip_ref.extractall("")

        self.panel.refreshList(self)

    def OnRefresh(self, e):
        self.panel.refreshList(self)

    def OnExit(self, e):
        self.Close()

    def OnOptions(self, e):
        self.dialog = Options(self)

    def AlwaysOnTop(self, e):
        val = self.menuAlwaysTop.IsChecked()
        
        if (val is True):
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

        organizer = wx.StaticBox(self, label=lang.EYE_SELECTION, size=(230, 420), pos=(10, 5))

        self.listBox = wx.ListBox(self, style=wx.LB_SORT | wx.LB_SINGLE, size=(200, 330), pos=(25, 25), choices=self.eyes)
        self.listBox.Bind(wx.EVT_LISTBOX, self.selectEye)

        createBitmap = wx.Image("Assets/createEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        self.buttonCreate = wx.BitmapButton(self, bitmap=createBitmap, pos=(25, 365))
        self.buttonCreate.SetToolTip(lang.TOOLTIP_CREATE)
        self.buttonCreate.Bind(wx.EVT_BUTTON, self.createNewEye)

        deleteBitmap = wx.Image("Assets/deleteEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        self.buttonDelete = wx.BitmapButton(self, bitmap=deleteBitmap, pos=(80, 365))
        self.buttonDelete.SetToolTip(lang.TOOLTIP_DELETE)
        self.buttonDelete.Bind(wx.EVT_BUTTON, self.deleteEye)
        
        # unused as of now
        #editBitmap = wx.Image("Assets/editEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        #self.buttonEdit = wx.BitmapButton(self, bitmap=editBitmap, pos=(135, 365), name="Edit")
        #self.buttonEdit.Bind(wx.EVT_BUTTON, self.createNewEye)

        organizer = wx.StaticBox(self, label=lang.EYE_PREVIEW, size=(310, 365), pos=(275, 5))

        eyePreviewBitmap = wx.Image("Assets/Unknown/1.png", type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
        self.eyePreview = wx.StaticBitmap(self, bitmap=eyePreviewBitmap, pos=(280,20))

        self.slider = wx.Slider(self, value=1, minValue=1, maxValue=3, pos=(280, 325), size=(300, 40))
        self.slider.Bind(wx.EVT_SLIDER, self.previewFrame)


        self.freezeFrame = wx.CheckBox(self, label=lang.FREEZE_FRAME, pos=(380, 390))

        applyButton = wx.Button(self, label=lang.APPLY, pos=(485, 385), size=(100,30))
        applyButton.Bind(wx.EVT_BUTTON, self.applyEyes)
        self.buttonDelete.SetToolTip(lang.TOOLTIP_APPLY)


    def selectEye(self, e):
        val = self.slider.GetValue()
        selection = self.listBox.GetSelection()
        path = "Eyes/" + self.listBox.GetString(selection) + "/" + str(val) + ".png"

        if (os.path.isfile(path) is False):
            dialog = wx.MessageDialog(self, lang.ERROR_O + "\n" + path, "ERROR CODE 0", style=wx.OK | wx.ICON_ERROR)
            selection = self.listBox.GetSelection()
            shutil.rmtree("Eyes/" + self.listBox.GetString(selection))

            self.refreshList(self)
            dialog.ShowModal()
        else:
            newBitmap = wx.Image(path, type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
            self.eyePreview.SetBitmap(newBitmap)
    
    def createNewEye(self, e):
        edit = False
        if (e.GetEventObject().GetName() == "Edit"):
            edit = True

        self.dialog = NewEyeDialog(self, edit)

    def deleteEye(self, e):
        selection = self.listBox.GetSelection()
        shutil.rmtree("Eyes/" + self.listBox.GetString(selection))

        self.refreshList(self)

    def previewFrame(self, e):
        val = self.slider.GetValue()
        selection = self.listBox.GetSelection()
        path = "Assets/Unknown/" + str(val) + ".png"
        if (selection != wx.NOT_FOUND):
            path = "Eyes/" + self.listBox.GetString(selection) + "/" + str(val) + ".png"

        newBitmap = wx.Image(path, type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
        self.eyePreview.SetBitmap(newBitmap)

    def applyEyes(self, e): 
        pathTo = option.PROJECT_64_DIR + "/Plugin/hires_texture/SUPER MARIO 64/png_all"

        if (os.path.isdir(option.PROJECT_64_DIR) is False):
            dialog = wx.MessageDialog(self, lang.ERROR_1, "ERROR CODE 1", style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        if (os.path.isdir(pathTo) is False):
            os.makedirs(pathTo)

        # replace eye textures
        if (self.listBox.GetSelection() == wx.NOT_FOUND):
            dialog = wx.MessageDialog(self, lang.ERROR_2, "ERROR CODE 2", style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        selection = self.listBox.GetSelection()
        pathFrom = "Eyes/" + self.listBox.GetString(selection)

        eyeFinalNames = [option.TEXTUREPATH1, option.TEXTUREPATH2, option.TEXTUREPATH3]

        i = 0
        while i < len(eyeFinalNames):
            frameToUse = i + 1

            if (self.freezeFrame.GetValue() is True):
                frameToUse = self.slider.GetValue()

            if (os.path.isfile(pathTo + "/" + eyeFinalNames[i] + ".png")):
                os.remove(pathTo + "/" + eyeFinalNames[i] + ".png")
            shutil.copy(pathFrom + "/" + str(frameToUse) + ".png", pathTo + "/" + eyeFinalNames[i] + ".png")
            i += 1

        dialog = wx.MessageDialog(self, lang.APPLY_SUCCESS1  + " '" + self.listBox.GetString(selection) + "' " + lang.APPLY_SUCCESS2, lang.APPLIED, style=wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()

    def refreshList(self, e):
        self.eyes = getEyes()
        self.listBox.SetItems(self.eyes)
        
# --- NEW EYE DIALOG
class NewEyeDialog(wx.Frame):
    def __init__(self, parent, edit):
        super(NewEyeDialog, self).__init__(parent, title=lang.CREATE_NEW_EYE, size=(530,340), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        
        panel = wx.Panel(self, size=(530, 300))

        finishButton = wx.Button(panel, label=lang.CREATE_FINISH, pos=(430, 270))
        finishButton.Bind(wx.EVT_BUTTON, self.finish)
        cancelButton = wx.Button(panel, label=lang.CREATE_CANCEL, pos=(345, 270))
        cancelButton.Bind(wx.EVT_BUTTON, self.cancel)

        noEye1Bitmap = wx.Image("Assets/Unknown/1.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()
        noEye2Bitmap = wx.Image("Assets/Unknown/2.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()
        noEye3Bitmap = wx.Image("Assets/Unknown/3.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()

        self.openLabel = wx.StaticText(panel, label=lang.CREATE_OPENED_LABEL, pos=(20,55))
        self.midLabel = wx.StaticText(panel, label=lang.CREATE_SEMI_LABEL, pos=(180,55))
        self.closedLabel = wx.StaticText(panel, label=lang.CREATE_CLOSED_LABEL, pos=(340,55))

        self.eyeOpenPreview = wx.StaticBitmap(panel, bitmap=noEye1Bitmap, pos=(20,70))
        self.eyeMidPreview = wx.StaticBitmap(panel, bitmap=noEye2Bitmap, pos=(180,70))
        self.eyeClosedPreview = wx.StaticBitmap(panel, bitmap=noEye3Bitmap, pos=(340,70))

        self.fileOpen = wx.FilePickerCtrl(panel, pos=(20,225),style=wx.FLP_OPEN, name="Open")
        self.fileMid = wx.FilePickerCtrl(panel, pos=(180,225),style=wx.FLP_OPEN, name="Mid")
        self.fileClosed = wx.FilePickerCtrl(panel, pos=(340,225),style=wx.FLP_OPEN, name="Closed")

        self.fileOpen.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)
        self.fileMid.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)
        self.fileClosed.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)

        self.eyeNameLabel = wx.StaticText(panel, label=lang.CREATE_NAME_LABEL, pos=(20,10))
        self.eyeName = wx.TextCtrl(panel, pos=(60, 10), size=(100,20))

        self.Show()

    def browseEye(self, e):
        name = e.GetEventObject().GetName()
        imagePath = e.GetEventObject().GetPath()
        bitmap = wx.Image(imagePath, type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()

        #python does not have switch statements...
        if (name == "Open"): 
            previewChange = self.eyeOpenPreview
        elif (name == "Mid"): 
            previewChange = self.eyeMidPreview
        else: 
            previewChange = self.eyeClosedPreview

        previewChange.SetBitmap(bitmap)

    def finish(self, e):
        if (self.eyeName.GetValue() == ""):
            dialog = wx.MessageDialog(self, lang.COULD_NOT_CREATE_1, lang.COULD_NOT_CREATE, style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        newpath = "Eyes/" + self.eyeName.GetValue()

        if (os.path.exists(newpath)):
            dialog = wx.MessageDialog(self, lang.COULD_NOT_CREATE_2, lang.COULD_NOT_CREATE, style=wx.OK | wx.ICON_ERROR)
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
        super(Options, self).__init__(parent, title=lang.SETTINGS, size=(350,230), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        panel = wx.Panel(self)

        apply = wx.Button(panel, label=lang.SETTINGS_SAVE, pos=(250, 160), name="Save")
        apply.Bind(wx.EVT_BUTTON, self.updateConfigFunc)

        notebook = wx.Notebook(panel)


        tab1 = wx.Panel(notebook)
        notebook.AddPage(tab1, lang.SETTINGS_GENERAL)

        project64Label = wx.StaticText(tab1, label=lang.SETTINGS_LABEL_PJ64_PATH, pos=(10,15))
        self.project64Dir = wx.DirPickerCtrl(tab1, pos=(100, 10), style=wx.DIRP_USE_TEXTCTRL | wx.DIRP_DIR_MUST_EXIST, size=(220,30), path=option.PROJECT_64_DIR)
        self.project64Dir.Bind(wx.EVT_DIRPICKER_CHANGED, self.updateConfigFunc)
        self.project64Dir.SetToolTip(lang.TOOLTIP_PJ64)

        tab2 = wx.Panel(notebook)
        notebook.AddPage(tab2,lang.SETTINGS_ADVANCED)
        
        organizer = wx.StaticBox(tab2, label=lang.SETTINGS_FINAL_EYE_TEXTURES, pos=(10,5), size=(305, 120))
        
        textureOpenLabel = wx.StaticText(tab2, label=lang.SETTINGS_OPEN_TEXTURE, pos=(20,30))
        self.textureOpenPath = wx.TextCtrl(tab2, pos=(125, 27), size=(180,22), value=option.TEXTUREPATH1)
        self.textureOpenPath.SetToolTip(lang.TOOLTIP_FINAL_EYE)

        textureMidLabel = wx.StaticText(tab2, label=lang.SETTINGS_MID_TEXTURE, pos=(20,60))
        self.textureMidPath = wx.TextCtrl(tab2, pos=(125, 57), size=(180,22), value=option.TEXTUREPATH2)
        self.textureMidPath.SetToolTip(lang.TOOLTIP_FINAL_EYE)

        textureClosedLabel = wx.StaticText(tab2, label=lang.SETTINGS_CLOSED_TEXTURE, pos=(20,90))
        self.textureClosedPath = wx.TextCtrl(tab2, pos=(125, 87), size=(180,22), value=option.TEXTUREPATH3)
        self.textureClosedPath.SetToolTip(lang.TOOLTIP_FINAL_EYE)

        resetOptions = wx.Button(tab2, pos=(5, 135), label = lang.SETTINGS_RESET_TO_DEFAULT)
        resetOptions.Bind(wx.EVT_BUTTON, self.resetCustomTexture)


        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Show()

    def updateConfigFunc(self, e):
        option.PROJECT_64_DIR = self.project64Dir.GetPath()
        if (self.textureOpenPath.GetValue() != ""): 
            option.TEXTUREPATH1 = self.textureOpenPath.GetValue()
        if (self.textureMidPath.GetValue() != ""): 
            option.TEXTUREPATH2 = self.textureMidPath.GetValue()
        if (self.textureClosedPath.GetValue() != ""): 
            option.TEXTUREPATH3 = self.textureClosedPath.GetValue()

        saveConfig()

        if (e.GetEventObject().GetName() == "Save"):
            self.Close()

    def resetCustomTexture(self, e):
        self.textureOpenPath.SetValue("SUPER MARIO 64#6B8D43C4#0#2_all")
        self.textureMidPath.SetValue("SUPER MARIO 64#9FBECEF9#0#2_all")
        self.textureClosedPath.SetValue("SUPER MARIO 64#5D6B0678#0#2_all")

# --- APP
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, lang.TITLE)
        self.frame.Show()
        self.frame.Center()

        #self.Bind(wx.EVT_IDLE, self.onIdle)

        return True

app = MyApp()
app.MainLoop()