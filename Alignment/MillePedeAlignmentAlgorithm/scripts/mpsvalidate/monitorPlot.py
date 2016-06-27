#!/usr/bin/env python

##########################################################################
# Draw the plots saved in the millePedeMonitor_merge.root file
#

from ROOT import TH1F, gStyle, TCanvas, TFile, TImage

from mpsvalidate.classes import OutputData


def plot(path, config):
    # adjust the plot style
    # show the skewness in the legend
    gStyle.SetOptStat("emrs")
    gStyle.SetPadLeftMargin(0.07)

    # open file
    rootfile = TFile("{0}".format(path))

    plotPaths = ["trackHists/r1Track", "trackHists/ptTrack",
                 "trackHists/etaTrack", "usedTrackHists/usedptTrack"]
    # loop over plots which should be plotted
    for plotPath in plotPaths:
        # get plotname
        plotName = plotPath.split("/")[1]
        # get plot
        plot = rootfile.Get(plotPath)

        # create canvas
        canvas = TCanvas("canvasModules{0}".format(
            plotName), "Parameter", 300, 0, 800, 600)
        canvas.cd()

        plot.Draw()

        # save as pdf
        canvas.Print(
            "{0}/plots/pdf/monitor_{1}.pdf".format(config.outputPath, plotName))

        # export as png
        image = TImage.Create()
        image.FromPad(canvas)
        image.WriteImage(
            "{0}/plots/png/monitor_{1}.png".format(config.outputPath, plotName))

        # add to output list
        output = OutputData(plottype="monitor", name=plotName,
                            filename="monitor_{0}".format(plotName))
        config.outputList.append(output)

    # reset the plot style
    gStyle.SetOptStat(0)
    gStyle.SetPadLeftMargin(0.17)
