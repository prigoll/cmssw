#!/usr/bin/env python

##########################################################################
##  Create histograms out of treeFile_merge.root . The pede.dump.gz file is
##  paresed. The histograms are plotted as PNG files. The output data is
##  created as PDF, HTML, ...
##

from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText, gStyle, gROOT, TLegend
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData, OutputData
from mpsvalidate.dumpparser import parse
from mpsvalidate.iniparser import ConfigData
from mpsvalidate import bigStructure, bigModule, subModule, pdfCreator, beamerCreator, timeStructure

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
    if not os.path.exists("{0}/plots/pdf".format(config.outputPath)):
        os.makedirs("{0}/plots/pdf".format(config.outputPath))
    if not os.path.exists("{0}/plots/png".format(config.outputPath)):
        os.makedirs("{0}/plots/png".format(config.outputPath))
        
    # parse the file pede.dump.gz and return a LogData Object
    pedeDump = parse("{0}/pede.dump.gz".format(config.jobDataPath), config)
    
    # TODO check if there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    treeFile = TFile("{0}/treeFile_merge.root".format(config.jobDataPath))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(config.jobTime))
    
    
    ##########################################################################
    # time dependend big structures
    #
    
    # list of all avaible TTrees
    listMillePedeUser = []
    # TODO use Ttrees in ini file
    for i in range(1, 31):
        if (treeFile.GetListOfKeys().Contains("MillePedeUser_{0}".format(i))):
            listMillePedeUser.append(i)
    
    for mode in ["xyz", "rot"]:
        # create the histogram data
        bigX = []
        legend = TLegend(0.05, 0.1, 0.95, 0.75)
        maximum = [0, 0, 0]
        minimum = [0, 0, 0]
        
        # loop over MillePedeUser_X TTrees
        # note that bigX data is stored in a list
        for jobTime, jobTimeName in enumerate(listMillePedeUser):
            MillePedeUser_X = treeFile.Get("MillePedeUser_{0}".format(jobTimeName))
            bigX.append(timeStructure.plot(MillePedeUser_X, geometryGetter, "rot", config, jobTimeName))
            # get maximum in each coordinate
            for i in range(3):
                if (bigX[jobTime].maxShift[i] > maximum[i]):
                    maximum[i] = bigX[jobTime].maxShift[i]
                if (bigX[jobTime].minShift[i] < minimum[i]):
                    minimum[i] = bigX[jobTime].minShift[i]
        
        # more space for labels
        gStyle.SetPadBottomMargin(0.25)
        
        # create canvas
        cBig = TCanvas("canvasTimeBigStrucutres_{0}".format(mode), "Parameter", 300, 0, 800, 600)
        cBig.Divide(2,2)
        
        # draw histograms
        cBig.cd(1)
        bigX[0].title.Draw()
        
        # loop over coordinates
        for i in range(3):
            cBig.cd(i+2)
            
            # set minimum and maximum of first plot
            bigX[0].histo[i].SetMaximum(1.05*maximum[i])
            bigX[0].histo[i].SetMinimum(1.05*minimum[i])
            
            # loop over MillePedeUser_X TTree data
            # note that bigX data is stored in a list
            for jobTime, jobTimeName in enumerate(listMillePedeUser):
                # chose different color for every TTree
                bigX[jobTime].histo[i].SetMarkerColor(jobTime+1)
                # option "p" to use marker
                bigX[jobTime].histo[i].Draw("pSame")
                
                # only AddEntry to legend in the first coordinate
                if (i==0):
                    legend.AddEntry(bigX[jobTime].histo[i], "{0}".format(jobTimeName), "p")
        
        cBig.cd(1)
        legend.Draw()
        
        cBig.Update()
        
        # save as pdf
        cBig.Print("{0}/plots/pdf/timeStructures_{1}.pdf".format(config.outputPath, mode))
        
        # export as png
        image = TImage.Create()
        image.FromPad(cBig)
        image.WriteImage("{0}/plots/png/timeStructures_{1}.png".format(config.outputPath, mode))
        
        # add to output list
        output = OutputData(plottype="time", parameter=mode, filename="timeStructures_{0}".format(mode))
        config.outputList.append(output)
    
    
    ##########################################################################
    # big structures
    #
    
    for mode in ["xyz", "rot"]:
        # create the histogram data
        big = bigStructure.plot(MillePedeUser, geometryGetter, mode, config)
        # more space for labels
        gStyle.SetPadBottomMargin(0.25)
        
        # create canvas
        cBig = TCanvas("canvasBigStrucutres_{0}".format(mode), "Parameter", 300, 0, 800, 600)
        cBig.Divide(2,2)
        
        # draw histograms
        cBig.cd(1)
        big.title.Draw()
        big.text.Draw()
        
        # loop over coordinates
        for i in range(3):
            cBig.cd(i+2)
            # option "p" to use marker
            big.histo[i].Draw("p")
        
        cBig.Update()
        
        # save as pdf
        cBig.Print("{0}/plots/pdf/structures_{1}.pdf".format(config.outputPath, mode))
        
        # export as png
        image = TImage.Create()
        image.FromPad(cBig)
        image.WriteImage("{0}/plots/png/structures_{1}.png".format(config.outputPath, mode))
        
        # add to output list
        output = OutputData(plottype="big", parameter=mode, filename="structures_{0}".format(mode))
        config.outputList.append(output)

    
    ##########################################################################
    # modules of a hole structure
    #
    
    # store TreeData for different modes
    mod = []
    # store Canvas for different modes
    cMod = []
    
    for modeNumber, mode in enumerate(["xyz", "rot", "dist"]):
        # create histogram data in a list
        mod.append(bigModule.plot(MillePedeUser, geometryGetter, mode, config))
                        
        # show the skewness in the legend
        gStyle.SetOptStat("nemrs")
        
        # draw plots
        cMod.append([])
        # loop over all structures to get the name
        for structNumber, struct in enumerate(geometryGetter.listbStructs()):
            cMod[modeNumber].append(TCanvas("canvasModules{0}_{1}".format(struct.getName(), mode), "Parameter", 300, 0, 800, 600))
            cMod[modeNumber][structNumber].Divide(2, 2)
            
            # the loop and the data in cMod are in the same order
            cMod[modeNumber][structNumber].cd(1)
            mod[modeNumber][structNumber].title.Draw()
            mod[modeNumber][structNumber].text.Draw()
            
            # is there any plot?
            plotNumber = 0
            
            # loop over coordinates
            for i in range(3):
                if(mod[modeNumber][structNumber].histo[i].GetEntries() > 0):
                    plotNumber += 1
                    cMod[modeNumber][structNumber].cd(i+2)
                    mod[modeNumber][structNumber].histo[i].DrawCopy()
                
            if (plotNumber == 0):
                break
            
            cMod[modeNumber][structNumber].Update()
            
            # save as pdf
            cMod[modeNumber][structNumber].Print("{0}/plots/pdf/modules_{1}_{2}.pdf".format(config.outputPath, mode, struct.getName()))
        
            # export as png
            image.FromPad(cMod[modeNumber][structNumber])
            image.WriteImage("{0}/plots/png/modules_{1}_{2}.png".format(config.outputPath, mode, struct.getName()))
            
            # add to output list
            output = OutputData(plottype="mod", name=struct.getName(), parameter=mode, filename="modules_{0}_{1}".format(mode, struct.getName()))
            config.outputList.append(output)
        
        
    ##########################################################################
    # modules of a part of a strucutre, together with the hole strucutre
    #
    
    # store TreeData for different modes
    subMod = []
    # store Canvas for different modes
    cModSub = []
    
    for modeNumber, mode in enumerate(["xyz", "rot", "dist"]):
        # create histograms
        subMod.append(subModule.plot(MillePedeUser, geometryGetter, mod, mode, config))
        
        # draw plots with nested lists
        cModSub.append([])
        
        # loop over all structures    
        for bStructNumber, bStruct in enumerate(geometryGetter.listbStructs()):
            # append nested list with parts of the structure
            cModSub[modeNumber].append([])
            
            # loop over the parts of a structure
            for subStructNumber, subStruct in enumerate(bStruct.getChildren()):
                cModSub[modeNumber][bStructNumber].append(TCanvas("canvasSubStruct{0}_{1}".format(subStruct.getName(), mode), "Parameter", 300, 0, 800, 600))
                cModSub[modeNumber][bStructNumber][subStructNumber].Divide(2, 2)
                
                # draw parts of the strucutre and the hole structure
                cModSub[modeNumber][bStructNumber][subStructNumber].cd(1)
                subMod[modeNumber][bStructNumber][subStructNumber].title.Draw()
                subMod[modeNumber][bStructNumber][subStructNumber].text.Draw()
                
                # is there any plot?
                plotNumber = 0
                
                # loop over coordinates
                for i in range(3):
                    # check if histogram is not emtpy
                    if (subMod[modeNumber][bStructNumber][subStructNumber].histo[i].GetEntries() > 0):
                        plotNumber += 1
                        cModSub[modeNumber][bStructNumber][subStructNumber].cd(i+2)
                        
                        # skip empty
                        if (mod[modeNumber][bStructNumber].histo[i].GetEntries() == 0):
                            break
                        
                        # normalize bStruct
                        mod[modeNumber][bStructNumber].histo[i].Scale( 1./mod[modeNumber][bStructNumber].histo[i].Integral() )
                        # get y maximum1
                        maximum1 = mod[modeNumber][bStructNumber].histo[i].GetMaximum()
                        
                        # normalize
                        if (subMod[modeNumber][bStructNumber][subStructNumber].histo[i].Integral() != 0):
                            subMod[modeNumber][bStructNumber][subStructNumber].histo[i].Scale(1./subMod[modeNumber][bStructNumber][subStructNumber].histo[i].Integral())
                        # get y maximum2
                        maximum2 = subMod[modeNumber][bStructNumber][subStructNumber].histo[i].GetMaximum()
                        
                        # set SetRangeUser
                        subMod[modeNumber][bStructNumber][subStructNumber].histo[i].GetYaxis().SetRangeUser(0., max([maximum1, maximum2]) * 1.1)
                                               
                        subMod[modeNumber][bStructNumber][subStructNumber].histo[i].Draw()
                        
                        mod[modeNumber][bStructNumber].histo[i].Draw("same")

                if (plotNumber == 0):
                    break
                
                cModSub[modeNumber][bStructNumber][subStructNumber].Update()
                
                # save as pdf
                cModSub[modeNumber][bStructNumber][subStructNumber].Print("{0}/plots/pdf/modules_{1}_{2}{3}.pdf".format(config.outputPath, mode, bStruct.getName(), subStructNumber+1))

                # export as png
                image.FromPad(cModSub[modeNumber][bStructNumber][subStructNumber])
                image.WriteImage("{0}/plots/png/modules_{1}_{2}{3}.png".format(config.outputPath, mode, bStruct.getName(), subStructNumber+1))
                
                # add to output list
                output = OutputData(plottype="subMod", name=bStruct.getName(), number=subStructNumber+1, parameter=mode, filename="modules_{0}_{1}{2}".format(mode, bStruct.getName(), subStructNumber+1))
                config.outputList.append(output)
            
            
    ##########################################################################
    # create TEX, beamer
    #
    
    pdfCreator.create(pedeDump, config.latexfile, config)
    beamerCreator.create(pedeDump, "beamer.tex", config)
    
if __name__ == "__main__":
    main()
