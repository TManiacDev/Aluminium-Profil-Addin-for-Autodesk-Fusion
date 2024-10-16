"""
This is a simple support for translation
"""
import os
from  adsk.core import UserLanguages as fusionUserLanguages
import xml.etree.ElementTree as xmlElementTree

from ..lib import fusion360utils as futil 

fusionLanguages = {
   fusionUserLanguages.ChinesePRCLanguage       : None,
   fusionUserLanguages.ChineseTaiwanLanguage    : 'english',
   fusionUserLanguages.CzechLanguage            : 'english',
   fusionUserLanguages.EnglishLanguage          : 'english',
   fusionUserLanguages.FrenchLanguage           : None, 
   fusionUserLanguages.GermanLanguage           : 'german', 
}

class Language:
    """
    This class support unknwon translations on a very simple way
    """
    def __init__(self, 
                 default: fusionUserLanguages  = fusionUserLanguages.EnglishLanguage, 
                 parentDir:str = None, 
                 showMissingTranslation:bool = False):
        """

        """
        self.__showMissingTranslation = showMissingTranslation
        self.__language = fusionLanguages[default]
        futil.log(f'Languages: {str(fusionLanguages)}') 
        futil.log(f'Default: {str(default)}') 
        self.__parentDir = parentDir
        dictName = self.__language + ".xml"
        self.__xmlDictionaries = []
        # load standard dictionary
        standardDictName = os.path.dirname(os.path.abspath(__file__)) + '\\' + dictName
        self.__xmlDictionaries.append(self.__readDataFromXmlFile(standardDictName))
        # load specialiced dictionary
        if parentDir != None:
            pathName = parentDir  + dictName
            self.nextDict = self.__readDataFromXmlFile(pathName)
            self.__xmlDictionaries.append(self.nextDict)

            

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
        

    def getTranslation(self, searchEntry:str) -> str:
        if self.__xmlDictionaries == []:
            dictReturn = 'no xml directory'
        else:            
            # we need a good way to query all dictionaries in reverse because the first dictionary is the standard dictionary
            
            for xmlDict in self.__xmlDictionaries:
                xmlRoot = xmlDict.getroot()
                searchQuery = "./translation[@name='" + searchEntry + "']"
                xmlFind = xmlRoot.find(searchQuery)
                if ( xmlFind != None ):
                    dictReturn = xmlFind.text.strip()
                    return dictReturn
            
            if self.__showMissingTranslation:
                dictReturn = searchEntry + ' (unkown word on xml)'
            else:
                dictReturn = searchEntry
        return dictReturn
    