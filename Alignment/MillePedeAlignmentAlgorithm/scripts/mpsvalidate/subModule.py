#!/usr/bin/env python

##########################################################################
##  Creates histograms of the modules of a part of a structure and combines it
##  with a plot of the modules of the hole structure. Returns a nested
##  list with the TreeData of the histograms
##

from ROOT import TTree, TH1F, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData

def plot(MillePedeUser, geometryGetter, mod, mode, config):
    # get modeNumber
    if (mode == "xyz"):
        modeNumber = 0
    if (mode == "rot"):
        modeNumber = 1
    if (mode == "dist"):
        modeNumber = 2
    
    # nested list with the TreeData
    modSub = []
    
    # number of bins to create the plot
    # shrinked afterwards
    numberOfBins = 10000

    # loop over a hole structure
    for bStructNumber, bStruct in enumerate(geometryGetter.listbStructs()):
        modSub.append([])
        # loop over the parts of a strucutre
        for subStructNumber, subStruct in enumerate(bStruct.getChildren()):
            
            modSub[bStructNumber].append(TreeData(mode))
            
            
            # initialize histograms
            for i in range(3):
                modSub[bStructNumber][subStructNumber].histo.append(TH1F("{0} {1} {2}".format(subStruct.getName(), modSub[bStructNumber][subStructNumber].xyz[i], mode), "Parameter {0}".format(modSub[bStructNumber][subStructNumber].xyz[i]), numberOfBins, -0.1, 0.1))
                modSub[bStructNumber][subStructNumber].histo[i].SetXTitle("[cm]")
                modSub[bStructNumber][subStructNumber].histoAxis.append(modSub[bStructNumber][subStructNumber].histo[i].GetXaxis())
                modSub[bStructNumber][subStructNumber].histo[i].SetLineColor(6)
            
            # add labels
            modSub[bStructNumber][subStructNumber].title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0} {1}".format(subStruct.getName(), mode))
            modSub[bStructNumber][subStructNumber].text = TPaveText(0.05, 0.1, 0.95, 0.75)
            modSub[bStructNumber][subStructNumber].text.SetTextAlign(12)
            modSub[bStructNumber][subStructNumber].text.SetTextSizePixels(20)
            
            # fill histogram
            for line in MillePedeUser:
                if (line.ObjId == 1 and subStruct.containLabel(line.Label)):
                    for i in range(3):
                        if (abs(line.Par[ modSub[bStructNumber][subStructNumber].data[i] ]) != 999999): 
                            modSub[bStructNumber][subStructNumber].histo[i].Fill(line.Par[ modSub[bStructNumber][subStructNumber].data[i] ])
                
            
            # find and apply the new range
            for i in range(3):
                if (modSub[bStructNumber][subStructNumber].histo[i].GetEntries() != 0 and modSub[bStructNumber][subStructNumber].histo[i].GetStdDev() != 0):
                    # use binShift of the hole structure
                    binShift = mod[modeNumber][bStructNumber].binShift[i]
                    
                    # count entries which are not shown anymore
                    # bin 1 to begin of histogram
                    for j in range(1, numberOfBins/2 - binShift):
                        modSub[bStructNumber][subStructNumber].hiddenEntries[i] += modSub[bStructNumber][subStructNumber].histo[i].GetBinContent(j)
                    # from the end of shown bins to the end of histogram
                    for j in range(numberOfBins/2 + binShift, modSub[bStructNumber][subStructNumber].histo[i].GetNbinsX()):
                        modSub[bStructNumber][subStructNumber].hiddenEntries[i] += modSub[bStructNumber][subStructNumber].histo[i].GetBinContent(j)
                    
                    # merge bins, ca. 100 should be visible in the resulting plot
                    mergeNumberBins = binShift
                    # skip empty histogram
                    if (mergeNumberBins != 0):
                        # the 2*maxBinShift bins should shrink to 100 bins
                        mergeNumberBins = int(2.*mergeNumberBins/config.numberofbins)
                        # the total number of bins should be dividable by the bins shrinked together
                        if (mergeNumberBins == 0):
                            mergeNumberBins = 1
                        while (numberOfBins%mergeNumberBins != 0 and mergeNumberBins != 1):
                            mergeNumberBins -= 1
                        
                        # Rebin and save new created histogram and axis
                        modSub[bStructNumber][subStructNumber].histo[i] = modSub[bStructNumber][subStructNumber].histo[i].Rebin( mergeNumberBins )
                        modSub[bStructNumber][subStructNumber].histoAxis[i] = modSub[bStructNumber][subStructNumber].histo[i].GetXaxis()
                        
                        # set view range. it is important to note that the number of bins have changed with the rebinning
                        # the total number and the number of shift must be corrected with / mergeNumberBins
                        modSub[bStructNumber][subStructNumber].histoAxis[i].SetRange(int(numberOfBins/(2*mergeNumberBins)-binShift / mergeNumberBins), int(numberOfBins/(2*mergeNumberBins)+binShift / mergeNumberBins))
            
            # output hiddenEntries
            for i in range(3):
                # skip empty
                if (modSub[bStructNumber][subStructNumber].histo[i].GetEntries() > 0):
                    if (modSub[bStructNumber][subStructNumber].hiddenEntries[i] != 0):
                        modSub[bStructNumber][subStructNumber].text.AddText("! {0} {1} entries not shown !".format(modSub[bStructNumber][subStructNumber].xyz[i], int(modSub[bStructNumber][subStructNumber].hiddenEntries[i])))
                        
    return modSub