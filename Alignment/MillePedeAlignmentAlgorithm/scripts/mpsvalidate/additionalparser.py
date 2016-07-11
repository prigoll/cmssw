#!/usr/bin/env python

##########################################################################
# Parse the alignment_merge.py file for additional information
#


class AdditionalData:
    """ stores the additional information of the alignment_merge.py file
    """

    def __init__(self):
        self.pedeSteererMethod = ""
        self.pedeSteererOptions = []
        self.pedeSteererCommand = ""

        # safe the selector information Rigid, Bowed, TwoBowed
        self.selector = [[] for x in range(3)]
        self.selectorTag = [[] for x in range(3)]
        self.selectorThird = [[] for x in range(3)]

        # string to find the information and variables where to safe the
        # information (searchstring: [selector list, seletor tag, third element,
        # name])
        self.pattern = {
            "process.AlignmentProducer.ParameterBuilder.SelectorRigid = cms.PSet(": [self.selector[0], self.selectorTag[0], self.selectorThird[0], "SelectorRigid"],
            "process.AlignmentProducer.ParameterBuilder.SelectorBowed = cms.PSet(": [self.selector[1], self.selectorTag[1], self.selectorThird[1], "SelectorBowed"],
            "process.AlignmentProducer.ParameterBuilder.SelectorTwoBowed = cms.PSet(": [self.selector[2], self.selectorTag[2], self.selectorThird[2], "SelectorTwoBowed"]
        }

    def parse(self, config, path):

        # open aligment_merge.py file
        with open(path) as inputFile:
            mergeFile = inputFile.readlines()

        # search pattern

        # loop over lines
        for index, line in enumerate(mergeFile):

            # search for SelectorRigid, SelectorBowed and SelectorTwoBowed
            for string in self.pattern:
                if ("#" not in line and string in line):
                    # extract data
                    for lineNumber in range(index + 2, index + 8):
                        # break at the end of the SelectorRigid
                        if (")" in mergeFile[lineNumber]):
                            break
                        self.pattern[string][0].append(
                            mergeFile[lineNumber].strip("', \n").split(","))
                        # check if third argument
                        if (len(self.pattern[string][0][-1]) > 2):
                            self.pattern[string][1].append(
                                self.pattern[string][0][-1][2])
                # check for third arguments
                if ("'" not in line):
                    for tag in self.pattern[string][1]:
                        if tag in line:
                            self.pattern[string][2].append(line.strip(" \n"))

            # search for pedeSteererMethod
            if ("process.AlignmentProducer.algoConfig.pedeSteerer.method" in line and "#" not in line):
                self.pedeSteererMethod = line.split("'")[1]

            # search for pedeSteererOptions
            if ("process.AlignmentProducer.algoConfig.pedeSteerer.options" in line and "#" not in line):
                for lineNumber in range(index + 1, index + 15):
                    if ("]" in mergeFile[lineNumber]):
                        break
                    self.pedeSteererOptions.append(
                        mergeFile[lineNumber].strip("', \n"))

            # search for pedeSteererCommand
            if ("process.AlignmentProducer.algoConfig.pedeSteerer.pedeCommand" in line and "#" not in line):
                self.pedeSteererCommand = line.split("'")[1]
