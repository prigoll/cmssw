#!/usr/bin/env python

##########################################################################
##  Creates histograms of the modules of a part of a structure and combines it
##  with a plot of the modules of the hole structure. Returns a nested
##  list with the TreeData of the histograms
##

from ROOT import TTree, TH1F, TPaveLabel, TPaveText, gStyle, gROOT, TCanvas, TImage, TLegend
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData, OutputData

def plot(MillePedeUser, geometryGetter, mode, struct, parentPlot, config):
    
    # skip empty
    number = 0
    for i in range(3):
        if(parentPlot.histo[i].GetEntries() == 0):
            number += 1
    if (number == 3):
        return
    
    # number of bins to start
    numberOfBins = 10000
    
    ######################################################################
    # initialize data hierarchy
    # plots[subStrucut]
    #
    
    plots = []

    # initialize histograms
    for subStructNumber, subStruct in enumerate(struct.getChildren()):
        plots.append( TreeData(mode) )
        
        # use a copy for shorter name
        plot = plots[subStructNumber]
        
        for i in range(3):
            if (mode == "xyz"):
                plot.histo.append(TH1F("{0} {1} {2}".format(subStruct.getName(), plot.xyz[i], mode), "Parameter {0}".format(plot.xyz[i]), numberOfBins, -1000, 1000))
            else:
                plot.histo.append(TH1F("{0} {1} {2}".format(subStruct.getName(), plot.xyz[i], mode), "Parameter {0}".format(plot.xyz[i]), numberOfBins, -0.1, 0.1))
            
            plot.histo[i].SetXTitle(plot.unit)
            plot.histo[i].SetLineColor(6)
            plot.histo[i].SetStats(0)
        
        # add labels
        plot.title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Module: {0} {1}".format(subStruct.getName(), mode))
        plot.text = TPaveText(0.05, 0.1, 0.95, 0.75)
        plot.text.SetTextAlign(12)
        plot.text.SetTextSizePixels(20) 
                
        # save copy
        plots[subStructNumber] = plot
    
    
    ######################################################################
    # fill histogram
    #
    
    for line in MillePedeUser:
        # is module ?
        if (line.ObjId == 1):
            for subStructNumber, subStruct in enumerate(struct.getChildren()):
                # use a copy for shorter name
                plot = plots[subStructNumber]
        
                # module in struct ?
                if (subStruct.containLabel(line.Label)):
                    for i in range(3):
                        if (abs(line.Par[ plot.data[i] ]) != 999999):
                            # transform xyz data from cm to #mu m
                            if (mode == "xyz"):
                                plot.histo[i].Fill(10000*line.Par[ plot.data[i] ])
                            else:
                                plot.histo[i].Fill(line.Par[ plot.data[i] ])
                            
                # save copy
                plots[subStructNumber] = plot
    
    ######################################################################
    # find the best range
    #
    for subStructNumber, subStruct in enumerate(struct.getChildren()):
        # use a copy for shorter name
        plot = plots[subStructNumber]
        for i in range(3):
            if (plot.histo[i].GetEntries() != 0 and plot.histo[i].GetStdDev() != 0):
                # use binShift of the hole structure
                binShift = parentPlot.usedRange[i]
                
                # count entries which are not shown anymore
                # bin 1 to begin of histogram
                for j in range(1, numberOfBins/2 - binShift):
                    plot.hiddenEntries[i] += plot.histo[i].GetBinContent(j)
                # from the end of shown bins to the end of histogram
                for j in range(numberOfBins/2 + binShift, plot.histo[i].GetNbinsX()):
                    plot.hiddenEntries[i] += plot.histo[i].GetBinContent(j)
                
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
                    plot.histo[i] = plot.histo[i].Rebin( mergeNumberBins )
                    
                    # set view range. it is important to note that the number of bins have changed with the rebinning
                    # the total number and the number of shift must be corrected with / mergeNumberBins
                    plot.histo[i].GetXaxis().SetRange(int(numberOfBins/(2*mergeNumberBins)-binShift / mergeNumberBins), int(numberOfBins/(2*mergeNumberBins)+binShift / mergeNumberBins))
                        
        # save copy
        plots[subStructNumber] = plot
    
    ######################################################################
    # make the plots
    #
    
    canvas = TCanvas("SubStruct_{0}_{1}".format(struct.getName(), mode), "Parameter", 300, 0, 800, 600)
    canvas.Divide(2, 2)
    
    canvas.cd(1)
    parentPlot.title.Draw()
    
    legend = TLegend(0.05, 0.1, 0.95, 0.75)
    
    for i in range(3):
        canvas.cd(i+2)
        
        # find y maximum
        maximum = []
        
        if (parentPlot.histo[i].GetEntries() == 0):
            break
    
        # normalize parent
        parentPlot.histo[i].Scale( 1./parentPlot.histo[i].Integral() )
        maximum.append(parentPlot.histo[i].GetMaximum())
        
        for subStructNumber, subStruct in enumerate(struct.getChildren()):
            # use a copy for shorter name
            plot = plots[subStructNumber]
            
            if (plot.histo[i].GetEntries() > 0):
                plot.histo[i].Scale( 1./plot.histo[i].Integral() )
                maximum.append(plot.histo[i].GetMaximum())
            
            # save copy
            plots[subStructNumber] = plot
                
                
        # set range and plot
        parentPlot.histo[i].GetYaxis().SetRangeUser(0., 1.05*max(maximum))
        parentPlot.histo[i].Draw()
        
        for subStructNumber, subStruct in enumerate(struct.getChildren()):
            # use a copy for shorter name
            plot = plots[subStructNumber].histo[i]
            
            plot.SetLineColorAlpha(subStructNumber+2, 0.5)
            plot.Draw("same")
            if (i == 0):
                legend.AddEntry(plot, "{0}".format(subStructNumber), "l")
            
    canvas.cd(1)
    legend.Draw()
    canvas.Update()
    
    # save as pdf
    canvas.Print("{0}/plots/pdf/subModules_{1}_{2}.pdf".format(config.outputPath, mode, struct.getName()))

    # export as png
    image = TImage.Create()
    image.FromPad(canvas)
    image.WriteImage("{0}/plots/png/subModules_{1}_{2}.png".format(config.outputPath, mode, struct.getName()))
    
    # add to output list
    output = OutputData(plottype="subMod", name=struct.getName(), number=subStructNumber+1, parameter=mode, filename="subModules_{0}_{1}".format(mode, struct.getName()))
    config.outputList.append(output)
