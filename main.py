# -- LIBRARIES
import os
import configparser
import zipfile
import shutil
import requests
import webbrowser
from glob import glob

import wx
import wx.adv

import gettext
gettext.install("main")

# --- GLOBAL VARIABLES
APP_VERSION = "v1.0.1"

# --- OPTIONS
class optionVars():
    PROJECT_64_DIR = ""
    LANGUAGE = "en"
    THEME = "Light"
    TEXTUREPATH1 = "SUPER MARIO 64#6B8D43C4#0#2_all"
    TEXTUREPATH2 = "SUPER MARIO 64#9FBECEF9#0#2_all"
    TEXTUREPATH3 = "SUPER MARIO 64#5D6B0678#0#2_all"

option = optionVars()

# --- CONFIG
config = configparser.ConfigParser()

# save the current settings
def saveConfig():
    config.read('config.ini')

    config["CONFIG"] = {"PROJECT_64_DIR": option.PROJECT_64_DIR, "LANGUAGE": option.LANGUAGE, "THEME": option.THEME}
    config["ADV"] = {"TEXTUREPATH1": option.TEXTUREPATH1, "TEXTUREPATH2": option.TEXTUREPATH2, "TEXTUREPATH3": option.TEXTUREPATH3}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# load from config.ini
def loadConfig():
    config.read('config.ini')

    if ("CONFIG" in config):
        configSec = config["CONFIG"]

        option.PROJECT_64_DIR = configSec.get("PROJECT_64_DIR", option.PROJECT_64_DIR)
        option.LANGUAGE = configSec.get("LANGUAGE", option.LANGUAGE)
        option.THEME = configSec.get("THEME", option.THEME)

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

# -- THEMES & LANG

# sort through each theme and language file
# considering not using a stupid module system to make it more accessable to people who dont understand python stuff
def getModules(direc, ext):
    array = []
    if (ext != "dir"):
        for file in os.listdir(direc):
            if file.endswith(ext):
                if (file == "__init__.py"):
                    continue
                else:
                    array.append(file.removesuffix(ext))
    else:
        dirlist = glob(direc+"/*/")
        i = 0

        while i < len(dirlist):
            array.append(dirlist[i].replace("\\", "").replace(direc, "", 1))
            i += 1

    return array

THEMES = getModules("themes/", ".theme")
THEMES.insert(0, "Light")
LANGS = getModules("lang", "dir")
print("loaded " + str(len(THEMES)) + " themes " + str(THEMES))
print("loaded " + str(len(LANGS)) + " languages " + str(LANGS))

# themes
from loadtheme import themeClass
theme = themeClass(option.THEME)

# lang
def updateLang(language):
    if (language != "en"):
        if (gettext.find("main", localedir="lang", languages=[language]) is not None):
            curLang = gettext.translation("main", localedir="lang", languages=[language])
            curLang.install()
    else:
        gettext.install("main")

updateLang(option.LANGUAGE)
        
#import lang
#lang = lang.eng.LANG()

# --- OTHER FUNCTIONS
def getEyes():
    dirlist = glob("Eyes/*/")
    newlist = []
    i = 0

    while i < len(dirlist):
        newlist.append(dirlist[i].replace("\\", "").replace("Eyes", "", 1))
        i += 1

    return newlist

def DownloadGlide64(self):
    saveTo = option.PROJECT_64_DIR + "\\Plugin\\GLideN64.dll"

    if (os.path.isdir(option.PROJECT_64_DIR + "\\Plugin") is False):
        os.makedirs(option.PROJECT_64_DIR + "\\Plugin")

    if (os.access(saveTo, os.R_OK)):

        downloadFrom = "https://www.dropbox.com/s/fqqickpexrv676h/GLideN64.dll?dl=1"
        request = requests.get(downloadFrom, allow_redirects=True)
    
        open(saveTo, 'wb').write(request.content)

        finished = wx.MessageDialog(self, _("Successfully downloaded & added GLideN64 to Project64.\nPlease change your Graphics Plugin in Project64 to GLideN64, and enable Texture Packs."), _("GLide64 Installation"), style=wx.OK | wx.ICON_INFORMATION)
        finished.ShowModal()

    else:
        error = wx.MessageDialog(self, _("Insufficient permissions, could not install GLideN64.\nPlease run the program as administrator and try to install again.\nTo attempt to install GLideN64 again, click on the 'Help', then 'Install GLideN64'.") + _("\n\n(Could not save to ") + saveTo + ")", _("GLide64 Installation"), style=wx.OK | wx.ICON_ERROR)
        error.ShowModal()

