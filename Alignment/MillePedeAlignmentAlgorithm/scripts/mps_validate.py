#!/usr/bin/env python

##########################################################################
##  Create histograms out of treeFile_merge.root . The pede.dump.gz file is
##  paresed. The histograms are plotted as PNG files. The output data is
##  created as PDF, HTML, ...
##

from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData
from mpsvalidate.dumpparser import parse
from mpsvalidate import bigStructure, bigModule, subModule

import argparse
import logging
import os

def main():
    # config logging module
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                       datefmt="%d.%m.%Y %H:%M:%S")
    
    # run ROOT in batchmode
    gROOT.SetBatch()
    # create GeometryGetter object
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
    
    # parse the file pede.dump.gz and return a LogData Object
    pedeDump = parse("{0}/pede.dump.gz".format(jobDataPath))
    
    # pedeDump.printLog()
    
    # TODO check if there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    treeFile = TFile("{0}/treeFile_merge.root".format(jobDataPath))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(alignmentTime))
    
    
    ##########################################################################
    # big structures
    #
    
    # create the histogram data
    big = bigStructure.plot(MillePedeUser, geometryGetter)
    # more space for labels
    gStyle.SetPadBottomMargin(0.25)
    
    # create canvas
    cBig = TCanvas("canvasBigStrucutres", "Parameter", 300, 0, 800, 600)
    cBig.Divide(2,2)
    
    # draw histograms
    cBig.cd(1)
    big.title.Draw()
    big.text.Draw()
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

    
    ##########################################################################
    # modules of a hole structure
    #
    
    # create histogram data in a list
    mod = bigModule.plot(MillePedeUser, geometryGetter)
                    
    # show the skewness in the legend
    gStyle.SetOptStat("nemrs")
    
    # draw plots
    cMod = []
    # loop over all structures to get the name
    for structNumber, struct in enumerate(geometryGetter.listbStructs()):
        cMod.append(TCanvas("canvasModules{0}".format(struct.getName()), "Parameter", 300, 0, 800, 600))
        cMod[structNumber].Divide(2, 2)
        
        # the loop and the data in cMod are in the same order
        cMod[structNumber].cd(1)
        mod[structNumber].title.Draw()
        mod[structNumber].text.Draw()
        
        cMod[structNumber].cd(2)
        mod[structNumber].histo[0].DrawCopy()
        
        cMod[structNumber].cd(3)
        mod[structNumber].histo[1].DrawCopy()
        
        cMod[structNumber].cd(4)
        mod[structNumber].histo[2].DrawCopy()
        
        cMod[structNumber].Update()
    
        # export as png
        image.FromPad(cMod[structNumber])
        image.WriteImage("{0}/plots/Mod_{1}.png".format(outputPath, struct.getName()))
        
        
    ##########################################################################
    # modules of a part of a strucutre, together with the hole strucutre
    #
    
    # create histograms
    subMod = subModule.plot(MillePedeUser, geometryGetter, mod)
    
    # draw plots with nested lists
    cModSub = []
    
    # loop over all structures    
    for bStructNumber, bStruct in enumerate(geometryGetter.listbStructs()):
        # append nested list with parts of the structure
        cModSub.append([])
        # loop over the parts of a structure
        for subStructNumber, subStruct in enumerate(bStruct.getChildren()):
            cModSub[bStructNumber].append(TCanvas("canvasSubStruct{0}".format(subStruct.getName()), "Parameter", 300, 0, 800, 600))
            cModSub[bStructNumber][subStructNumber].Divide(2, 2)
            
            # draw parts of the strucutre and the hole structure
            cModSub[bStructNumber][subStructNumber].cd(1)
            subMod[bStructNumber][subStructNumber].title.Draw()
            subMod[bStructNumber][subStructNumber].text.Draw()
            
            # check if histogram is not emtpy
            if (subMod[bStructNumber][subStructNumber].histo[0].GetEntries() > 0):
                cModSub[bStructNumber][subStructNumber].cd(2)
                subMod[bStructNumber][subStructNumber].histo[0].DrawNormalized()
                mod[bStructNumber].histo[0].DrawNormalized("same")
            
            if (subMod[bStructNumber][subStructNumber].histo[1].GetEntries() > 0):
                cModSub[bStructNumber][subStructNumber].cd(3)
                subMod[bStructNumber][subStructNumber].histo[1].DrawNormalized()
                mod[bStructNumber].histo[1].DrawNormalized("same")
            
            if (subMod[bStructNumber][subStructNumber].histo[2].GetEntries() > 0):
                cModSub[bStructNumber][subStructNumber].cd(4)
                subMod[bStructNumber][subStructNumber].histo[2].DrawNormalized()
                mod[bStructNumber].histo[2].DrawNormalized("same")
            
            cModSub[bStructNumber][subStructNumber].Update()

            # export as png
            image.FromPad(cModSub[bStructNumber][subStructNumber])
            image.WriteImage("{0}/plots/Mod_{1}_{2}.png".format(outputPath, bStruct.getName(), subStructNumber))
            
    
if __name__ == "__main__":
    main()
