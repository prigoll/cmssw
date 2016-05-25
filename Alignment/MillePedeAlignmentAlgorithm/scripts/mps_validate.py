#!/usr/bin/env python
from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText, gStyle

import argparse
import gzip
import logging
import os
import re

class GeometryGetter:
    """ Getting human readable names of detector parts
    """
    
    objid_names = {-1: "notfound", 0: "invalid", 1: "AlignableDetUnit", 2: "AlignableDet", 3: "TPBModule", 4: "TPBLadder", 5: "TPBLayer", 6: "TPBHalfBarrel", 7: "TPBBarrel", 8: "TPEModule", 9: "TPEPanel", 10: "TPEBlade", 11: "TPEHalfDisk", 12: "TPEHalfCylind", 13: "TPEEndcap", 14: "TIBModule", 15: "TIBString", 16: "TIBSurface", 17: "TIBHalfShell", 18: "TIBLayer", 19: "TIBHalfBarrel", 20: "TIBBarrel", 21: "TIDModule", 22: "TIDSide", 23: "TIDRing", 24: "TIDDisk", 25: "TIDEndcap", 26: "TOBModule", 27: "TOBRod", 28: "TOBLayer", 29: "TOBHalfBarrel", 30: "TOBBarrel", 31: "TECModule", 32: "TECRing", 33: "TECPetal", 34: "TECSide", 35: "TECDisk", 36: "TECEndcap", 37: "Pixel", 38: "Strip", 39: "Tracker", 100: "AlignableDTBarrel", 101: "AlignableDTWheel", 102: "AlignableDTStation", 103: "AlignableDTChamber", 104: "AlignableDTSuperLayer", 105: "AlignableDTLayer", 106: "AlignableCSCEndcap", 107: "AlignableCSCStation", 108: "AlignableCSCRing", 109: "AlignableCSCChamber", 110: "AlignableCSCLayer", 111: "AlignableMuon", 112: "Detector", 1000: "Extras", 1001: "BeamSpot"}
    
    # TODO last value is guessed
#    boundaries_bStruct = [61, 17541, 37021, 121061, 144401, 284201, 700000, 1000000]
    boundariesStruct = [ [61, 8781], [17541, 19961, 22401,  24821, 27281, 29701, 32141, 34561], [37021, 79041], [144401, 214301], [121061, 132721], [284201, 380121], [700000], [1000000] ]
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
    
    xyz = {0: "X", 1: "Y", 2: "Z"}
    
    def __init__(self):
        self.numberOfBins = [0, 0, 0]
        self.maxShift = [0, 0, 0]
        self.maxBinShift = [0, 0, 0]
        # used binShift
        self.binShift = [0, 0, 0]
        self.hiddenEntries = [0, 0, 0]
        self.binPosition = [1, 1, 1]
        self.histo = []
        self.histoAxis = []
        
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
        
    def print_log(self):
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
                        


