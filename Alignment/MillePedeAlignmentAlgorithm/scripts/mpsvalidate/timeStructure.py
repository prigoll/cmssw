#!/usr/bin/env python

##########################################################################
##  Creates a histogram where the the names of the structures are present
##  as humanreadable text. Multiple MillePedeUser TTrees are used to
##  get a time dependent plot.
##

from ROOT import TTree, TH1F, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData

def plot(MillePedeUser, geometryGetter, mode, config, jobTime):
        
       
    big = TreeData(mode)
    
    # count number of needed bins and max/min shift
    for line in MillePedeUser:
        if (line.ObjId != 1):
            for i in range(3):
                if (abs(line.Par[i]) != 999999):
                    big.numberOfBins[i] += 1
                    if (line.Par[i] > big.maxShift[i]):
                        big.maxShift[i] = line.Par[i]
                    if (line.Par[i] < big.minShift[i]):
                        big.minShift[i] = line.Par[i]
    
    # initialize histograms
    for i in range(3):
        big.histo.append(TH1F("Time Structure {0} {1} {2}".format(big.xyz[i], mode, jobTime), "Parameter {0}".format(big.xyz[i]), big.numberOfBins[i], 0, big.numberOfBins[i]))
        big.histo[i].SetYTitle("[cm]")
        big.histo[i].SetStats(0)
        big.histo[i].SetMarkerStyle(5)
        big.histoAxis.append(big.histo[i].GetXaxis())
        # bigger labels for the text
        big.histoAxis[i].SetLabelSize(0.06)
        big.histo[i].GetYaxis().SetTitleOffset(1.6)
        
    
    # add labels
    big.title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "Time dependent Structures {0}".format(mode))
    big.text = TPaveText(0.05, 0.1, 0.95, 0.75)
    big.text.SetTextAlign(12)
    
    # fill histograms with value and name
    for line in MillePedeUser:
        if (line.ObjId != 1):
            for i in range(3):
                if (abs(line.Par[ big.data[i] ]) != 999999):
                    # set name of the structure
                    big.histoAxis[i].SetBinLabel(big.binPosition[i], geometryGetter.name_by_objid(line.ObjId))
                    # fill with data, big.data[i] xyz or rot data
                    big.histo[i].SetBinContent(big.binPosition[i], line.Par[ big.data[i] ])
                    big.binPosition[i] += 1
    
    # rotate labels
    for i in range(3):
        big.histoAxis[i].LabelsOption("v")
    

    
    # reset BottomMargin
    gStyle.SetPadBottomMargin(0.1)
    
    return big