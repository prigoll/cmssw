#!/usr/bin/env python

##########################################################################

# Read the ini data which is passed to the function and return the
# data as a configData object. If a parameter is given the function
# parseParameter will override the config values.
##

import ConfigParser
import logging


class ConfigData:
    """ stores the config data of the ini files or the console parameters
    """

    def __init__(self):
        # General
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
        # identification in every plot (e.g. mp1885)
        self.message = ""
        # limits for warning dict with keys xyz, rot, dist
        # arguments must be given in this order
        self.limit = {}
        # statboxsize
        self.statboxsize = -1

        # what should be created
        self.showmonitor = -1
        self.showadditional = -1
        self.showdump = -1
        self.showtime = -1
        self.showhighlevel = -1
        self.showmodule = -1
        self.showsubmodule = -1
        self.showtex = -1
        self.showbeamer = -1
        self.showhtml = -1

        # MODULEPLOTS
        # number of bins after shrinking
        self.numberofbins = -1
        # definition of sharp peak; max_outlier / StdDev > X
        self.defpeak = -1
        # new histogram width in units of StdDev
        self.widthstddev = -1
        # every parameter (e.g. xyz) with same range
        self.samerange = -1
        # rangemode "stddev" = multiple of StdDev, "all" = show all, "given" =
        # use given ranges
        self.rangemode = -1
        # ranges
        self.rangexyzM = []
        self.rangerotM = []
        self.rangedistM = []

        # HIGHLEVELPLOTS
        # given ranges
        self.rangexyzHL = []
        self.rangerotHL = []
        # every parameter (e.g. xyz) with same range
        self.samerangeHL = -1
        # rangemode "all" = show all, "given" = use given ranges
        self.rangemodeHL = -1

        # Time dependent
        self.firsttree = -1

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
            configBuffer.jobNumber = int(parser.get("GENERAL", "job"))
        except:
            pass

        try:
            configBuffer.jobDataPath = parser.get("GENERAL", "jobdatapath")
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

        # set outputpath
        try:
            self.outputPath = parser.get("GENERAL", "outputpath")
        except:
            pass

        if (self.outputPath == ""):
            self.outputPath = self.jobDataPath + "/validation_output"

        # data which could be stored directly
        try:
            self.jobTime = int(parser.get("GENERAL", "time"))
        except:
            pass

        try:
            self.latexfile = parser.get("GENERAL", "latexfile")
        except:
            pass

        try:
            self.limit = parser.get("GENERAL", "limit")
            self.limit = map(float, self.limit.replace(" ", "").split(","))
            # make a dict to lookup by mode
            self.limit = dict(zip(["xyz", "rot", "dist"], self.limit))
        except:
            pass

        try:
            self.statboxsize = float(parser.get("GENERAL", "statboxsize"))
        except:
            pass

        # MODULEPLOTS

        try:
            self.numberofbins = int(parser.get("MODULEPLOTS", "numberofbins"))
        except:
            pass

        try:
            self.defpeak = int(parser.get("MODULEPLOTS", "defpeak"))
        except:
            pass

        try:
            self.widthstddev = int(parser.get("MODULEPLOTS", "widthstddev"))
        except:
            pass

        try:
            self.samerange = int(parser.get("MODULEPLOTS", "samerange"))
        except:
            pass

        try:
            self.rangemode = parser.get("MODULEPLOTS", "rangemode")
        except:
            pass

        try:
            self.rangexyzM = parser.get("MODULEPLOTS", "rangexyz")
            self.rangexyzM = sorted(
                map(float, self.rangexyzM.replace(" ", "").split(",")))
        except:
            pass

        try:
            self.rangerotM = parser.get("MODULEPLOTS", "rangerot")
            self.rangerotM = sorted(
                map(float, self.rangerotM.replace(" ", "").split(",")))
        except:
            pass

        try:
            self.rangedistM = parser.get("MODULEPLOTS", "rangedist")
            self.rangedistM = sorted(
                map(float, self.rangedistM.replace(" ", "").split(",")))
        except:
            pass

        # HIGHLEVELPLOTS

        try:
            self.rangexyzHL = parser.get("HIGHLEVELPLOTS", "rangexyz")
            self.rangexyzHL = sorted(
                map(float, self.rangexyzHL.replace(" ", "").split(",")))
        except:
            pass

        try:
            self.rangerotHL = parser.get("HIGHLEVELPLOTS", "rangerot")
            self.rangerotHL = sorted(
                map(float, self.rangerotHL.replace(" ", "").split(",")))
        except:
            pass

        try:
            self.samerangeHL = int(parser.get("HIGHLEVELPLOTS", "samerange"))
        except:
            pass

        try:
            self.rangemodeHL = parser.get("HIGHLEVELPLOTS", "rangemode")
        except:
            pass

        # TIMEPLOTS

        try:
            self.firsttree = int(parser.get("TIMEPLOTS", "firsttree"))
        except:
            pass

        # SHOW

        try:
            self.showmonitor = int(parser.get("SHOW", "showmonitor"))
        except:
            pass

        try:
            self.showadditional = int(parser.get("SHOW", "showadditional"))
        except:
            pass

        try:
            self.showdump = int(parser.get("SHOW", "showdump"))
        except:
            pass

        try:
            self.showtime = int(parser.get("SHOW", "showtime"))
        except:
            pass

        try:
            self.showhighlevel = int(parser.get("SHOW", "showhighlevel"))
        except:
            pass

        try:
            self.showmodule = int(parser.get("SHOW", "showmodule"))
        except:
            pass

        try:
            self.showsubmodule = int(parser.get("SHOW", "showsubmodule"))
        except:
            pass

        try:
            self.showtex = int(parser.get("SHOW", "showtex"))
        except:
            pass

        try:
            self.showbeamer = int(parser.get("SHOW", "showbeamer"))
        except:
            pass

        try:
            self.showhtml = int(parser.get("SHOW", "showhtml"))
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

        if (args.message != ""):
            self.message = args.message
