"""
This file handles the access to the profile library
"""
import os

import xml.etree.ElementTree as xmlElementTree

class AluProfileLibrary:
    def __init__(self):
        self.__libraries = []
        # load standard dictionary
        standardDictName = os.path.dirname(os.path.abspath(__file__)) + '\\' + "Motedis.xml"
        self.__libraries.append(self.__readDataFromXmlFile(standardDictName))

    def getLibNameList(self):
        nameList = []
        for lib in self.__libraries:
            libRoot = lib.getroot()
            manuTag = libRoot.get("manufacture")
            nameList.append(manuTag)
        return nameList
    
    def getAll(self): 
        return self.__libraries
    
    def getLibraryByIndex(self, index: int ) -> xmlElementTree:
        return self.__libraries[index]

    def getProfilList(self, libIndex: int) -> list[xmlElementTree.Element]:
        profilList = []
        lib = self.__libraries[libIndex]
        libRoot = lib.getroot()
        for child in libRoot:
            profilList.append(child.attrib)
        return profilList
    
    def getFolder(self):
        return os.path.dirname(os.path.abspath(__file__))

    def __readDataFromXmlFile(self, filePath):
        try:
            xmlDictionary =  xmlElementTree.parse(filePath)
            self.xmlError = xmlElementTree.ParseError
            return xmlDictionary
        except:
            self.xmlError = xmlElementTree.ParseError
            return None