def main():
    # config logging module
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                       datefmt="%d.%m.%Y %H:%M:%S")
    
    
    geometryGetter = GeometryGetter()

    
    # ArgumentParser
    parser = argparse.ArgumentParser(description="Validate your Aligment.")
    # TODO set default -> 0
    parser.add_argument("-j", "--job", help="chose jobmX directory (default: 0)", default=3, type=int)
    parser.add_argument("-t", "--time", help="chose MillePedeUser_X Tree (default: 1)", default=1, type=int)
    args = parser.parse_args()
    
    # TODO get latest Alignment directory
    alignmentNumber = args.job
    
    # TODO which time MillePedeUser_X
    alignmentTime = args.time
    
    # jobData path
    if (alignmentNumber == 0):
        jobDataPath = "./jobData/jobm"
    else:
        jobDataPath = "./jobData/jobm{0}".format(alignmentNumber)
    
    # create output directories
    outputPath = "validate"
    if not os.path.exists("{0}/plots".format(outputPath)):
        os.makedirs("{0}/plots".format(outputPath))
    
    
    # parse pede.dump.gz
    
    logData = LogData()
    
    # only recognize warning the first time
    warningBool = False
    
    # save lines in list
    with gzip.open("{0}/pede.dump.gz".format(jobDataPath)) as gzipFile:
        dumpFile = gzipFile.readlines()
    
    for i, line in enumerate(dumpFile):
        # Sum(Chi^2)/Sum(Ndf)
        if ("Sum(Chi^2)/Sum(Ndf) =" in line):
            number = []
            number.append(map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i])))
            number.append(map(int, re.findall(r"[-+]?\d+", dumpFile[i+1])))
            number.append(map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i+2])))
            logData.sumSteps = "{0} / ( {1} - {2} )".format(number[0][0], number[1][0], number[1][1])
            logData.sumValue = number[2][0]
            
        # Sum(W*Chi^2)/Sum(Ndf)/<W>
        if ("Sum(W*Chi^2)/Sum(Ndf)/<W> =" in line):
            number = []
            number.append(map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i])))
            number.append(map(int, re.findall(r"[-+]?\d+", dumpFile[i+1])))
            number.append(map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i+2])))
            number.append(map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i+3])))
            logData.sumSteps = "{0} / ( {1} - {2} ) / {3}".format(number[0][0], number[1][0], number[1][1], number[2][0])
            logData.sumWValue = number[3][0]
        
        if ("with correction for down-weighting" in line):
            number = map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i]))
            logData.correction = number[0]
            
        # Peak dynamic memory allocation
        if ("Peak dynamic memory allocation:" in line):
            number = map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i]))
            logData.memory = number[0]
            
        # total time
        if ("Iteration-end" in line):
            number = map(int, re.findall(r"\d+", dumpFile[i+1]))
            logData.time = number[:3]
            
        # warings
        if ("WarningWarningWarningWarning" in line and warningBool == False):
            warningBool = True
            j = i+8
            print "WARNING:"
            while ("Warning" not in dumpFile[j]): 
                logData.warning.append(dumpFile[j])
                j += 1
                
        # nrec number of records
        if (" = number of records" in line):
            number = map(int, re.findall("\d+", dumpFile[i]))
            logData.nrec = number[0]
        
        # ntgb total number of parameters
        if (" = total number of parameters" in line):
            number = map(int, re.findall("\d+", dumpFile[i]))
            logData.ntgb = number[0]
        
        # nvgb number of variable parameters
        if (" = number of variable parameters" in line):
            number = map(int, re.findall("\d+", dumpFile[i]))
            logData.nvgb = number[0]
            
            
    logData.print_log()

    
    
    
    # TODO check if there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    treeFile = TFile("{0}/treeFile_merge.root".format(jobDataPath))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(alignmentTime))
    
    ######################################################################################
    # big structures
    
        
    # more space for labels
    gStyle.SetPadBottomMargin(0.25)
    
    cBig = TCanvas("canvasBigStrucutres", "Parameter", 300, 0, 800, 600)
    cBig.Divide(2,2)
    
    big = TreeData()
    
    # count number of needed bins and max shift
    for line in MillePedeUser:
        if (line.ObjId != 1):
            for i in range(3):
                if (abs(line.Par[i]) != 999999):
                    big.numberOfBins[i] += 1
                    if (abs(line.Par[i]) > big.maxShift[i]):
                        big.maxShift[i] = abs(line.Par[i])
    
    # initialize histograms
    for i in range(3):
        big.histo.append(TH1F("Big Structure {0}".format(big.xyz[i]), "Parameter {0}".format(big.xyz[i]), big.numberOfBins[i], 0, big.numberOfBins[i]))
        big.histo[i].SetYTitle("[cm]")
        big.histo[i].SetStats(0)
        big.histo[i].SetMarkerStyle(2)
        big.histoAxis.append(big.histo[i].GetXaxis())
        # bigger labels for the text
        big.histoAxis[i].SetLabelSize(0.06)
        big.histo[i].GetYaxis().SetTitleOffset(1.6)
        
    
    # add labels
    title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Big Structures")
    text = TPaveText(0.05, 0.1, 0.95, 0.75)
    text.SetTextAlign(13)
    text.SetTextSizePixels(22)
    
    # TODO chose good limit
    # error if shift is bigger than limit
    limit = 0.02
    for i in range(3):
        text.AddText("max. shift {0}: {1:.2}".format(big.xyz[i], big.maxShift[i]))
        if (big.maxShift[i] > limit):
            text.AddText("! {0} shift bigger than {1} !".format(big.xyz[i], limit))
    
    # fill histograms with value and name
    for line in MillePedeUser:
        if (line.ObjId != 1):
            for i in range(3):
                if (abs(line.Par[i]) != 999999):
                    big.histoAxis[i].SetBinLabel(big.binPosition[i], geometryGetter.name_by_objid(line.ObjId))
                    big.histo[i].SetBinContent(big.binPosition[i], line.Par[i])
                    big.binPosition[i] += 1
    
    # rotate labels
    for i in range(3):
        big.histoAxis[i].LabelsOption("v")
    
    cBig.cd(1)
    title.Draw()
    text.Draw()
    cBig.cd(2)
    # option "p" to use marker
    big.histo[0].Draw("p")
    cBig.cd(3)
    big.histo[1].Draw("p")
    cBig.cd(4)
    big.histo[2].Draw("p")
    cBig.Update()
    
    # export as png
    image = TImage.Create()
    image.FromPad(cBig)
    image.WriteImage("{0}/plots/Big.png".format(outputPath))
    
    # reset BottomMargin
    gStyle.SetPadBottomMargin(0.1)

    
    ######################################################################################
    # module Struct
    
    cMod = []
    
    # loop over all structures
    for bStructNumber, bStruct in enumerate(geometryGetter.listbStructs()):
        cMod.append(TCanvas("canvasModules{0}".format(bStruct.getName()), "Parameter", 300, 0, 800, 600))
        cMod[bStructNumber].Divide(2, 2)
        
        mod = TreeData()
        
        numberOfBins = 10000
                        
        # initialize histograms
        for i in range(3):
            mod.histo.append(TH1F("{0} {1}".format(bStruct.getName(), mod.xyz[i]), "Parameter {0}".format(mod.xyz[i]), numberOfBins, -0.1, 0.1))
            mod.histo[i].SetXTitle("[cm]")
            mod.histoAxis.append(mod.histo[i].GetXaxis())
        
        # add labels
        title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0}".format(bStruct.getName()))
        text = TPaveText(0.05, 0.1, 0.95, 0.75)
        text.SetTextAlign(13)
        text.SetTextSizePixels(20)        

        # fill histogram
        for line in MillePedeUser:
            if (line.ObjId == 1 and bStruct.containLabel(line.Label)):
                for i in range(3):
                    if (abs(line.Par[i]) != 999999): 
                        mod.histo[i].Fill(line.Par[i])
                        
        # find the best range
        for i in range(3):
            # get first and last bin with content and chose the one which has a greater distance to the center
            mod.maxBinShift[i] = max( abs(numberOfBins/2-mod.histo[i].FindFirstBinAbove()), abs(mod.histo[i].FindLastBinAbove()-numberOfBins/2) )
            # skip empty histogram
            if (mod.maxBinShift[i] == numberOfBins/2+1):
                mod.maxBinShift[i] = 0
            # set the maxShift value
            mod.maxShift[i] = mod.histo[i].GetBinCenter( numberOfBins/2+mod.maxBinShift[i] )

        # find and apply the new range
        for i in range(3):
            if (mod.histo[i].GetEntries() != 0 and mod.histo[i].GetStdDev() != 0):
                # if the plotrange is much bigger than the standard deviation use 3 * StdDev als Range
                if ( max(mod.maxShift)/mod.histo[i].GetStdDev() > 9 ):
                    # corresponding bin 3*StdDev
                    binShift = int(mod.histo[i].FindBin(3*mod.histo[i].GetStdDev()) - numberOfBins/2)
                    # count entries which are not shown anymore
                    # bin 1 to begin of histogram
                    for j in range(1, numberOfBins/2 - binShift):
                        mod.hiddenEntries[i] += mod.histo[i].GetBinContent(j)
                    # from the end of shown bins to the end of histogram
                    for j in range(numberOfBins/2 + binShift, mod.histo[i].GetNbinsX()):
                        mod.hiddenEntries[i] += mod.histo[i].GetBinContent(j)
                else:
                    binShift = max(mod.maxBinShift)
                
                # save used binShift
                mod.binShift[i] = binShift
                
                # merge bins, ca. 100 should be visible in the resulting plot
                mergeNumberBins = binShift
                # skip empty histogram
                if (mergeNumberBins != 0):
                    # the 2*maxBinShift bins should shrink to 100 bins
                    mergeNumberBins = int(2*mergeNumberBins/100.)
                    # the total number of bins should be dividable by the bins shrinked together
                    if (mergeNumberBins == 0):
                        mergeNumberBins = 1
                    while (numberOfBins%mergeNumberBins != 0 and mergeNumberBins != 1):
                        mergeNumberBins -= 1
                    
                    # Rebin and save new created histogram and axis
                    mod.histo[i] = mod.histo[i].Rebin( mergeNumberBins )
                    mod.histoAxis[i] = mod.histo[i].GetXaxis()
                    
                    # set view range. it is important to note that the number of bins have changed with the rebinning
                    # the total number and the number of shift must be corrected with / mergeNumberBins
                    mod.histoAxis[i].SetRange(int(numberOfBins/(2*mergeNumberBins)-binShift / mergeNumberBins), int(numberOfBins/(2*mergeNumberBins)+binShift / mergeNumberBins))
            
               
        # TODO chose good limit
        # error if shift is bigger than limit
        limit = 0.02
        for i in range(3):
            text.AddText("max. shift {0}: {1:.2}".format(mod.xyz[i], mod.maxShift[i]))
            if (mod.maxShift[i] > limit):
                text.AddText("! {0} shift bigger than {1} !".format(mod.xyz[i], limit))
            if (mod.hiddenEntries[i] != 0):
                text.AddText("! {0} entries not shown !".format(int(mod.hiddenEntries[i])))
        
        
                        
        # show the skewness in the legend
        gStyle.SetOptStat("nemrs")
        
        cMod[bStructNumber].cd(1)
        title.Draw()
        text.Draw()
        cMod[bStructNumber].cd(2)
        mod.histo[0].DrawCopy()
        cMod[bStructNumber].cd(3)
        mod.histo[1].DrawCopy()
        cMod[bStructNumber].cd(4)
        mod.histo[2].DrawCopy()
        cMod[bStructNumber].Update()
        raw_input("..")
        
        # export as png
        image.FromPad(cMod[bStructNumber])
        image.WriteImage("{0}/plots/Mod_{1}.png".format(outputPath, bStruct.getName()))
        
        
        ######################################################################################
        # module subStruct
        
        cModSub = []
        
        print bStruct.getChildren()
        
        # loop over subStructs
        for subStructNumber, subStruct in enumerate(bStruct.getChildren()):
            cModSub.append(TCanvas("canvasSubStruct{0}".format(subStruct.getName()), "Parameter", 300, 0, 800, 600))
            cModSub[subStructNumber].Divide(2, 2)
            
            modSub = TreeData()
            
            # initialize histograms
            for i in range(3):
                modSub.histo.append(TH1F("{0} {1}".format(subStruct.getName(), modSub.xyz[i]), "Parameter {0}".format(modSub.xyz[i]), numberOfBins, -0.1, 0.1))
                modSub.histo[i].SetXTitle("[cm]")
                modSub.histoAxis.append(modSub.histo[i].GetXaxis())
                modSub.histo[i].SetLineColor(6)
            
            # add labels
            titleSub = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0}".format(subStruct.getName()))
            textSub = TPaveText(0.05, 0.1, 0.95, 0.75)
            textSub.SetTextAlign(13)
            textSub.SetTextSizePixels(20)
            
            # fill histogram
            for line in MillePedeUser:
                if (line.ObjId == 1 and subStruct.containLabel(line.Label)):
                    for i in range(3):
                        if (abs(line.Par[i]) != 999999): 
                            modSub.histo[i].Fill(line.Par[i])
            
            # find and apply the new range
            for i in range(3):
                if (modSub.histo[i].GetEntries() != 0 and modSub.histo[i].GetStdDev() != 0):
                    # use binShift of the hole structure
                    binShift = mod.binShift[i]
                    
                    # merge bins, ca. 100 should be visible in the resulting plot
                    mergeNumberBins = binShift
                    # skip empty histogram
                    if (mergeNumberBins != 0):
                        # the 2*maxBinShift bins should shrink to 100 bins
                        mergeNumberBins = int(2*mergeNumberBins/100.)
                        # the total number of bins should be dividable by the bins shrinked together
                        if (mergeNumberBins == 0):
                            mergeNumberBins = 1
                        while (numberOfBins%mergeNumberBins != 0 and mergeNumberBins != 1):
                            mergeNumberBins -= 1
                        
                        # Rebin and save new created histogram and axis
                        modSub.histo[i] = modSub.histo[i].Rebin( mergeNumberBins )
                        modSub.histoAxis[i] = modSub.histo[i].GetXaxis()
                        
                        # set view range. it is important to note that the number of bins have changed with the rebinning
                        # the total number and the number of shift must be corrected with / mergeNumberBins
                        modSub.histoAxis[i].SetRange(int(numberOfBins/(2*mergeNumberBins)-binShift / mergeNumberBins), int(numberOfBins/(2*mergeNumberBins)+binShift / mergeNumberBins))
            
            # draw subStruct modules and the hole struct
            cModSub[subStructNumber].cd(1)
            titleSub.Draw()
            textSub.Draw()
            cModSub[subStructNumber].cd(2)
            modSub.histo[0].DrawCopy()
            mod.histo[0].DrawCopy("same")
            cModSub[subStructNumber].cd(3)
            modSub.histo[1].DrawCopy()
            mod.histo[1].DrawCopy("same")
            cModSub[subStructNumber].cd(4)
            modSub.histo[2].DrawCopy()
            mod.histo[2].DrawCopy("same")
            cModSub[subStructNumber].Update()
            raw_input("stop")
            
            
                
                
    
    raw_input("wait...")
    

    
if __name__ == "__main__":
    main()
