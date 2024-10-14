"""
This is a simple support for translation
"""
import os
from . import english
from . import german
from  adsk.core import UserLanguages as fusionUserLanguages
import xml.etree.ElementTree as xmlElementTree

# the english file has the creation of the dictionary
# don't copy this line to your language
language = {
    'english' : english,
    'german'  : german,
    'deutsch'  : german
}

fusionLanguages = {
   fusionUserLanguages.ChinesePRCLanguage       : None,
   fusionUserLanguages.ChineseTaiwanLanguage    : english,
   fusionUserLanguages.CzechLanguage            : english,
   fusionUserLanguages.EnglishLanguage          : english,
   fusionUserLanguages.FrenchLanguage           : None, 
   fusionUserLanguages.GermanLanguage           : german, 
}

class Language:
    """
    This class support unknwon translations on a very simple way
    """
    def __init__(self, default: str = 'english', parentDir:str = None):
        self.__language = default.lower()
        self.__unknownCounter = 0
        self.__parentDir = parentDir
        dictName = default + ".xml"
        self.__xmlDictionaries = []
        self.xmlPaths = []
        # load standard dictionary
        # f'{os.path.dirname(os.path.abspath(__file__))}\
        # load specialiced dictionary
        if parentDir != None:
            pathName = parentDir  + dictName
            self.xmlPaths.append(pathName)
            self.nextDict = self.__readDataFromXmlFile(pathName)
            self.__xmlDictionaries.append(self.nextDict)
        else:
            self.nextDict = "what is happen"

            
        standardDictName = os.path.dirname(os.path.abspath(__file__)) + '\\' + dictName
        self.xmlPaths.append(standardDictName)
        self.__xmlDictionaries.append(self.__readDataFromXmlFile(standardDictName))

    @property
    def directory(self) -> bool:
        """
        Gets and sets the directory where the translation will be.
        """
        # maybe we do a test to check all components are ready
        return self.__parentDir
    
    @directory.setter
    def directory(self, parentDir:str):
        self.__parentDir = parentDir

    def __readDataFromXmlFile(self, filePath):
        try:
            xmlDictionary =  xmlElementTree.parse(filePath)
            self.xmlError = xmlElementTree.ParseError
            return xmlDictionary
        except:
            self.xmlError = xmlElementTree.ParseError
            return None
        
    def dictonaryByAdskLanguage(self):
        #  hmmm wie weiter ???
        return None

    def getDictName(self, pos):
        return self.__xmlDictionaries[pos].getroot()
        

    def getTranslation(self, searchEntry):
        if self.__xmlDictionaries == []:
            dictReturn = 'no xml directory'
        else:            
            # we need a good way to query all dictionaries in reverse because the first dictionary is the standard dictionary
            xmlRoot = self.__xmlDictionaries[1].getroot()
            searchQuery = "./translation[@name='" + searchEntry + "']"
            try:
                dictReturn = xmlRoot.find(searchQuery).text
            except:
                dictReturn = 'unkown word on xml'
        return dictReturn
    