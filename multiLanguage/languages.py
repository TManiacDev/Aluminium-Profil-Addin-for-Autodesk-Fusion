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
        self.__readDataFromXmlFile("english.xml")

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
           self.__xmlDictionary =  xmlElementTree.parse(f'{os.path.dirname(os.path.abspath(__file__))}\{filePath}')
        except:
            self.__xmlDictionary = None
        
    def dictonaryByAdskLanguage(self):
        #  hmmm wie weiter ???
        return None

        
    def getTranslation(self, searchEntry, subDictionary: str = 'standard'):
        if subDictionary.lower() == 'standard':
            try:
                dictReturn = language[self.__language].standardWords[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1          
        elif subDictionary.lower() == 'addin':
            try:
                dictReturn = language[self.__language].interfaceName[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'  
                self.__unknownCounter += 1    
        elif subDictionary.lower() == 'createbycoordcommand':
            try:
                dictReturn = language[self.__language].createByCoordCommand[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1         
        elif subDictionary.lower() == 'analyzemotioncommand':
            try:
                dictReturn = language[self.__language].analyzeMotionCommand[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1       
        elif subDictionary.lower() == 'attribute':
            try:
                dictReturn = language[self.__language].attributeName[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1
        elif subDictionary.lower() == 'component':
            try:
                dictReturn = language[self.__language].componentName[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1
        elif subDictionary.lower() == 'construction':
            try:
                dictReturn = language[self.__language].constructionName[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1
        elif subDictionary.lower() == 'joint':
            try:
                dictReturn = language[self.__language].jointName[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1
        elif subDictionary.lower() == 'customfeature':
            try:
                dictReturn = language[self.__language].customFeature[searchEntry]
            except:
                dictReturn = 'unknown word (' +str(self.__unknownCounter) + ')'
                self.__unknownCounter += 1
        else:
            dictReturn = 'unkwon dictionary'                

        return dictReturn

    def getTranslation2(self, searchEntry):
        if self.__xmlDictionary == None:
            dictReturn = 'no xml directory'
        else:            
            xmlRoot = self.__xmlDictionary.getroot()
            searchQuery = "./translation[@name='" + searchEntry + "']"
            try:
                dictReturn = xmlRoot.find(searchQuery).text
            except:
                dictReturn = 'unkown word on xml'
        return dictReturn
    