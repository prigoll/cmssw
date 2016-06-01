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
            mod[bStructNumber].histo.append(TH1F("{0} {1}".format(bStruct.getName(), mod[bStructNumber].xyz[i]), "Parameter {0}".format(mod[bStructNumber].xyz[i]), numberOfBins, -0.1, 0.1))
            mod[bStructNumber].histo[i].SetXTitle("[cm]")
            mod[bStructNumber].histoAxis.append(mod[bStructNumber].histo[i].GetXaxis())
        
        # add labels
        mod[bStructNumber].title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0}".format(bStruct.getName()))
        mod[bStructNumber].text = TPaveText(0.05, 0.1, 0.95, 0.75)
        mod[bStructNumber].text.SetTextAlign(13)
        mod[bStructNumber].text.SetTextSizePixels(20)        

        # fill histogram
        for line in MillePedeUser:
            if (line.ObjId == 1 and bStruct.containLabel(line.Label)):
                for i in range(3):
                    if (abs(line.Par[i]) != 999999): 
                        mod[bStructNumber].histo[i].Fill(line.Par[mod[bStructNumber].data[i]])
                        
        # find the best range
        for i in range(3):
            # get first and last bin with content and chose the one which has a greater distance to the center
            mod[bStructNumber].maxBinShift[i] = max( abs(numberOfBins/2-mod[bStructNumber].histo[i].FindFirstBinAbove()), abs(mod[bStructNumber].histo[i].FindLastBinAbove()-numberOfBins/2) )
            # skip empty histogram
            if (mod[bStructNumber].maxBinShift[i] == numberOfBins/2+1):
                mod[bStructNumber].maxBinShift[i] = 0
            # set the maxShift value
            mod[bStructNumber].maxShift[i] = mod[bStructNumber].histo[i].GetBinCenter( numberOfBins/2+mod[bStructNumber].maxBinShift[i] )

        # find and apply the new range
        for i in range(3):
            if (mod[bStructNumber].histo[i].GetEntries() != 0 and mod[bStructNumber].histo[i].GetStdDev() != 0):
                # if the plotrange is much bigger than the standard deviation use 3 * StdDev als Range
                # check the configData if it is allowed to hide data
                if ( max(mod[bStructNumber].maxShift)/mod[bStructNumber].histo[i].GetStdDev() > 9 and config.allowhidden == 1):
                    # corresponding bin 3*StdDev
                    binShift = int(mod[bStructNumber].histo[i].FindBin(3*mod[bStructNumber].histo[i].GetStdDev()) - numberOfBins/2)
                    # count entries which are not shown anymore
                    # bin 1 to begin of histogram
                    for j in range(1, numberOfBins/2 - binShift):
                        mod[bStructNumber].hiddenEntries[i] += mod[bStructNumber].histo[i].GetBinContent(j)
                    # from the end of shown bins to the end of histogram
                    for j in range(numberOfBins/2 + binShift, mod[bStructNumber].histo[i].GetNbinsX()):
                        mod[bStructNumber].hiddenEntries[i] += mod[bStructNumber].histo[i].GetBinContent(j)
                else:
                    binShift = max(mod[bStructNumber].maxBinShift)
                
                # save used binShift
                mod[bStructNumber].binShift[i] = binShift
                
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
                    mod[bStructNumber].histo[i] = mod[bStructNumber].histo[i].Rebin( mergeNumberBins )
                    mod[bStructNumber].histoAxis[i] = mod[bStructNumber].histo[i].GetXaxis()
                    
                    # set view range. it is important to note that the number of bins have changed with the rebinning
                    # the total number and the number of shift must be corrected with / mergeNumberBins
                    mod[bStructNumber].histoAxis[i].SetRange(int(numberOfBins/(2*mergeNumberBins)-binShift / mergeNumberBins), int(numberOfBins/(2*mergeNumberBins)+binShift / mergeNumberBins))
            
                
        # TODO chose good limit
        # error if shift is bigger than limit
        limit = 0.02
        for i in range(3):
            mod[bStructNumber].text.AddText("max. shift {0}: {1:.2}".format(mod[bStructNumber].xyz[i], mod[bStructNumber].maxShift[i]))
            if (mod[bStructNumber].maxShift[i] > limit):
                mod[bStructNumber].text.AddText("! {0} shift bigger than {1} !".format(mod[bStructNumber].xyz[i], limit))
            if (mod[bStructNumber].hiddenEntries[i] != 0):
                mod[bStructNumber].text.AddText("! {0} entries not shown !".format(int(mod[bStructNumber].hiddenEntries[i])))
    return mod