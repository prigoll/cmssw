#!/usr/bin/env python

##########################################################################
##  Create histograms out of treeFile_merge.root . The pede.dump.gz file is
##  paresed. The histograms are plotted as PNG files. The output data is
##  created as PDF, HTML, ...
##

from ROOT import TTree, TFile, TH1F, TCanvas, TImage, TPaveLabel, TPaveText, gStyle, gROOT
from mpsvalidate.classes import GeometryGetter, Struct, TreeData, LogData, OutputData
from mpsvalidate.dumpparser import parse
from mpsvalidate.iniparser import ConfigData
from mpsvalidate import bigStructure, bigModule, subModule, pdfCreator, beamerCreator, timeStructure

import argparse
import logging
import os

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
    parser.add_argument("-j", "--job", help="chose jobmX directory (default: ini-file)", default=-1, type=int)
    parser.add_argument("-t", "--time", help="chose MillePedeUser_X Tree (default: ini-file)", default=-1, type=int)
    parser.add_argument("-i", "--ini", help="specify a ini file", default="-1")
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
    
    ## create output directories
    if not os.path.exists("{0}/plots/pdf".format(config.outputPath)):
        os.makedirs("{0}/plots/pdf".format(config.outputPath))
    if not os.path.exists("{0}/plots/png".format(config.outputPath)):
        os.makedirs("{0}/plots/png".format(config.outputPath))
        
    # parse the file pede.dump.gz and return a LogData Object
    pedeDump = parse("{0}/pede.dump.gz".format(config.jobDataPath), config)
    
    # TODO check if there is a file and a TTree
    # open root file and get TTree MillePedeUser_X
    treeFile = TFile("{0}/treeFile_merge.root".format(config.jobDataPath))
    MillePedeUser = treeFile.Get("MillePedeUser_{0}".format(config.jobTime))
    
    
    ##########################################################################
    # time dependend big structures
    #
    
    

    for mode in ["xyz", "rot"]:
        # create the histogram data
        timeStructure.plot(treeFile, geometryGetter, mode, config)

    
    ##########################################################################
    # big structures
    #
    
    big = bigStructure.plot(MillePedeUser, geometryGetter,  config)
    
    ##########################################################################
    # modules of a hole structure
    # and part of structure
    #
    
    bigModule.plot(MillePedeUser, geometryGetter, config)
    
    ##########################################################################
    # create TEX, beamer
    #
    
    pdfCreator.create(pedeDump, config.latexfile, config)
    beamerCreator.create(pedeDump, "beamer.tex", config)
    
if __name__ == "__main__":
    main()
