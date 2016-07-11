#!/usr/bin/env python

##########################################################################
# Create histograms out of treeFile_merge.root . The pede.dump.gz file is
# paresed. The histograms are plotted as PNG files. The output data is
# created as PDF, HTML, ...
##

import argparse
import logging
import os

from ROOT import (TH1F, TCanvas, TFile, TImage, TPaveLabel, TPaveText, TTree,
                  gROOT, gStyle)

from mpsvalidate import (additionalparser, beamerCreator, bigModule,
                         bigStructure, dumpparser, htmlCreator, monitorPlot,
                         pdfCreator, subModule, timeStructure)
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.classes import OutputData, PedeDumpData, PlotData
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.geometry import Alignables, Structure
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.iniparser import ConfigData
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.style import setgstyle


def main():
    # config logging module
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        datefmt="%d.%m.%Y %H:%M:%S")

    # run ROOT in batchmode
    gROOT.SetBatch()
    # create alignables object
    alignables = Alignables()

    # ArgumentParser
    parser = argparse.ArgumentParser(description="Validate your Alignment.")
    # TODO set default -> 0
    parser.add_argument(
        "-j", "--job", help="chose jobmX directory (default: ini-file)", default=-1, type=int)
    parser.add_argument(
        "-t", "--time", help="chose MillePedeUser_X Tree (default: ini-file)", default=-1, type=int)
    parser.add_argument("-i", "--ini", help="specify a ini file", default="-1")
    parser.add_argument("-m", "--message",
                        help="identification on every plot", default="")
    parser.add_argument("-p", "--jobdatapath",
                        help="path to the input files", default="")
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

    # create output directories
    if not os.path.exists("{0}/plots/pdf".format(config.outputPath)):
        os.makedirs("{0}/plots/pdf".format(config.outputPath))
    if not os.path.exists("{0}/plots/png".format(config.outputPath)):
        os.makedirs("{0}/plots/png".format(config.outputPath))

    # TODO check if there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    treeFile = TFile("{0}/treeFile_merge.root".format(config.jobDataPath))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(config.jobTime))
    if not MillePedeUser:
        logging.error("Error: Could not open TTree File MillePedeUser_{0} in {1}.treeFile_merge.root".format(
            config.jobTime, config.jobDataPath))
        return

    # set gStyle
    setgstyle()

    ##########################################################################
    # draw the plots of the millePedeMonitor_merge.root file
    #

    if (config.showmonitor == 1):
        monitorPlot.plot(config)

    ##########################################################################
    # parse the alignment_merge.py file
    #

    if (config.showadditional == 1):
        additionalData = additionalparser.AdditionalData()
        additionalData.parse(
            config, "{0}/alignment_merge.py".format(config.jobDataPath))

    ##########################################################################
    # parse the file pede.dump.gz and return a PedeDumpData Object
    #

    if (config.showdump == 1):
        pedeDump = dumpparser.parse(
            "{0}/pede.dump.gz".format(config.jobDataPath), config)

    ##########################################################################
    # time dependend big structures
    #

    if (config.showtime == 1):
        timeStructure.plot(treeFile, alignables, config)

    ##########################################################################
    # big structures
    #

    if (config.showhighlevel == 1):
        bigStructure.plot(MillePedeUser, alignables, config)

    ##########################################################################
    # modules of a hole structure
    # and part of structure
    #

    if (config.showmodule == 1):
        bigModule.plot(MillePedeUser, alignables, config)

    ##########################################################################
    # create TEX, beamer
    #

    if (config.showtex == 1):
        pdfCreator.create(alignables, pedeDump,
                          additionalData, config.latexfile, config)
    if (config.showbeamer == 1):
        beamerCreator.create(alignables, pedeDump, "beamer.tex", config)
    if (config.showhtml == 1):
        htmlCreator.create(alignables, pedeDump, "html_file.html", config)

if __name__ == "__main__":
    main()
