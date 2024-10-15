"""
This file handles the access to the profile library
The library is a list of xml trees
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
        """
        get a list of manufature names 
        """
        nameList = []
        for lib in self.__libraries:
            libRoot = lib.getroot()
            manuTag = libRoot.get("manufacture")
            nameList.append(manuTag)
        return nameList
    
    def getAll(self): 
        return self.__libraries
    
    def getLibraryByIndex(self, index: int ) -> xmlElementTree:
        """
        get the xml tree of a single manufacture library by index
        """
        return self.__libraries[index]

    def getProfilList(self, libIndex: int) -> list[xmlElementTree.Element]:
        """
        get a list of profiles from a single manufacture library
        """
        profilList = []
        lib = self.__libraries[libIndex]
        libRoot = lib.getroot()
        for child in libRoot:
            profilList.append(child.attrib)
        return profilList
    
    def getFolder(self) -> str:
        """
        Get the full path of the profile library entry
        """
        return os.path.dirname(os.path.abspath(__file__))
    
    def getProfileFilePath(self, manufactureName:str, profileName:str ) -> str:        
        for lib in self.__libraries:
            libRoot = lib.getroot()
            manuTag = libRoot.get("manufacture")
            if manuTag == manufactureName:
                searchTag = "./profile[@name='" + profileName + "']"
                #searchTag = "./profile[@name='P40x120L_N8_I']"
                profile = libRoot.find(searchTag)
                if profile != None:
                    fileName = self.getFolder() + '\\' + manuTag + '\\' + profile.find("dxf-file").text
                else:
                    fileName = "can't find profile " + searchTag + " -> " + str(libRoot.attrib)

        fullPath = fileName
        return fullPath

    def __readDataFromXmlFile(self, filePath):
        """
        parse the xml file to xml tree
        """
        try:
            xmlDictionary =  xmlElementTree.parse(filePath)
            self.xmlError = xmlElementTree.ParseError
            return xmlDictionary
        except:
            self.xmlError = xmlElementTree.ParseError
            return None