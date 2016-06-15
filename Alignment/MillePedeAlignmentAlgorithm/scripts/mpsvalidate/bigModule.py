#!/usr/bin/env python

##########################################################################
##  Creates histograms of the modules of one structure. and returns them as
##  a list of TreeData objects.
##

from ROOT import TTree, TH1F, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData

def plot(MillePedeUser, geometryGetter, mode, config):
    
    mod = []

    # loop over all structures
    for bStructNumber, bStruct in enumerate(geometryGetter.listbStructs()):
        
        
        mod.append(TreeData(mode))
        
        numberOfBins = 10000
                        
        # initialize histograms
        for i in range(3):
            # bigger range if plot is xyz
            if (mode=="xyz"):
                mod[bStructNumber].histo.append(TH1F("{0} {1} {2}".format(bStruct.getName(), mod[bStructNumber].xyz[i], mode), "Parameter {0}".format(mod[bStructNumber].xyz[i]), numberOfBins, -1000, 1000))
            else:
                mod[bStructNumber].histo.append(TH1F("{0} {1} {2}".format(bStruct.getName(), mod[bStructNumber].xyz[i], mode), "Parameter {0}".format(mod[bStructNumber].xyz[i]), numberOfBins, -0.1, 0.1))
            mod[bStructNumber].histo[i].SetXTitle(mod[bStructNumber].unit)
            mod[bStructNumber].histoAxis.append(mod[bStructNumber].histo[i].GetXaxis())
        
        # add labels
        mod[bStructNumber].title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0} {1}".format(bStruct.getName(), mode))
        mod[bStructNumber].text = TPaveText(0.05, 0.1, 0.95, 0.75)
        mod[bStructNumber].text.SetTextAlign(12)
        mod[bStructNumber].text.SetTextSizePixels(20)        

        # fill histogram
        for line in MillePedeUser:
            if (line.ObjId == 1 and bStruct.containLabel(line.Label)):
                for i in range(3):
                    if (abs(line.Par[ mod[bStructNumber].data[i] ]) != 999999): 
                        # transform xyz data from cm to #mu m
                        if (mode == "xyz"):
                            mod[bStructNumber].histo[i].Fill(10000*line.Par[ mod[bStructNumber].data[i] ])
                        else:
                            mod[bStructNumber].histo[i].Fill(line.Par[ mod[bStructNumber].data[i] ])
                        
         # find the best range
        for i in range(3):
            # get first and last bin with content and chose the one which has a greater distance to the center
            if (abs(numberOfBins/2-mod[bStructNumber].histo[i].FindFirstBinAbove()) > abs(mod[bStructNumber].histo[i].FindLastBinAbove()-numberOfBins/2) ):
                mod[bStructNumber].maxBinShift[i] = abs(numberOfBins/2-mod[bStructNumber].histo[i].FindFirstBinAbove())
                # set the maxShift value
                mod[bStructNumber].maxShift[i] = mod[bStructNumber].histo[i].GetBinCenter(mod[bStructNumber].histo[i].FindFirstBinAbove())
            else:
                mod[bStructNumber].maxBinShift[i] = abs(mod[bStructNumber].histo[i].FindLastBinAbove()-numberOfBins/2)
                # set the maxShift value
                mod[bStructNumber].maxShift[i] = mod[bStructNumber].histo[i].GetBinCenter(mod[bStructNumber].histo[i].FindLastBinAbove())
            # skip empty histogram
            if (abs(mod[bStructNumber].maxBinShift[i]) == numberOfBins/2+1):
                mod[bStructNumber].maxBinShift[i] = 0

        # three types of ranges
        
        # 1. multiple of standard dev
        if (config.rangemode == 1):
            for i in range(3):
                if (mod[bStructNumber].histo[i].GetEntries() != 0 and mod[bStructNumber].histo[i].GetStdDev() != 0):
                    # if the plotrange is much bigger than the standard deviation use config.widthstdev * StdDev als Range
                    # check the configData if it is allowed to hide data
                    if ( max(mod[bStructNumber].maxShift)/mod[bStructNumber].histo[i].GetStdDev() > config.defpeak and config.allowhidden == 1 or config.forcestddev == 1):
                        # corresponding bin config.widthstdev*StdDev
                        binShift = int(mod[bStructNumber].histo[i].FindBin(config.widthstddev*mod[bStructNumber].histo[i].GetStdDev()) - numberOfBins/2)
                    else:
                        binShift = max(mod[bStructNumber].maxBinShift)
                    
                    # save used binShift
                    mod[bStructNumber].binShift[i] = binShift
        
        # 2. show all
        if (config.rangemode == 2):
            for i in range(3):
                mod[bStructNumber].binShift[i] = mod[bStructNumber].maxBinShift[i]
                
        # 3. use given ranges
        if (config.rangemode == 3):
            for i in range(3):
                if (mode == "xyz"):
                    valuelist = config.rangexyzM
                if (mode == "rot"):
                    valuelist = config.rangerotM
                if (mode == "dist"):
                    valuelist = config.rangedistM
                    
                for value in valuelist:
                    # maximum smaller than given value
                    if (abs(mod[bStructNumber].maxShift[i]) < value):
                        binShift = value
                        break
                # if not possible, force highest
                if (abs(mod[bStructNumber].maxShift[i]) > valuelist[-1]):
                    binShift = valuelist[-1]
                # calculate binShift
                mod[bStructNumber].binShift[i] = int(binShift/mod[bStructNumber].histo[i].GetBinWidth(1))

        
        # all plot the same range
        if (config.samerange == 1):
            for i in range(3):
                mod[bStructNumber].binShift[i] = max(mod[bStructNumber].binShift)
                
        # save used range
        for i in range(3):
            mod[bStructNumber].usedRange[i] = mod[bStructNumber].binShift[i]
                
        # count entries which are not shown anymore
        for i in range(3):
            # bin 1 to begin of histogram
            for j in range(1, numberOfBins/2 - mod[bStructNumber].binShift[i]):
                mod[bStructNumber].hiddenEntries[i] += mod[bStructNumber].histo[i].GetBinContent(j)
            # from the end of shown bins to the end of histogram
            for j in range(numberOfBins/2 + mod[bStructNumber].binShift[i], mod[bStructNumber].histo[i].GetNbinsX()):
                mod[bStructNumber].hiddenEntries[i] += mod[bStructNumber].histo[i].GetBinContent(j)
        
        # apply new range
        for i in range(3):
            if (mod[bStructNumber].histo[i].GetEntries() != 0):
                # merge bins, ca. 100 should be visible in the resulting plot
                mergeNumberBins = mod[bStructNumber].binShift[i]
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
                    mod[bStructNumber].histo[i] = mod[bStructNumber].histo[i].Rebin( mergeNumberBins )
                    mod[bStructNumber].histoAxis[i] = mod[bStructNumber].histo[i].GetXaxis()
                    
                    # set view range. it is important to note that the number of bins have changed with the rebinning
                    # the total number and the number of shift must be corrected with / mergeNumberBins
                    mod[bStructNumber].histoAxis[i].SetRange(int(numberOfBins/(2*mergeNumberBins)-mod[bStructNumber].binShift[i] / mergeNumberBins), int(numberOfBins/(2*mergeNumberBins)+mod[bStructNumber].binShift[i] / mergeNumberBins))
            
                
        # TODO chose good limit
        # error if shift is bigger than limit
        limit = 0.02
        for i in range(3):
            # skip empty
            if (mod[bStructNumber].histo[i].GetEntries() > 0):
                mod[bStructNumber].text.AddText("max. shift {0}: {1:.2}".format(mod[bStructNumber].xyz[i], mod[bStructNumber].maxShift[i]))
                if (abs(mod[bStructNumber].maxShift[i]) > limit):
                    mod[bStructNumber].text.AddText("! {0} shift bigger than {1} !".format(mod[bStructNumber].xyz[i], limit))
                if (mod[bStructNumber].hiddenEntries[i] != 0):
                    mod[bStructNumber].text.AddText("! {0} {1} outlier !".format(mod[bStructNumber].xyz[i], int(mod[bStructNumber].hiddenEntries[i])))
    return mod