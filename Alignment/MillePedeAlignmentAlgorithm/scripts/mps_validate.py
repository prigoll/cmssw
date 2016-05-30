#!/usr/bin/env python

##########################################################################
##  Create histograms out of treeFile_merge.root . The pede.dump.gz file is
##  paresed. The histograms are plotted as PNG files. The output data is
##  created as PDF, HTML, ...
##

from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData
from mpsvalidate.dumpparser import parse
from mpsvalidate.iniparser import ConfigData
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
    parser = argparse.ArgumentParser(description="Validate your Alignment.")
    # TODO set default -> 0
    parser.add_argument("-j", "--job", help="chose jobmX directory (default: ini-file)", default=-1, type=int)
    parser.add_argument("-t", "--time", help="chose MillePedeUser_X Tree (default: ini-file)", default=-1, type=int)
    parser.add_argument("-i", "--ini", help="specify a ini file", default="-1")
    args = parser.parse_args()
    
    # create config object
    config = ConfigData()
    
    # parse default ini file
    config.parseConfig("./mpsvalidate/default.ini")
    
    # parse user ini file
    if (args.ini != "-1"):
        config.parseConfig(args.ini)
    
    # override ini configs with consol parameter
    config.parseParameter(args)
    
    ## create output directories
    if not os.path.exists("{0}/plots".format(config.outputPath)):
        os.makedirs("{0}/plots".format(config.outputPath))
    
    # parse the file pede.dump.gz and return a LogData Object
    pedeDump = parse("{0}/pede.dump.gz".format(config.jobDataPath), config)
    
    # pedeDump.printLog()
    
    # TODO check if there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    treeFile = TFile("{0}/treeFile_merge.root".format(config.jobDataPath))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(config.jobTime))
    
    
    ##########################################################################
    # big structures
    #
    
    # create the histogram data
    big = bigStructure.plot(MillePedeUser, geometryGetter, config)
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
    image.WriteImage("{0}/plots/Big.png".format(config.outputPath))

    
    ##########################################################################
    # modules of a hole structure
    #
    
    # create histogram data in a list
    mod = bigModule.plot(MillePedeUser, geometryGetter, config)
                    
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
        image.WriteImage("{0}/plots/Mod_{1}.png".format(config.outputPath, struct.getName()))
        
        
    ##########################################################################
    # modules of a part of a strucutre, together with the hole strucutre
    #
    
    # create histograms
    subMod = subModule.plot(MillePedeUser, geometryGetter, mod, config)
    
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
            image.WriteImage("{0}/plots/Mod_{1}_{2}.png".format(config.outputPath, bStruct.getName(), subStructNumber))
            
    
if __name__ == "__main__":
    main()
