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
                  gROOT, gStyle, PyConfig)

from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate import (additionalparser, beamerCreator, bigModule,
                         bigStructure, dumpparser, htmlCreator, monitorPlot,
                         pdfCreator, subModule, timeStructure)
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.classes import OutputData, PedeDumpData, PlotData
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.geometry import Alignables, Structure
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.iniparser import ConfigData
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidate.style import setgstyle


def main():
    # config logging module
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(asctime)s (%(pathname)s line %(lineno)d): %(message)s", datefmt="%H:%M:%S")
    logger = logging.getLogger("logging")
    
    # run ROOT in batchmode
    gROOT.SetBatch()

    # ArgumentParser
    parser = argparse.ArgumentParser(description="Validate your Alignment.")
    parser.add_argument(
        "-j", "--job", help="chose jobmX directory (default: ini-file)", default=-1, type=int)
    parser.add_argument(
        "-t", "--time", help="chose MillePedeUser_X Tree (default: ini-file)", default=-1, type=int)
    parser.add_argument("-i", "--ini", help="specify a ini file", default="-1")
    parser.add_argument("-m", "--message",
                        help="identification on every plot", default="")
    parser.add_argument("-p", "--jobdatapath",
                        help="path to the jobm directory", default="")
    parser.add_argument("-l", "--logging",
                        help="if this argument is given a logging file (validation.log) is saved in the current directory", action="store_true")
    args = parser.parse_args()

    # create config object
    config = ConfigData()
    
    # create logging handler
    if(args.logging):
        handler = logging.FileHandler("validation.log", mode="w")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s %(asctime)s (%(pathname)s line %(lineno)d): %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # parse default ini file
    logger.info("start to parse the default.ini")
    config.parseConfig(os.path.join(config.mpspath, "default.ini"))

    # parse user ini file
    if (args.ini != "-1"):
        logger.info("start to parse the user ini: {0}".format(args.ini))
        config.parseConfig(args.ini)

    # override ini configs with consol parameter
    config.parseParameter(args)

    # create output directories
    logger.info("create the output directories")
    if not os.path.exists(os.path.join(config.outputPath, "plots/pdf")):
        os.makedirs(os.path.join(config.outputPath, "plots/pdf"))
    if not os.path.exists(os.path.join(config.outputPath, "plots/png")):
        os.makedirs(os.path.join(config.outputPath, "plots/png"))

    # open root file and get TTree MillePedeUser_X
    logger.info("try to open the root file: {0}".format(os.path.join(config.jobDataPath, "treeFile_merge.root")))
    treeFile = TFile(os.path.join(config.jobDataPath, "treeFile_merge.root"))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(config.jobTime))
    if not MillePedeUser:
        logger.error("Error: Could not open TTree File MillePedeUser_{0} in {1}".format(
            config.jobTime, os.path.join(config.jobDataPath, "treeFile_merge.root")))
        return

    # set gStyle
    setgstyle()
    
    # create alignables object
    alignables = Alignables(config)

    ##########################################################################
    # draw the plots of the millePedeMonitor_merge.root file
    #

    if (config.showmonitor == 1):
        logger.info("start to collect the plots of the millePedeMonitor_merge.root file")
        monitorPlot.plot(config)

    ##########################################################################
    # parse the alignment_merge.py file
    #

    if (config.showadditional == 1):
        logger.info("start to parse the alignment_merge.py file")
        additionalData = additionalparser.AdditionalData()
        additionalData.parse(
            config, os.path.join(config.jobDataPath, "alignment_merge.py"))

    ##########################################################################
    # parse the file pede.dump.gz and return a PedeDumpData Object
    #

    
    if (config.showdump == 1):
        logger.info("start to parse the pede.dump.gz file")
        pedeDump = dumpparser.parse(
            os.path.join(config.jobDataPath, "pede.dump.gz"), config)

    ##########################################################################
    # time dependend big structures
    #

    if (config.showtime == 1):
        logger.info("create the time dependend plots")
        timeStructure.plot(treeFile, alignables, config)

    ##########################################################################
    # big structures
    #

    if (config.showhighlevel == 1):
        logger.info("create the high level plots")
        bigStructure.plot(MillePedeUser, alignables, config)

    ##########################################################################
    # modules of a hole structure
    # and part of structure
    #

    if (config.showmodule == 1):
        logger.info("create the module plots")
        bigModule.plot(MillePedeUser, alignables, config)

    ##########################################################################
    # create TEX, beamer
    #

    if (config.showtex == 1):
        logger.info("create the latex file")
        pdfCreator.create(alignables, pedeDump,
                          additionalData, config.latexfile, config)
    if (config.showbeamer == 1):
        logger.info("create the latex beamer file")
        beamerCreator.create(alignables, pedeDump, "beamer.tex", config)
    if (config.showhtml == 1):
        logger.info("create the HTML file")
        htmlCreator.create(alignables, pedeDump, additionalData, "html_file.html", config)

if __name__ == "__main__":
    main()
