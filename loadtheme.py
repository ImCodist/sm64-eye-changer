import os
import configparser
import wx

class themeClass():
    FOREGROUND = "N/A"
    BACKGROUND = "N/A"
    BACKGROUND2 = "N/A"
    BUTTON = "N/A"

    I_CREATEEYE = "assets/createEye.png"
    I_DELETEEYE = "assets/deleteEye.png"
    I_EDITEYE = "assets/editEye.png"
    I_UNKNOWN = "assets/Unknown/"
    
    def __init__(self, theme):
        
        def parseColor(array):
            array = array.split(", ")
            numArray = []
            for x in array:
                numArray.append(int(x))
            
            return wx.Colour(numArray[0], numArray[1], numArray[2])

        file = "themes/"+theme+".theme"
        if (os.path.isfile(file)):
            themeFile = configparser.ConfigParser()
            themeFile.read(file)

            if ("THEME" in themeFile):
                themeSec = themeFile["THEME"]

                self.FOREGROUND = parseColor(themeSec.get("FOREGROUND", self.FOREGROUND))
                self.BACKGROUND = parseColor(themeSec.get("BACKGROUND", self.BACKGROUND))
                self.BACKGROUND2 = parseColor(themeSec.get("BACKGROUND2", self.BACKGROUND2))
                self.BUTTON = parseColor(themeSec.get("BUTTON", self.BUTTON))

                self.I_CREATEEYE = themeSec.get("I_CREATEEYE", self.I_CREATEEYE)
                self.I_DELETEEYE = themeSec.get("I_DELETEEYE", self.I_DELETEEYE)
                self.I_EDITEYE = themeSec.get("I_EDITEYE", self.I_EDITEYE)
                self.I_UNKNOWN = themeSec.get("I_UNKNOWN", self.I_UNKNOWN)