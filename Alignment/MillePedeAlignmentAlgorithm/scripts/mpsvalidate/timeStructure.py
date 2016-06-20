#!/usr/bin/env python

##########################################################################
##  Creates a histogram where the the names of the structures are present
##  as humanreadable text. Multiple MillePedeUser TTrees are used to
##  get a time dependent plot.
##

from ROOT import TTree, TH1F, TPaveLabel, TPaveText, gStyle, gROOT, TCanvas, TLegend, TImage
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData, OutputData
from mpsvalidate.style import identification

def plot(treeFile, geometryGetter, config):
    
    for mode in ["xyz", "rot"]:
        
        time = TreeData(mode)
        
        # list of all avaible TTrees
        listMillePedeUser = []
        MillePedeUser = []
        # TODO use Ttrees in ini file
        for i in range(config.firsttree, 101):
            if (treeFile.GetListOfKeys().Contains("MillePedeUser_{0}".format(i))):
                listMillePedeUser.append(i)
                
        # load MillePedeUser_X TTrees
        for i in listMillePedeUser:
            MillePedeUser.append(treeFile.Get("MillePedeUser_{0}".format(i)))
        
        ######################################################################
        # remove TTrees without results
        #
        
        # check if there is a TTree without any results
        # therefor search for the first alignable
        first = 0
        newlistMillePedeUser = []
        # find first alignable
        for line in MillePedeUser[0]:
            if (line.ObjId != 1 and any(abs(line.Par[ time.data[i] ])!=999999 for i in [0,1,2])):
                first = line.Id
                newlistMillePedeUser.append(config.firsttree)
                break
            
        # check the following TTrees
        for ttreeNumber, ttree in enumerate(MillePedeUser[1:]):
            for line in  ttree:
                if (line.Id == first):
                    if (any(abs(line.Par[ time.data[i] ])!=999999 for i in [0,1,2])):
                        # note that the first tree was checked
                        newlistMillePedeUser.append(ttreeNumber+config.firsttree+1)
                    break
        
        listMillePedeUser = newlistMillePedeUser
        
        # reload MillePedeUser_X TTrees
        MillePedeUser = []
        for i in listMillePedeUser:
            MillePedeUser.append(treeFile.Get("MillePedeUser_{0}".format(i)))
        
                
        ######################################################################
        # initialize data hierarchy
        #
        
        plots = []
        # objids which were found in the TTree
        objids = []
        
        # loop over first tree to initialize
        for line in MillePedeUser[0]:
            if (line.ObjId != 1 and any(abs(line.Par[ time.data[i] ])!=999999 for i in [0,1,2])):
                plots.append( TreeData(mode) )
                
                # new objid?
                if (line.ObjId not in objids):
                    objids.append(line.ObjId)
                
                # initialize histograms
                for i in range(3):
                    plots[-1].histo.append(TH1F("Time Structure {0} {1} {2} {3}".format(mode, geometryGetter.name_by_objid(line.ObjId), len(plots), i), "Parameter {0}".format(time.xyz[i]), len(listMillePedeUser), 0, len(listMillePedeUser)))
                    plots[-1].label = line.Id
                    plots[-1].objid = line.ObjId
                    
                    plots[-1].histo[i].SetYTitle(time.unit)
                    plots[-1].histo[i].SetStats(0)
                    plots[-1].histo[i].SetMarkerStyle(21)
                    # bigger labels for the text
                    plots[-1].histo[i].GetXaxis().SetLabelSize(0.06)
                    plots[-1].histo[i].GetYaxis().SetTitleOffset(1.6)
                    
                    
        ######################################################################
        # fill histogram
        #
        
        # loop over TTrees
        for treeNumber, tree in enumerate(MillePedeUser):
            for line in tree:
                if (line.ObjId != 1 and any(abs(line.Par[ time.data[i] ])!=999999 for i in [0,1,2])):
                    # find the right plot
                    for plot in plots:
                        if (plot.label == line.Id):
                            for i in range(3):
                                # note that the first bin is referenced by 1
                                plot.histo[i].GetXaxis().SetBinLabel(treeNumber+1, str(listMillePedeUser[treeNumber]))
                                plot.histo[i].SetBinContent(treeNumber+1, line.Par[ plot.data[i] ])
                    
        ######################################################################
        # find maximum/minimum
        #
        
        maximum = [[0,0,0] for x in range(len(objids))]
        minimum = [[0,0,0] for x in range(len(objids))]
        
        for index, objid in enumerate(objids):
            for plot in plots:
                if (plot.objid == objid):
                    for i in range(3):
                        # maximum
                        if (plot.histo[i].GetMaximum() > maximum[index][i]):
                            maximum[index][i] = plot.histo[i].GetMaximum()
                        # minimum
                        if (plot.histo[i].GetMinimum() < minimum[index][i]):
                            minimum[index][i] = plot.histo[i].GetMinimum()
            
        
        ######################################################################
        # make the plots
        #
        
        # loop over all objids
        for index, objid in enumerate(objids):
        
            canvas = TCanvas("canvasTimeBigStrucutres_{0}_{1}".format(mode, geometryGetter.name_by_objid(objid)), "Parameter", 300, 0, 800, 600)
            canvas.Divide(2,2)
            
            # add text
            title = TPaveLabel(0.1, 0.8, 0.9, 0.9, "{0} over time {1}".format(geometryGetter.name_by_objid(objid), mode))
            
            legend = TLegend(0.05, 0.1, 0.95, 0.75)
            
            # draw on canvas
            canvas.cd(1)
            title.Draw()
            
            # draw identification
            ident = identification(config)
            ident.Draw()
            
            # draw plots on canvas
            # loop over coordinates
            for i in range(3):
                canvas.cd(2+i)
                        
                # set first plot to maximum/minimum
                for plot in plots:
                    if (plot.objid == objid):
                        plot.histo[i].SetMaximum(1.05*maximum[index][i])
                        plot.histo[i].SetMinimum(1.05*minimum[index][i])
                        break
                
                number = 1
                
                for plot in plots:
                    if (plot.objid == objid):
                        plot.histo[i].SetLineColorAlpha(number+2, 0.5)
                        plot.histo[i].SetMarkerColorAlpha(number+2, 1)
                        plot.histo[i].Draw("lpsame")
                        if (i == 0):
                            legend.AddEntry(plot.histo[i], "{0}".format(number))
                        number += 1
            
            canvas.cd(1)
            legend.Draw()
            
            canvas.Update()
            
            # save as pdf
            canvas.Print("{0}/plots/pdf/timeStructures_{1}_{2}.pdf".format(config.outputPath, mode, geometryGetter.name_by_objid(objid)))
            
            # export as png
            image = TImage.Create()
            image.FromPad(canvas)
            image.WriteImage("{0}/plots/png/timeStructures_{1}_{2}.png".format(config.outputPath, mode, geometryGetter.name_by_objid(objid)))
            
            # add to output list
            output = OutputData(plottype="time", parameter=mode, filename="timeStructures_{0}_{1}".format(mode, geometryGetter.name_by_objid(objid)))
            config.outputList.append(output)
