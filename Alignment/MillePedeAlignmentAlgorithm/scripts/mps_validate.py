#!/usr/bin/env python
from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText
import argparse
import logging

class GeometryGetter:
    """ Getting human readable names of detector parts
    """
    
    obj_id_names = {-1: "notfound", 0: "invalid", 1: "AlignableDetUnit", 2: "AlignableDet", 3: "TPBModule", 4: "TPBLadder", 5: "TPBLayer", 6: "TPBHalfBarrel", 7: "TPBBarrel", 8: "TPEModule", 9: "TPEPanel", 10: "TPEBlade", 11: "TPEHalfDisk", 12: "TPEHalfCylinder", 13: "TPEEndcap", 14: "TIBModule", 15: "TIBString", 16: "TIBSurface", 17: "TIBHalfShell", 18: "TIBLayer", 19: "TIBHalfBarrel", 20: "TIBBarrel", 21: "TIDModule", 22: "TIDSide", 23: "TIDRing", 24: "TIDDisk", 25: "TIDEndcap", 26: "TOBModule", 27: "TOBRod", 28: "TOBLayer", 29: "TOBHalfBarrel", 30: "TOBBarrel", 31: "TECModule", 32: "TECRing", 33: "TECPetal", 34: "TECSide", 35: "TECDisk", 36: "TECEndcap", 37: "Pixel", 38: "Strip", 39: "Tracker", 100: "AlignableDTBarrel", 101: "AlignableDTWheel", 102: "AlignableDTStation", 103: "AlignableDTChamber", 104: "AlignableDTSuperLayer", 105: "AlignableDTLayer", 106: "AlignableCSCEndcap", 107: "AlignableCSCStation", 108: "AlignableCSCRing", 109: "AlignableCSCChamber", 110: "AlignableCSCLayer", 111: "AlignableMuon", 112: "Detector", 1000: "Extras", 1001: "BeamSpot"}
    
    def __init__(self):
        pass
        
    def name_by_objid(self, id):
        return self.obj_id_names[id]


def main():
    # config logging module
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                       datefmt="%d.%m.%Y %H:%M:%S")
    
    
    geometryGetter = GeometryGetter()
    
    # ArgumentParser
    parser = argparse.ArgumentParser(description="Validate your Aligment.")
    parser.add_argument("-j", "--job", help="chose jobmX directory (default: 0)", default=0, type=int)
    parser.add_argument("-t", "--time", help="chose MillePedeUser_X Tree (default: 1)", default=1, type=int)
    args = parser.parse_args()
    
    # TODO get latest Alignment directory
    #alignmentNumber = args.job
    alignmentNumber = 3
    
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
    
    cBigXYZ = TCanvas("canvasBigStrucutres", "Parameter", 300, 0, 800, 600)
    cBigXYZ.Divide(2,2)
    
    # TODO dynamic range, error
    # count number of needed bins
    numberOfBins = 0
    for line in MillePedeUser:
        if (line.ObjId != 1):
            numberOfBins += 1
    
    # initate histograms
    hBigX = TH1F("Big Structure X", "Parameter X", numberOfBins, 0, numberOfBins)
    hBigY = TH1F("Big Structure Y", "Parameter Y", numberOfBins, 0, numberOfBins)
    hBigZ = TH1F("Big Structure Z", "Parameter Z", numberOfBins, 0, numberOfBins)
    hBigX.SetYTitle("[cm]")
    hBigY.SetYTitle("[cm]")
    hBigZ.SetYTitle("[cm]")
    hBigX.SetStats(0)
    hBigY.SetStats(0)
    hBigZ.SetStats(0)
    axisBigX = hBigX.GetXaxis()
    axisBigY = hBigY.GetXaxis()
    axisBigZ = hBigZ.GetXaxis()
    
    # add labels
    title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Big Structures")
    text = TPaveText(0.05, 0.1, 0.95, 0.75)
    text.SetTextAlign(13)
    text.SetTextSizePixels(22)
    
    # fill histograms with value and name
    binPosition = 1
    for line in MillePedeUser:
        if (line.ObjId != 1):
            axisBigX.SetBinLabel(binPosition, geometryGetter.name_by_objid(line.ObjId))
            axisBigY.SetBinLabel(binPosition, geometryGetter.name_by_objid(line.ObjId))
            axisBigZ.SetBinLabel(binPosition, geometryGetter.name_by_objid(line.ObjId))
            hBigX.SetBinContent(binPosition, line.Par[0])
            hBigY.SetBinContent(binPosition, line.Par[1])
            hBigZ.SetBinContent(binPosition, line.Par[2])
            binPosition += 1
    
    # find maximum shift
    maximumX = max([ abs(hBigX.GetMaximum()), abs(hBigX.GetMinimum()) ])
    maximumY = max([ abs(hBigY.GetMaximum()), abs(hBigY.GetMinimum()) ])
    maximumZ = max([ abs(hBigZ.GetMaximum()), abs(hBigZ.GetMinimum()) ])
    text.AddText("max. shift X: {0:.2}".format(maximumX))
    text.AddText("max. shift Y: {0:.2}".format(maximumY))
    text.AddText("max. shift Z: {0:.2}".format(maximumZ))
    
    # TODO chose good limit
    # error if shift is bigger than limit
    limit = 0.02
    if (max([maximumX, maximumY,maximumZ]) > limit):
        text.AddText("! shift bigger than {0} !".format(limit))
    
    cBigXYZ.cd(1)
    title.Draw()
    text.Draw()
    cBigXYZ.cd(2)
    hBigX.Draw()
    cBigXYZ.cd(3)
    hBigY.Draw()
    cBigXYZ.cd(4)
    hBigZ.Draw()
    cBigXYZ.Update()
    
    # export as png
    imageBig = TImage.Create()
    imageBig.FromPad(cBigXYZ)
    imageBig.WriteImage("BigXYZ.png")
    
    
    # modules
    
    cMod = TCanvas("canvasModules", "Parameter", 300, 0, 800, 600)
    cMod.Divide(2,2)
    
    # TODO what modules should be counted
    # find maximum shift
    maximum = 0
    for line in MillePedeUser:
        if (line.ObjId == 1 and abs(line.Par[0]) != 999999 and abs(line.Par[1]) != 999999 and abs(line.Par[2]) != 999999):
            linemax = max([abs(line.Par[0]), abs(line.Par[1]), abs(line.Par[2])])
            if (linemax > maximum):
                maximum = linemax
    print "Maximum: {0}".format(maximum)
    maximum = round(maximum, 3) + 0.01
    print "Maximum: {0}".format(maximum)
    
    
    hModX = TH1F("Module X", "Parameter X", 100, -maximum, maximum)
    hModY = TH1F("Module Y", "Parameter Y", 100, -maximum, maximum)
    hModZ = TH1F("Module Z", "Parameter Z", 100, -0.005, 0.005)
    hModX.SetXTitle("[cm]")
    hModY.SetXTitle("[cm]")
    hModZ.SetXTitle("[cm]")
    axisModX = hModX.GetXaxis()
    axisModY = hModY.GetXaxis()
    axisModZ = hModZ.GetXaxis()
    
    for line in MillePedeUser:
        if (line.ObjId == 1):
            hModX.Fill(line.Par[0])
            hModY.Fill(line.Par[0])
            hModZ.Fill(line.Par[0])
            
    cMod.cd(2)
    hModX.Draw()
    cMod.cd(3)
    hModY.Draw()
    cMod.cd(4)
    hModZ.Draw()
    cMod.Update()
    
    input("wait...")
    

    
if __name__ == "__main__":
    main()
