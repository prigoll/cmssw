#!/usr/bin/env python

##########################################################################
##  Classes which are needed by the mps_validate.py file.
##

class GeometryGetter:
    """ Getting human readable names of detector parts
    """
    
    objid_names = {-1: "notfound", 0: "invalid", 1: "AlignableDetUnit", 2: "AlignableDet", 3: "TPBModule", 4: "TPBLadder", 5: "TPBLayer", 6: "TPBHalfBarrel", 7: "TPBBarrel", 8: "TPEModule", 9: "TPEPanel", 10: "TPEBlade", 11: "TPEHalfDisk", 12: "TPEHalfCylind", 13: "TPEEndcap", 14: "TIBModule", 15: "TIBString", 16: "TIBSurface", 17: "TIBHalfShell", 18: "TIBLayer", 19: "TIBHalfBarrel", 20: "TIBBarrel", 21: "TIDModule", 22: "TIDSide", 23: "TIDRing", 24: "TIDDisk", 25: "TIDEndcap", 26: "TOBModule", 27: "TOBRod", 28: "TOBLayer", 29: "TOBHalfBarrel", 30: "TOBBarrel", 31: "TECModule", 32: "TECRing", 33: "TECPetal", 34: "TECSide", 35: "TECDisk", 36: "TECEndcap", 37: "Pixel", 38: "Strip", 39: "Tracker", 100: "AlignableDTBarrel", 101: "AlignableDTWheel", 102: "AlignableDTStation", 103: "AlignableDTChamber", 104: "AlignableDTSuperLayer", 105: "AlignableDTLayer", 106: "AlignableCSCEndcap", 107: "AlignableCSCStation", 108: "AlignableCSCRing", 109: "AlignableCSCChamber", 110: "AlignableCSCLayer", 111: "AlignableMuon", 112: "Detector", 1000: "Extras", 1001: "BeamSpot"}
    
    # TODO last value is guessed
#    boundaries_bStruct = [61, 17541, 37021, 121061, 144401, 284201, 700000, 1000000]
    boundariesStruct = [ [61, 8781], [17541, 19961, 22401,  24821, 27281, 29701, 32141, 34561], [37021, 79041], [121061, 132721], [144401, 214301], [284201, 380121], [700000], [1000000] ]
    namebStruct = ["TrackerTPBHalfBarrel", "TrackerTPEHalfDisk", "TrackerTIBHalfBarrel", "TrackerTIDEndcap", "TrackerTOBHalfBarrel", "TrackerTECEndcap", "newIOV"]
    
    def __init__(self):
        self.bStructs = []
        for i, name in enumerate(self.namebStruct):
            self.bStructs.append(Struct(name, self.boundariesStruct[i][0], self.boundariesStruct[i+1][0]-1, True))
            for j in range(len(self.boundariesStruct[i])):
                # end of big strucutre
                if ( j+1 == len(self.boundariesStruct[i]) ):
                    self.bStructs[i].children.append(Struct("{0} {1}".format(name, j+1), self.boundariesStruct[i][j], self.boundariesStruct[i+1][0]-1))    
                else:
                    self.bStructs[i].children.append(Struct("{0} {1}".format(name, j+1), self.boundariesStruct[i][j], self.boundariesStruct[i][j+1])) 
                
        
        
    def name_by_objid(self, objid):
        return self.objid_names[objid]
    
    def listbStructs(self):
        return self.bStructs
    
    # check if label is in the range of the structlabels specified by bStructNumber
    def label_in_bStruct(self, label, bStructNumber):
        # check if it is the last structure
        if (bStructNumber < len(self.boundaries_bStruct)):
            # check if label is between boundaries
            if (label > self.boundaries_bStruct[bStructNumber] and label < self.boundaries_bStruct[bStructNumber+1]):
                return True
        elif (label > self.boundaries_bStruct[bStructNumber]):
            return True

class Struct:
    """ informaion about the physical structs in the detector
    """
    def __init__(self, name, begin, end, big = False):
        self.name = name
        self.begin = begin
        self.end = end
        self.big = big
        self.children = []
        
    def addChild(self, child):
        self.children.append(child)
        
    def getChildren(self):
        return self.children
    
    def getName(self):
        return self.name
    
    def containLabel(self, label):
        if (label > self.begin and label < self.end):
            return True
        else:
            return False
    
    
class TreeData:
    """ Hold information about XYZ
    """
    
    
    
    def __init__(self, mode):
        self.numberOfBins = [0, 0, 0]
        self.maxShift = [0, 0, 0]
        self.maxBinShift = [0, 0, 0]
        # used binShift
        self.binShift = [0, 0, 0]
        self.hiddenEntries = [0, 0, 0]
        self.binPosition = [1, 1, 1]
        self.histo = []
        self.histoAxis = []
        # plot title and text
        self.title = 0
        self.text = 0
        # switch mode for position, rotation, distortion
        if (mode=="xyz"):
            self.xyz = {0: "X", 1: "Y", 2: "Z"}
            self.data = [0, 1, 2]
        if (mode=="rot"):
            self.xyz = {0: "#alpha", 1: "#beta", 2: "#gamma"}
            self.data = [3, 4, 5]
        if (mode=="dist"):
            self.xyz = {0: "A", 1: "B", 2: "C"}
            self.data = [6, 7, 8]
        
class LogData:
    """ information out of the pede.dump.gz file
    """
    
    def __init__(self):
        self.sumValue = 0
        self.sumWValue = 0
        self.sumSteps = ""
        self.correction = 0
        self.memory = 0
        self.time = []
        self.warning = []
        # number of records
        self.nrec = 0
        # total numer of parameters
        self.ntgb = 0
        # number of variable parameters
        self.nvgb = 0
        
    def printLog(self):
        if (self.sumValue != 0):
            print "Sum(Chi^2)/Sum(Ndf) = {0} = {1}".format(self.sumSteps, self.sumValue)
        else:
            print "Sum(W*Chi^2)/Sum(Ndf)/<W> = {0} = {1}".format(self.sumSteps, self.sumWValue)
        print "with correction for down-weighting: {0}".format(self.correction)
        print "Peak dynamic memory allocation: {0} GB".format(self.memory)
        print "Total time: {0} h {1} m {2} s".format(self.time[0], self.time[1], self.time[2])
        print "Number of records: {0}".format(self.nrec)
        print "Total number of parameters: {0}".format(self.ntgb)
        print "Number of variable parameters: {0}".format(self.nvgb)
        print "Warning:"
        for line in self.warning:
            print line

        