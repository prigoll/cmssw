#!/usr/bin/env python

##########################################################################
# Parse the pede.dump.gz file and returns a LogData object with the
# parsed information of the file.
##

import gzip
import re

from mpsvalidate.classes import LogData


def parse(path, config):
    # parse pede.dump.gz

    logData = LogData()

    # only recognize warning the first time
    warningBool = False

    # save lines in list
    with gzip.open(path) as gzipFile:
        dumpFile = gzipFile.readlines()

    for i, line in enumerate(dumpFile):
        # Sum(Chi^2)/Sum(Ndf)
        if ("Sum(Chi^2)/Sum(Ndf) =" in line):
            number = []
            number.append(map(float, re.findall(
                r"[-+]?\d*\.\d+", dumpFile[i])))
            number.append(map(int, re.findall(r"[-+]?\d+", dumpFile[i + 1])))
            number.append(map(float, re.findall(
                r"[-+]?\d*\.\d+", dumpFile[i + 2])))
            logData.sumSteps = "{0} / ( {1} - {2} )".format(
                number[0][0], number[1][0], number[1][1])
            logData.sumValue = number[2][0]

        # Sum(W*Chi^2)/Sum(Ndf)/<W>
        if ("Sum(W*Chi^2)/Sum(Ndf)/<W> =" in line):
            number = []
            number.append(map(float, re.findall(
                r"[-+]?\d*\.\d+", dumpFile[i])))
            number.append(map(int, re.findall(r"[-+]?\d+", dumpFile[i + 1])))
            number.append(map(float, re.findall(
                r"[-+]?\d*\.\d+", dumpFile[i + 2])))
            number.append(map(float, re.findall(
                r"[-+]?\d*\.\d+", dumpFile[i + 3])))
            logData.sumSteps = "{0} / ( {1} - {2} ) / {3}".format(
                number[0][0], number[1][0], number[1][1], number[2][0])
            logData.sumWValue = number[3][0]

        if ("with correction for down-weighting" in line):
            number = map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i]))
            logData.correction = number[0]

        # Peak dynamic memory allocation
        if ("Peak dynamic memory allocation:" in line):
            number = map(float, re.findall(r"[-+]?\d*\.\d+", dumpFile[i]))
            logData.memory = number[0]

        # total time
        if ("Iteration-end" in line):
            number = map(int, re.findall(r"\d+", dumpFile[i + 1]))
            logData.time = number[:3]

        # warings
        if ("WarningWarningWarningWarning" in line and warningBool == False):
            warningBool = True
            j = i + 8
            while ("Warning" not in dumpFile[j]):
                logData.warning.append(dumpFile[j])
                j += 1

        # nrec number of records
        if (" = number of records" in line):
            number = map(int, re.findall("\d+", dumpFile[i]))
            logData.nrec = number[0]

        # ntgb total number of parameters
        if (" = total number of parameters" in line):
            number = map(int, re.findall("\d+", dumpFile[i]))
            logData.ntgb = number[0]

        # nvgb number of variable parameters
        if (" = number of variable parameters" in line):
            number = map(int, re.findall("\d+", dumpFile[i]))
            logData.nvgb = number[0]

    return logData
