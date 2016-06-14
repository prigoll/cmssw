#!/usr/bin/env python

##########################################################################
##  Creates a histogram where the the names of the structures are present
##  as humanreadable text.
##

from ROOT import TTree, TH1F, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData

def plot(MillePedeUser, geometryGetter, mode, config):
        
       
    big = TreeData(mode)
    
    # count number of needed bins and max shift
    for line in MillePedeUser:
        if (line.ObjId != 1):
            for i in range(3):
                if (abs(line.Par[ big.data[i] ]) != 999999):
                    if (mode == "xyz"):
                        line.Par[ big.data[i] ] *= 10000                    
                    big.numberOfBins[i] += 1
                    if (abs(line.Par[ big.data[i] ]) > abs(big.maxShift[i])):
                        big.maxShift[i] = line.Par[ big.data[i] ]
    
    # initialize histograms
    for i in range(3):
        big.histo.append(TH1F("Big Structure {0} {1}".format(big.xyz[i], mode), "Parameter {0}".format(big.xyz[i]), big.numberOfBins[i], 0, big.numberOfBins[i]))
        big.histo[i].SetYTitle(big.unit)
        big.histo[i].SetStats(0)
        big.histo[i].SetMarkerStyle(5)
        big.histoAxis.append(big.histo[i].GetXaxis())
        # bigger labels for the text
        big.histoAxis[i].SetLabelSize(0.06)
        big.histo[i].GetYaxis().SetTitleOffset(1.6)
        
    
    # add labels
    big.title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "High Level Structures {0}".format(mode))
    big.text = TPaveText(0.05, 0.1, 0.95, 0.75)
    big.text.SetTextAlign(12)
    
    # TODO chose good limit
    # error if shift is bigger than limit
    limit = 0.02
    for i in range(3):
        big.text.AddText("max. shift {0}: {1:.2}".format(big.xyz[i], big.maxShift[i]))
        if (abs(big.maxShift[i]) > limit):
            big.text.AddText("! {0} shift bigger than {1} !".format(big.xyz[i], limit))
    
    # fill histograms with value and name
    for line in MillePedeUser:
        if (line.ObjId != 1):
            for i in range(3):
                if (abs(line.Par[ big.data[i] ]) != 999999):
                    # set name of the structure
                    big.histoAxis[i].SetBinLabel(big.binPosition[i], geometryGetter.name_by_objid(line.ObjId))
                    # fill with data, big.data[i] xyz or rot data
                    # transform xyz data from cm to #mu m
                    if (mode=="xyz"):
                        big.histo[i].SetBinContent(big.binPosition[i], 10000*line.Par[ big.data[i] ])
                    else:
                        big.histo[i].SetBinContent(big.binPosition[i], line.Par[ big.data[i] ])
                    big.binPosition[i] += 1
    
    # rotate labels
    for i in range(3):
        big.histoAxis[i].LabelsOption("v")
    
    # reset y range
    
    # use given values
    # TODO what value
    # TODO when to apply given values
    
    # TODO own configuration?
    # all the same range
    if (config.samerange == 1):
        # apply new range
        for i in range(3):
            big.histo[i].GetYaxis().SetRangeUser( -1.05*max(map(abs, big.maxShift)), 1.05*max(map(abs, big.maxShift)) )

    
    # reset BottomMargin
    gStyle.SetPadBottomMargin(0.1)
    
    return big