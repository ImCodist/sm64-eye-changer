import os
import configparser
import wx

class themeClass():
    
    def __init__(self, theme):
        
        def parseColor(array):
            if (array != "N/A"):
                array = array.split(", ")
                numArray = []
                for x in array:
                    numArray.append(int(x))
                
                return wx.Colour(numArray[0], numArray[1], numArray[2])

        file = "themes/"+theme+".theme"

        themeFile = configparser.ConfigParser()
        themeFile.read(file)

        self.FOREGROUND = parseColor(themeFile.get("THEME", "FOREGROUND", fallback="N/A"))
        self.BACKGROUND = parseColor(themeFile.get("THEME", "BACKGROUND", fallback="N/A"))
        self.BACKGROUND2 = parseColor(themeFile.get("THEME", "BACKGROUND2", fallback="N/A"))
        self.BUTTON = parseColor(themeFile.get("THEME", "BUTTON", fallback="N/A"))

        self.I_CREATEEYE = themeFile.get("THEME", "I_CREATEEYE", fallback="assets/createEye.png")
        self.I_DELETEEYE = themeFile.get("THEME", "I_DELETEEYE", fallback="assets/deleteEye.png")
        self.I_EDITEYE = themeFile.get("THEME", "I_EDITEYE", fallback="assets/editEye.png")
        self.I_UNKNOWN = themeFile.get("THEME", "I_UNKNOWN", fallback="assets/Unknown/")