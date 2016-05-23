#!/usr/bin/env python
from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText
import argparse
import logging

class GeometryGetter:
    """ Getting human readable names of detector parts
    """
    
    objid_names = {-1: "notfound", 0: "invalid", 1: "AlignableDetUnit", 2: "AlignableDet", 3: "TPBModule", 4: "TPBLadder", 5: "TPBLayer", 6: "TPBHalfBarrel", 7: "TPBBarrel", 8: "TPEModule", 9: "TPEPanel", 10: "TPEBlade", 11: "TPEHalfDisk", 12: "TPEHalfCylinder", 13: "TPEEndcap", 14: "TIBModule", 15: "TIBString", 16: "TIBSurface", 17: "TIBHalfShell", 18: "TIBLayer", 19: "TIBHalfBarrel", 20: "TIBBarrel", 21: "TIDModule", 22: "TIDSide", 23: "TIDRing", 24: "TIDDisk", 25: "TIDEndcap", 26: "TOBModule", 27: "TOBRod", 28: "TOBLayer", 29: "TOBHalfBarrel", 30: "TOBBarrel", 31: "TECModule", 32: "TECRing", 33: "TECPetal", 34: "TECSide", 35: "TECDisk", 36: "TECEndcap", 37: "Pixel", 38: "Strip", 39: "Tracker", 100: "AlignableDTBarrel", 101: "AlignableDTWheel", 102: "AlignableDTStation", 103: "AlignableDTChamber", 104: "AlignableDTSuperLayer", 105: "AlignableDTLayer", 106: "AlignableCSCEndcap", 107: "AlignableCSCStation", 108: "AlignableCSCRing", 109: "AlignableCSCChamber", 110: "AlignableCSCLayer", 111: "AlignableMuon", 112: "Detector", 1000: "Extras", 1001: "BeamSpot"}
    
    boundaries_bStruct = [61, 17541, 37021, 121061, 144401, 284201, 700000]
    name_bStruct = ["TrackerTPBHalfBarrel", "TrackerTPEHalfDisk", "TrackerTIBHalfBarrel", "TrackerTIDEndcap", "TrackerTOBHalfBarrel", "TrackerTECEndcap", "newIOV"]
    
    def __init__(self):
        pass
        
    def name_by_objid(self, objid):
        return self.objid_names[objid]
    
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
    
    
    # TODO check of there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    if (alignmentNumber == 0):
        treeFile = TFile("./jobData/jobm/treeFile_merge.root")
    else:
        treeFile = TFile("./jobData/jobm{0}/treeFile_merge.root".format(alignmentNumber))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(alignmentTime))
    
    
    # big structures
    
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
        big.histoAxis.append(big.histo[i].GetXaxis())
    
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
    big.histo[0].Draw()
    cBig.cd(3)
    big.histo[1].Draw()
    cBig.cd(4)
    big.histo[2].Draw()
    cBig.Update()
    
    # export as png
    image = TImage.Create()
    image.FromPad(cBig)
    image.WriteImage("Big.png")
    
    
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
            mod.histo.append(TH1F("Module {0}".format(mod.xyz[i]), "Parameter {0}".format(mod.xyz[i]), 100, -mod.maxShift[i], mod.maxShift[i]))
            mod.histo[i].SetXTitle("[cm]")                    
        
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
        image.WriteImage("Mod_{0}.png".format(name_bStruct))
    
    input("wait...")
    

    
if __name__ == "__main__":
    main()
