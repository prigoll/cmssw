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
    
    boundaries_bStruct = [61, 17541, 37021, 121061, 144401, 284201, 700000]
    name_bStruct = ["TrackerTPBHalfBarrel", "TrackerTPEHalfDisk", "TrackerTIBHalfBarrel", "TrackerTIDEndcap", "TrackerTOBHalfBarrel", "TrackerTECEndcap", "newIOV"]
    
    def __init__(self):
        pass
        
    def name_by_objid(self, objid):
        return self.objid_names[objid]
    
    # check if label is in the range of the structlabels specified by number_bStruct
    def label_in_bStruct(self, label, number_bStruct):
        # check if it is the last structure
        if (number_bStruct < len(self.boundaries_bStruct)):
            # check if label is between boundaries
            if (label > self.boundaries_bStruct[number_bStruct] and label < self.boundaries_bStruct[number_bStruct+1]):
                return True
        elif (label > self.boundaries_bStruct[number_bStruct]):
            return True
    
    
    
class TreeData:
    """ Hold information about XYZ
    """
    
    xyz = {0: "X", 1: "Y", 2: "Z"}
    
    def __init__(self):
        self.numberOfBins = [0, 0, 0]
        self.maxShift = [0, 0, 0]
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
        big.histo[i].SetFillColor(42)
        
    
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
    big.histo[0].Draw("hbarP")
    cBig.cd(3)
    big.histo[1].Draw("hbarp")
    cBig.cd(4)
    big.histo[2].Draw("hbarL")
    cBig.Update()
    
    # export as png
    image = TImage.Create()
    image.FromPad(cBig)
    image.WriteImage("{0}/plots/Big.png".format(outputPath))
    
    # reset BottomMargin
    gStyle.SetPadBottomMargin(0.1)
    raw_input("wait..")
    
    # modules
    
    cMod = []
    
    # loop over all structures
    for number_bStruct, name_bStruct in enumerate(geometryGetter.name_bStruct):
        cMod.append(TCanvas("canvasModules{0}".format(name_bStruct), "Parameter", 300, 0, 800, 600))
        cMod[number_bStruct].Divide(2,2)
        
        mod = TreeData()
        
        # get max shift
        for line in MillePedeUser:
            if (line.ObjId == 1 and geometryGetter.label_in_bStruct(line.Label, number_bStruct)):
                for i in range(3):
                    if (abs(line.Par[i]) != 999999 and abs(line.Par[i]) > mod.maxShift[i]):
                        mod.maxShift[i] = line.Par[i]
        
        # round max shift
        for i in range(3):
            mod.maxShift[i] = round(mod.maxShift[i],3) + 0.001
                        
        # initialize histograms
        for i in range(3):
            mod.histo.append(TH1F("Module {0}".format(mod.xyz[i]), "Parameter {0}".format(mod.xyz[i]), 100, -max(mod.maxShift), max(mod.maxShift)))
            mod.histo[i].SetXTitle("[cm]")
            
        # show the skewness in the legend
        gStyle.SetOptStat("nemrs")

        
        # add labels
        title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0}".format(name_bStruct))
        text = TPaveText(0.05, 0.1, 0.95, 0.75)
        text.SetTextAlign(13)
        text.SetTextSizePixels(20)
        
        # TODO chose good limit
        # error if shift is bigger than limit
        limit = 0.02
        for i in range(3):
            text.AddText("max. shift {0}: {1:.2}".format(mod.xyz[i], mod.maxShift[i]))
            if (mod.maxShift[i] > limit):
                text.AddText("! {0} shift bigger than {1} !".format(mod.xyz[i], limit))
        

        for line in MillePedeUser:
            if (line.ObjId == 1 and geometryGetter.label_in_bStruct(line.Label, number_bStruct)):
                for i in range(3):
                    if (abs(line.Par[i]) != 999999): 
                        mod.histo[i].Fill(line.Par[i])
                
        
        cMod[number_bStruct].cd(1)
        title.Draw()
        text.Draw()
        cMod[number_bStruct].cd(2)
        mod.histo[0].Draw()
        cMod[number_bStruct].cd(3)
        mod.histo[1].Draw()
        cMod[number_bStruct].cd(4)
        mod.histo[2].Draw()
        cMod[number_bStruct].Update()
        
        # export as png
        image.FromPad(cMod[number_bStruct])
        image.WriteImage("{0}/plots/Mod_{1}.png".format(outputPath, name_bStruct))
    
    raw_input("wait...")
    

    
if __name__ == "__main__":
    main()
