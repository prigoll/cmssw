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

from mpsvalidate import (beamerCreator, bigModule, bigStructure, htmlCreator,
                         monitorPlot, pdfCreator, subModule, timeStructure)
from mpsvalidate.classes import (GeometryGetter, LogData, OutputData, Struct,
                                 TreeData)
from mpsvalidate.dumpparser import parse
from mpsvalidate.iniparser import ConfigData
from mpsvalidate.style import setgstyle


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
    parser.add_argument(
        "-j", "--job", help="chose jobmX directory (default: ini-file)", default=-1, type=int)
    parser.add_argument(
        "-t", "--time", help="chose MillePedeUser_X Tree (default: ini-file)", default=-1, type=int)
    parser.add_argument("-i", "--ini", help="specify a ini file", default="-1")
    parser.add_argument("-m", "--message",
                        help="identification on every plot", default="mpXXXX")
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

    # set gStyle
    setgstyle()

    ##########################################################################
    # draw the plots of the millePedeMonitor_merge.root file
    #

    if (config.showmonitor == 1):
        monitorPlot.plot(
            "{0}/millePedeMonitor_merge.root".format(config.jobDataPath), config)

    ##########################################################################
    # parse the file pede.dump.gz and return a LogData Object
    #

    if (config.showdump == 1):
        pedeDump = parse("{0}/pede.dump.gz".format(config.jobDataPath), config)

    ##########################################################################
    # time dependend big structures
    #

    if (config.showtime == 1):
        timeStructure.plot(treeFile, geometryGetter, config)

    ##########################################################################
    # big structures
    #

    if (config.showhighlevel == 1):
        big = bigStructure.plot(MillePedeUser, geometryGetter, config)

    ##########################################################################
    # modules of a hole structure
    # and part of structure
    #

    if (config.showmodule == 1):
        bigModule.plot(MillePedeUser, geometryGetter, config)

    ##########################################################################
    # create TEX, beamer
    #

    if (config.showdump == 1 and config.showtime == 1 and config.showhighlevel == 1 and config.showmodule == 1 and config.showbeamer == 1 and config.showsubmodule):
        if (config.showtex == 1):
            pdfCreator.create(pedeDump, config.latexfile, config)
        if (config.showbeamer == 1):
            beamerCreator.create(pedeDump, "beamer.tex", config)
        if (config.showhtml == 1):
            htmlCreator.create(pedeDump, "html_file.html", config)

if __name__ == "__main__":
    main()