# run when user first starts the app
# detection system may need to be changed later
def FirstTimeSetup(self):
    firstDialog = wx.MessageDialog(self, _("It seems this is your first time using SM64EC.\nPlease select the folder Project64 is stored in. (This can be changed later in settings)\n\nA dialog will open once you press 'OK'"), _("Welcome!"), style=wx.OK | wx.CANCEL | wx.ICON_INFORMATION)
    result = firstDialog.ShowModal()

    if (result == wx.ID_OK):
        pj64 = wx.DirDialog(self, _("Project 64 Directory"), style=wx.DD_DIR_MUST_EXIST | wx.RESIZE_BORDER)
        result = pj64.ShowModal()

        if (result == wx.ID_OK):
            option.PROJECT_64_DIR = pj64.GetPath()
            saveConfig()

            downloadGlide64 = wx.MessageDialog(self, _("Would you like to install GLideN64?"), _("Welcome!"), style=wx.YES_NO | wx.ICON_INFORMATION)
            result = downloadGlide64.ShowModal()

            if (result == wx.ID_YES):
                DownloadGlide64(self)
                

        else:
            self.Close()

    else:
        self.Close()

# -------------------------------- WINDOW CODE --------------------------------

# --- FRAME
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(610,520), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.Center()

        icon = wx.Icon("Assets/icon.ico")
        self.SetIcon(icon)
        
        self.defaultWindowStyle = self.GetWindowStyle()

        if (option.PROJECT_64_DIR == ""):
            FirstTimeSetup(self)

        self.SetBackgroundColour(theme.BACKGROUND)

        # status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetStatusText(APP_VERSION)

        # create a panel
        self.panel = PanelOne(self)

        # menu
        self.InitMenuBar(self)

    def InitMenuBar(self, e):
        menuFile = wx.Menu()
        menuCreateEye = menuFile.Append(wx.ID_NEW, _("New"), _("Create a new eye texture."))
        menuFile.AppendSeparator()
        menuExportEye = menuFile.Append(wx.ID_SAVE, _("Export..."), _("Export your current textures to a .zip file for sharing."))
        menuImportEye = menuFile.Append(wx.ID_OPEN, _("Import..."), _("Import a selection of texture files."))
        menuFile.AppendSeparator()
        menuRefresh = menuFile.Append(wx.ID_REFRESH, _("Refresh List"), _("Refresh your current list of textures."))
        menuFile.AppendSeparator()
        menuExit = menuFile.Append(wx.ID_EXIT, _("Exit"), _("Exit the program."))

        menuOptions = wx.Menu()
        self.menuAlwaysTop = menuOptions.AppendCheckItem(wx.ID_TOP, _("Always On Top"), _("Toggle the program to show above all windows."))
        menuOptions.AppendSeparator()
        menuSettings = menuOptions.Append(wx.ID_PREFERENCES, _("Settings..."), _("Configure the program to your liking."))

        menuHelp = wx.Menu()
        menuWiki = menuHelp.Append(wx.ID_HELP, _("Official Wiki"), _("Open the Official SM64EC Wiki in a new tab."))
        menuReport = menuHelp.Append(wx.ID_HELP_INDEX, _("Report a issue..."), _("If you find a problem with this program report it here."))
        menuGlide = menuHelp.Append(wx.ID_FILE, _("Install GLideN64"), _("Reinstall / Install the GLideN64 graphics plugin."))
        menuHelp.AppendSeparator()
        menuAbout = menuHelp.Append(wx.ID_ABOUT, _("About"), _("Information about this program."))

        menuBar = wx.MenuBar()
        menuBar.Append(menuFile, _("File"))
        menuBar.Append(menuOptions, _("Options"))
        menuBar.Append(menuHelp, _("Help"))
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.OnNew, menuCreateEye)
        self.Bind(wx.EVT_MENU, self.OnExport, menuExportEye)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImportEye)
        self.Bind(wx.EVT_MENU, self.OnRefresh, menuRefresh)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Bind(wx.EVT_MENU, self.OnOptions, menuSettings)
        self.Bind(wx.EVT_MENU, self.AlwaysOnTop, self.menuAlwaysTop)
        
        self.Bind(wx.EVT_MENU, self.OnWiki, menuWiki)
        self.Bind(wx.EVT_MENU, self.OnReport, menuReport)
        self.Bind(wx.EVT_MENU, self.OnGlide, menuGlide)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
    
    def OnWiki(self, e):
        webbrowser.open_new_tab("https://github.com/ImCodist/sm64-eye-changer/wiki")

    def OnReport(self, e):
        webbrowser.open_new_tab("https://github.com/ImCodist/sm64-eye-changer/issues")

    def OnGlide(self, e):
        DownloadGlide64(self)

    def OnAbout(self, e):
        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName(_("SM64 Eye Changer"))
        aboutInfo.SetVersion(APP_VERSION)
        aboutInfo.SetDescription(_("SM64EC is a tool created for Super Mario 64 machinima.\nThe tool allows for the quick swapping of Mario's eye texture in-game,\ngiving Mario more character and expression."))
        aboutInfo.SetWebSite("https://github.com/ImCodist/sm64-eye-changer")
        aboutInfo.AddDeveloper("@ImCodist / codist")
        aboutInfo.AddArtist("@GlitchyPSIX / GlitchyPSI (Default Eye Textures)")
        aboutInfo.SetLicence(_("This project uses the") + "\nGNU General Public License v3.0")

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

        organizer = wx.StaticBox(self, label= _("Eye Selection"), size=(230, 420), pos=(10, 5))
        organizer.SetForegroundColour(theme.FOREGROUND)
        organizer.SetBackgroundColour(theme.BACKGROUND2)

        self.listBox = wx.ListBox(self, style=wx.LB_SORT | wx.LB_SINGLE, size=(200, 330), pos=(25, 25), choices=self.eyes)
        self.listBox.Bind(wx.EVT_LISTBOX, self.selectEye)
        self.listBox.SetForegroundColour(theme.FOREGROUND)
        self.listBox.SetBackgroundColour(theme.BACKGROUND2)

        createBitmap = wx.Image(theme.I_CREATEEYE, type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        self.buttonCreate = wx.BitmapButton(self, bitmap=createBitmap, pos=(25, 365))
        self.buttonCreate.SetToolTip(_("Create a new eye texture."))
        self.buttonCreate.Bind(wx.EVT_BUTTON, self.createNewEye)
        self.buttonCreate.SetBackgroundColour(theme.BUTTON)

        deleteBitmap = wx.Image(theme.I_DELETEEYE, type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        self.buttonDelete = wx.BitmapButton(self, bitmap=deleteBitmap, pos=(80, 365))
        self.buttonDelete.SetToolTip(_("Delete an existing eye texture."))
        self.buttonDelete.Bind(wx.EVT_BUTTON, self.deleteEye)
        self.buttonDelete.SetBackgroundColour(theme.BUTTON)
        
        # unused as of now
        #editBitmap = wx.Image("Assets/editEye.png", type=wx.BITMAP_TYPE_ANY).Scale(40, 40).ConvertToBitmap()
        #self.buttonEdit = wx.BitmapButton(self, bitmap=editBitmap, pos=(135, 365), name="Edit")
        #self.buttonEdit.Bind(wx.EVT_BUTTON, self.createNewEye)

        organizer = wx.StaticBox(self, label=_("Eye Preview"), size=(310, 365), pos=(275, 5))
        organizer.SetForegroundColour(theme.FOREGROUND)
        organizer.SetBackgroundColour(theme.BACKGROUND2)

        eyePreviewBitmap = wx.Image(theme.I_UNKNOWN + "1.png", type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
        self.eyePreview = wx.StaticBitmap(self, bitmap=eyePreviewBitmap, pos=(280,20))
        self.eyePreview.SetBackgroundColour(theme.BACKGROUND2)

        self.slider = wx.Slider(self, value=1, minValue=1, maxValue=3, pos=(280, 325), size=(300, 40))
        self.slider.Bind(wx.EVT_SLIDER, self.previewFrame)

        self.freezeFrame = wx.CheckBox(self, label=_("Freeze Frame"), pos=(380, 390))
        self.freezeFrame.SetForegroundColour(theme.FOREGROUND)

        applyButton = wx.Button(self, label=_("APPLY"), pos=(485, 385), size=(100,30))
        applyButton.Bind(wx.EVT_BUTTON, self.applyEyes)
        applyButton.SetToolTip(_("Apply the currently selected eye texture to the game."))
        applyButton.SetForegroundColour(theme.FOREGROUND)
        applyButton.SetBackgroundColour(theme.BUTTON)


    def selectEye(self, e):
        val = self.slider.GetValue()
        selection = self.listBox.GetSelection()
        path = "Eyes/" + self.listBox.GetString(selection) + "/" + str(val) + ".png"

        if (os.path.isfile(path) is False):
            dialog = wx.MessageDialog(self, _("Could not load from the path:") + "\n" + path, "ERROR CODE 0", style=wx.OK | wx.ICON_ERROR)
            selection = self.listBox.GetSelection()
            shutil.rmtree("Eyes/" + self.listBox.GetString(selection))

            self.refreshList(self)
            dialog.ShowModal()
        else:
            newBitmap = wx.Image(path, type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
            self.eyePreview.SetBitmap(newBitmap)
    
    def createNewEye(self, e):
        self.dialog = NewEyeDialog(self, False)

    def deleteEye(self, e):
        selection = self.listBox.GetSelection()
        shutil.rmtree("Eyes/" + self.listBox.GetString(selection))

        self.refreshList(self)

    def previewFrame(self, e):
        val = self.slider.GetValue()
        selection = self.listBox.GetSelection()
        path = theme.I_UNKNOWN + str(val) + ".png"
        if (selection != wx.NOT_FOUND):
            path = "Eyes/" + self.listBox.GetString(selection) + "/" + str(val) + ".png"

        newBitmap = wx.Image(path, type=wx.BITMAP_TYPE_ANY).Scale(300, 300).ConvertToBitmap()
        self.eyePreview.SetBitmap(newBitmap)

    def applyEyes(self, e): 
        gameName = option.TEXTUREPATH1.split('#')[0]
        print(gameName)
        pathTo = option.PROJECT_64_DIR + "/Plugin/hires_texture/" + gameName +"/png_all"
        
        if (os.path.isdir(pathTo) is False):
            os.makedirs(pathTo)

        if (os.access(pathTo, os.R_OK) == False):
            dialog = wx.MessageDialog(self, _("Could not save to ")  + " '" + pathTo + "' " + _("\nRun the program as administrator and try again."), _("COULD NOT APPLY"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        if (os.path.isdir(option.PROJECT_64_DIR) is False):
            dialog = wx.MessageDialog(self, _("Please enter a valid Project 64 path."), _("ERROR CODE 1"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        # replace eye textures
        if (self.listBox.GetSelection() == wx.NOT_FOUND):
            dialog = wx.MessageDialog(self, _("Please select a eye texture to apply."), _("ERROR CODE 2"), style=wx.OK | wx.ICON_ERROR)
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

        dialog = wx.MessageDialog(self, _("Applied the")  + " '" + self.listBox.GetString(selection) + "' " + _("eye texture.\nPlease restart the game or load a savestate."), _("APPLIED"), style=wx.OK | wx.ICON_INFORMATION)
        dialog.ShowModal()

    def refreshList(self, e):
        self.eyes = getEyes()
        self.listBox.SetItems(self.eyes)
        
# --- NEW EYE DIALOG
class NewEyeDialog(wx.Frame):
    def __init__(self, parent, edit):
        super(NewEyeDialog, self).__init__(parent, title=_("Create New Eye"), size=(530,340), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        
        panel = wx.Panel(self, size=(530, 300))
        panel.SetBackgroundColour(theme.BACKGROUND)

        finishButton = wx.Button(panel, label=_("Finish"), pos=(430, 270))
        finishButton.Bind(wx.EVT_BUTTON, self.finish)
        finishButton.SetForegroundColour(theme.FOREGROUND)
        finishButton.SetBackgroundColour(theme.BUTTON)

        cancelButton = wx.Button(panel, label=_("Cancel"), pos=(345, 270))
        cancelButton.Bind(wx.EVT_BUTTON, self.cancel)
        cancelButton.SetForegroundColour(theme.FOREGROUND)
        cancelButton.SetBackgroundColour(theme.BUTTON)

        self.openLabel = wx.StaticText(panel, label=_("Opened"), pos=(20,55))
        self.midLabel = wx.StaticText(panel, label=_("Semi Opened"), pos=(180,55))
        self.closedLabel = wx.StaticText(panel, label=_("Closed"), pos=(340,55))
        self.openLabel.SetForegroundColour(theme.FOREGROUND)
        self.midLabel.SetForegroundColour(theme.FOREGROUND)
        self.closedLabel.SetForegroundColour(theme.FOREGROUND)

        noEye1Bitmap = wx.Image(theme.I_UNKNOWN+"1.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()
        noEye2Bitmap = wx.Image(theme.I_UNKNOWN+"2.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()
        noEye3Bitmap = wx.Image(theme.I_UNKNOWN+"3.png", type=wx.BITMAP_TYPE_ANY).Scale(150, 150).ConvertToBitmap()

        self.eyeOpenPreview = wx.StaticBitmap(panel, bitmap=noEye1Bitmap, pos=(20,70))
        self.eyeMidPreview = wx.StaticBitmap(panel, bitmap=noEye2Bitmap, pos=(180,70))
        self.eyeClosedPreview = wx.StaticBitmap(panel, bitmap=noEye3Bitmap, pos=(340,70))

        self.fileOpen = wx.FilePickerCtrl(panel, pos=(20,225),style=wx.FLP_OPEN, name="Open")
        self.fileMid = wx.FilePickerCtrl(panel, pos=(180,225),style=wx.FLP_OPEN, name="Mid")
        self.fileClosed = wx.FilePickerCtrl(panel, pos=(340,225),style=wx.FLP_OPEN, name="Closed")

        self.fileOpen.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)
        self.fileMid.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)
        self.fileClosed.Bind(wx.EVT_FILEPICKER_CHANGED, self.browseEye)

        self.eyeNameLabel = wx.StaticText(panel, label=_("Name"), pos=(20,10))
        self.eyeNameLabel.SetForegroundColour(theme.FOREGROUND)
        self.eyeName = wx.TextCtrl(panel, pos=(60, 10), size=(100,20))
        self.eyeName.SetForegroundColour(theme.FOREGROUND)
        self.eyeName.SetBackgroundColour(theme.BACKGROUND2)

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
            dialog = wx.MessageDialog(self, _("A name cannot be blank, silly. :P"), _("COULD NOT CREATE"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        newpath = "Eyes/" + self.eyeName.GetValue()

        if (os.path.exists(newpath)):
            dialog = wx.MessageDialog(self, _("An eye texture with this name already exists.\nPlease choose a different name."), _("COULD NOT CREATE"), style=wx.OK | wx.ICON_ERROR)
            dialog.ShowModal()
            return

        if (self.fileOpen.GetPath() == "" or self.fileMid.GetPath() == "" or self.fileClosed.GetPath() == ""):
            dialog = wx.MessageDialog(self, _("Please select a texture for each type of eye."), _("COULD NOT CREATE"), style=wx.OK | wx.ICON_ERROR)
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
        super(Options, self).__init__(parent, title=_("Settings"), size=(350,230), style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.Centre()
        panel = wx.Panel(self)
        panel.SetBackgroundColour(theme.BACKGROUND)

        apply = wx.Button(panel, label=_("Save"), pos=(250, 160), name="Save")
        apply.Bind(wx.EVT_BUTTON, self.updateConfigFunc)
        apply.SetForegroundColour(theme.FOREGROUND)
        apply.SetBackgroundColour(theme.BUTTON)

        notebook = wx.Notebook(panel)

        tab1 = wx.Panel(notebook)
        notebook.AddPage(tab1, _("General"))

        project64Label = wx.StaticText(tab1, label=_("Project64 Path"), pos=(10,15))
        project64Label.SetForegroundColour(theme.FOREGROUND)

        self.project64Dir = wx.DirPickerCtrl(tab1, pos=(100, 10), style=wx.DIRP_USE_TEXTCTRL | wx.DIRP_DIR_MUST_EXIST, size=(220,30), path=option.PROJECT_64_DIR)
        self.project64Dir.Bind(wx.EVT_DIRPICKER_CHANGED, self.updateConfigFunc)
        self.project64Dir.SetToolTip(_("Set the directory in which Project64 is stored.\nIS REQUIRED."))

        themeLabel = wx.StaticText(tab1, label=_("Theme"), pos=(10,53))
        themeLabel.SetForegroundColour(theme.FOREGROUND)
        self.themeBox = wx.Choice(tab1, pos=(100, 50), choices=THEMES, size=(100,30))
        self.themeBox.SetSelection(THEMES.index(option.THEME))
        self.themeBox.Bind(wx.EVT_CHOICE, self.updateThemeFunc)

        langageLabel = wx.StaticText(tab1, label=_("Language"), pos=(10,83))
        langageLabel.SetForegroundColour(theme.FOREGROUND)
        self.languageBox = wx.adv.BitmapComboBox(tab1 ,pos=(100, 80), size=(80,30))
        self.languageBox.Bind(wx.EVT_COMBOBOX, self.updateLangFunc)
        self.languageBox.SetForegroundColour(theme.FOREGROUND)
        self.languageBox.SetBackgroundColour(theme.BACKGROUND2)

        for lang in LANGS:
            path = "lang/"+lang

            settings = configparser.ConfigParser()
            settings.read(path+"/settings.ini")

            name = settings.get("SETTINGS", "name", fallback=lang)

            flag = path+"/flag.png"
            if (os.path.isfile(flag) is False):
                flag = "assets/unknown/flag.png"
            bitmap = wx.Image(flag, type=wx.BITMAP_TYPE_ANY).Scale(20, 15).ConvertToBitmap()

            self.languageBox.Append(name, bitmap)
            if (option.LANGUAGE == lang):
                self.languageBox.SetValue(name)

        flagBitmap = self.languageBox.GetItemBitmap(LANGS.index(option.LANGUAGE))
        self.flagPreview = wx.StaticBitmap(panel, bitmap=flagBitmap, pos=(190,108))

        tab2 = wx.Panel(notebook)
        notebook.AddPage(tab2,_("Advanced"))
        
        organizer = wx.StaticBox(tab2, label=_("Final Eye Textures"), pos=(10,5), size=(305, 120))
        
        toolTipWarning = _("When applying textures, this will be the final name of the files when copied.\nCan be used to work with ROMs that arent the base game.\nOnly change if you know what you are doing.")

        textureOpenLabel = wx.StaticText(tab2, label=_("Open Texture"), pos=(20,30))
        textureOpenLabel.SetForegroundColour(theme.FOREGROUND)
        self.textureOpenPath = wx.TextCtrl(tab2, pos=(125, 27), size=(180,22), value=option.TEXTUREPATH1)
        self.textureOpenPath.SetToolTip(toolTipWarning)
        self.textureOpenPath.SetForegroundColour(theme.FOREGROUND)
        self.textureOpenPath.SetBackgroundColour(theme.BACKGROUND2)

        textureMidLabel = wx.StaticText(tab2, label=_("Mid Texture"), pos=(20,60))
        textureMidLabel.SetForegroundColour(theme.FOREGROUND)
        self.textureMidPath = wx.TextCtrl(tab2, pos=(125, 57), size=(180,22), value=option.TEXTUREPATH2)
        self.textureMidPath.SetToolTip(toolTipWarning)
        self.textureMidPath.SetForegroundColour(theme.FOREGROUND)
        self.textureMidPath.SetBackgroundColour(theme.BACKGROUND2)

        textureClosedLabel = wx.StaticText(tab2, label=_("Closed Texture"), pos=(20,90))
        textureClosedLabel.SetForegroundColour(theme.FOREGROUND)
        self.textureClosedPath = wx.TextCtrl(tab2, pos=(125, 87), size=(180,22), value=option.TEXTUREPATH3)
        self.textureClosedPath.SetToolTip(toolTipWarning)
        self.textureClosedPath.SetForegroundColour(theme.FOREGROUND)
        self.textureClosedPath.SetBackgroundColour(theme.BACKGROUND2)

        resetOptions = wx.Button(tab2, pos=(5, 135), label = _("Reset To Default"))
        resetOptions.Bind(wx.EVT_BUTTON, self.resetCustomTexture)
        resetOptions.SetForegroundColour(theme.FOREGROUND)
        resetOptions.SetBackgroundColour(theme.BUTTON)


        sizer = wx.BoxSizer()
        sizer.Add(notebook, 1, wx.EXPAND)
        panel.SetSizer(sizer)

        self.Show()

    def updateConfigFunc(self, e):
        option.PROJECT_64_DIR = self.project64Dir.GetPath()
        #option.LANGUAGE = self.languageBox.GetValue()

        if (self.textureOpenPath.GetValue() != ""): 
            option.TEXTUREPATH1 = self.textureOpenPath.GetValue()
        if (self.textureMidPath.GetValue() != ""): 
            option.TEXTUREPATH2 = self.textureMidPath.GetValue()
        if (self.textureClosedPath.GetValue() != ""): 
            option.TEXTUREPATH3 = self.textureClosedPath.GetValue()

        saveConfig()

        if (e.GetEventObject().GetName() == "Save"):
            self.Close()

    def updateThemeFunc(self, e):
        option.THEME = THEMES[self.themeBox.GetSelection()]

        theme = themeClass(option.THEME)
        saveConfig()

        app.frame.Close()

        app.OnInit()
        app.frame.OnOptions(e)

    def updateLangFunc(self, e):
        option.LANGUAGE = LANGS[self.languageBox.GetSelection()]

        updateLang(option.LANGUAGE)
        saveConfig()

        app.frame.Close()

        app.OnInit()
        app.frame.OnOptions(e)

    def resetCustomTexture(self, e):
        self.textureOpenPath.SetValue("SUPER MARIO 64#6B8D43C4#0#2_all")
        self.textureMidPath.SetValue("SUPER MARIO 64#9FBECEF9#0#2_all")
        self.textureClosedPath.SetValue("SUPER MARIO 64#5D6B0678#0#2_all")

# --- APP
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(None, _("SM64 EYE CHANGER"))
        self.frame.Show()

        # self.Bind(wx.EVT_IDLE, self.onIdle)

        return True

app = MyApp()
app.MainLoop()