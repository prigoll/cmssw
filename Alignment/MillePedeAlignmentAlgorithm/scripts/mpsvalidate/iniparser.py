#!/usr/bin/env python

##########################################################################

##  Read the ini data which is passed to the function and return the
##  data as a configData object. If a parameter is given the function
##  parseParameter will override the config values.
##

import ConfigParser
import logging

class ConfigData:
    """ stores the config data of the ini files or the console parameters
    """
    
    def __init__(self):
        ## General
        # jobmX dir
        self.jobNumber = -1
        # MillePedeUser_X time
        self.jobTime = -1
        # ./jobData/jobmX path
        self.jobDataPath = ""
        # base outputpath
        self.outputPath = ""
        # latex file name
        self.latexfile = ""
        
        ## MODULEPLOTS
        # allow to use the standard deviation as the plotrange
        self.allowhidden = -1
        # number of bins after shrinking
        self.numberofbins = -1
        # definition of sharp peak; max_outlier / StdDev > X
        self.defpeak = -1
        # new histogram width in units of StdDev
        self.widthstddev = -1
        # force to use histogram width self.widthstdev * StdDev
        self.forcestddev = -1
        # every parameter (e.g. xyz) with same range
        self.samerange = -1
        # rangemode 1 = multiple of StdDev, 2 = show all, 3 = use given ranges
        self.rangemode = -1
        
        ## HIGHLEVELPLOTS
        # given ranges
        self.rangexyzHL = []
        self.rangerotHL = []
        # every parameter (e.g. xyz) with same range
        self.samerangeHL = -1
        # rangemode 1 = show all, 2 = use given ranges
        self.rangemodeHL = -1
        
        
        # list with the plots for the output
        self.outputList = []

    def parseConfig(self, path):
        # create ConfigParser object
        parser = ConfigParser.ConfigParser()
        
        # read ini file
        if (parser.read(path) == []):
            logging.error("Could not open ini-file: {0}".format(path))
        
        # buffer object
        configBuffer = ConfigData()
        
        
        # collect data and process it
        try:
            configBuffer.jobNumber = int(parser.get("GENERAL","job"))
        except:
            pass
        
        try:
            configBuffer.jobDataPath = parser.get("GENERAL","jobdatapath")
        except:
            pass
        
        # set jobDataPath if job number is given and if path is not given
        if (configBuffer.jobNumber != -1 and configBuffer.jobDataPath == ""):
            self.jobNumber = configBuffer.jobNumber
            if (self.jobNumber == 0):
                self.jobDataPath = ".jobData/jobm"
            else:
                self.jobDataPath = "./jobData/jobm{0}".format(self.jobNumber)
        
        # if jobData path is given
        if (configBuffer.jobDataPath != ""):
            self.jobDataPath = configBuffer.jobDataPath
        
        
        # data which could be stored directly
        try:
            self.jobTime = int(parser.get("GENERAL","time"))
        except:
            pass    
        
        try:
            self.outputPath = parser.get("GENERAL","outputpath")
        except:
            pass
        
        try:
            self.latexfile = parser.get("GENERAL","latexfile")
        except:
            pass
        
        ## MODULEPLOTS        
        try:
            self.allowhidden = int(parser.get("MODULEPLOTS","allowhidden"))
        except:
            pass
        
        try:
            self.numberofbins = int(parser.get("MODULEPLOTS","numberofbins"))
        except:
            pass
        
        try:
            self.defpeak = int(parser.get("MODULEPLOTS","defpeak"))
        except:
            pass
        
        try:
            self.widthstddev = int(parser.get("MODULEPLOTS","widthstddev"))
        except:
            pass
        
        try:
            self.forcestddev = int(parser.get("MODULEPLOTS","forcestddev"))
        except:
            pass
        
        try:
            self.samerange = int(parser.get("MODULEPLOTS","samerange"))
        except:
            pass
        
        try:
            self.rangemode = int(parser.get("MODULEPLOTS","rangemode"))
        except:
            pass
        
        ## HIGHLEVELPLOTS
        
        try:
            self.rangexyzHL = parser.get("HIGHLEVELPLOTS","rangexyz")
            self.rangexyzHL = sorted(map(float,self.rangexyzHL.replace(" ", "").split(",")))
        except:
            pass
        
        try:
            self.rangerotHL = parser.get("HIGHLEVELPLOTS","rangerot")
            self.rangerotHL = sorted(map(float,self.rangerotHL.replace(" ", "").split(",")))
        except:
            pass
        
        try:
            self.samerangeHL = int(parser.get("HIGHLEVELPLOTS","samerange"))
        except:
            pass
        
        try:
            self.rangemodeHL = int(parser.get("HIGHLEVELPLOTS","rangemode"))
        except:
            pass
        

    def parseParameter(self, args):
        # check if parameter is given and override the config data
        if (args.time != -1):
            self.jobTime = args.time
            
        if (args.job != -1):
            self.jobNumber = args.job
            
            # set jobDataPath
            if (self.jobNumber == 0):
                self.jobDataPath = ".jobData/jobm"
            else:
                self.jobDataPath = "./jobData/jobm{0}".format(self.jobNumber)
