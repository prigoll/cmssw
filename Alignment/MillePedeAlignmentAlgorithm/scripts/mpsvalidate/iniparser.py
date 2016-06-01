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
        # jobmX dir
        self.jobNumber = -1
        # MillePedeUser_X time
        self.jobTime = -1
        # ./jobData/jobmX path
        self.jobDataPath = ""
        # base outputpath
        self.outputPath = ""
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
            self.allowhidden = int(parser.get("PLOTS","allowhidden"))
        except:
            pass
        
        try:
            self.numberofbins = int(parser.get("PLOTS","numberofbins"))
        except:
            pass
        
        try:
            self.defpeak = int(parser.get("PLOTS","defpeak"))
        except:
            pass
        
        try:
            self.widthstddev = int(parser.get("PLOTS","widthstddev"))
        except:
            pass
        
        try:
            self.forcestddev = int(parser.get("PLOTS","forcestddev"))
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
