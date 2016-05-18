#!/usr/bin/env python
from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel
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
    
    
    geometrygetter = GeometryGetter()
    
    # TODO get latest Alignment directory
    alignmentNumber = 3
    
    # TODO which time MillePedeUser_X
    alignmentTime = 1
    
    
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
    hBigX = TH1F("Big Structure X", "Parameter X", 100, -0.005, 0.005)
    hBigY = TH1F("Big Structure Y", "Parameter Y", 100, -0.005, 0.005)
    hBigZ = TH1F("Big Structure Z", "Parameter Z", 100, -0.005, 0.005)
    hBigX.SetXTitle("[cm]")
    hBigY.SetXTitle("[cm]")
    hBigZ.SetXTitle("[cm]")
    
    title = TPaveLabel(0.1,0.2,0.3,0.4, "Big Structures")
    
    for line in MillePedeUser:
        if (line.ObjId != 1):
            hBigX.Fill(line.Par[0])
            hBigY.Fill(line.Par[1])
            hBigZ.Fill(line.Par[2])
    
    cBigXYZ.cd(1)
    title.Draw()
    cBigXYZ.cd(2)
    hBigX.Draw()
    cBigXYZ.cd(3)
    hBigY.Draw()
    cBigXYZ.cd(4)
    hBigZ.Draw()
    cBigXYZ.Update()
    
    imageBig = TImage.Create()
    imageBig.FromPad(cBigXYZ)
    imageBig.WriteImage("BigXYZ.png")
    
    input("wait...")
    
    """
    try:
        for element in MillePedeUser1:
            print "Id: {0} ({1})".format(element.Id, geometrygetter.name_by_objid(element.ObjId))
    except Exception as e:
        logging.critical("Error: {}".format(e))
        raise
    """    
    

    
if __name__ == "__main__":
    main()
