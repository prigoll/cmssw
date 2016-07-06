#!/usr/bin/env python

##########################################################################
# Parse the alignment_merge.py file for additional information
#

from mpsvalidate.classes import AdditionalData


def parse(config, path):
    additionalData = AdditionalData()

    # third arugments
    selectorRigidTag = []
    selectorBowedTag = []
    selectorTwoBowedTag = []

    # open aligment_merge.py file
    with open(path) as inputFile:
        mergeFile = inputFile.readlines()

    # search pattern
    pattern = {
        "process.AlignmentProducer.ParameterBuilder.SelectorRigid = cms.PSet(": [additionalData.selectorRigid, selectorRigidTag, additionalData.selectorRigidThird],
        "process.AlignmentProducer.ParameterBuilder.SelectorBowed = cms.PSet(": [additionalData.selectorBowed,
                                                                                 selectorBowedTag, additionalData.selectorBowedThird],
        "process.AlignmentProducer.ParameterBuilder.SelectorTwoBowed = cms.PSet(": [additionalData.selectorTwoBowed, selectorTwoBowedTag, additionalData.selectorTwoBowedThird]
    }

    # loop over lines
    for index, line in enumerate(mergeFile):

        # search for SelectorRigid, SelectorBowed and SelectorTwoBowed
        for string in pattern:
            if ("#" not in line and string in line):
                # extract data
                for lineNumber in range(index + 2, index + 8):
                    # break at the end of the SelectorRigid
                    if (")" in mergeFile[lineNumber]):
                        break
                    pattern[string][0].append(
                        mergeFile[lineNumber].strip("', \n").split(","))
                    # check if third argument
                    if (len(pattern[string][0][-1]) > 2):
                        pattern[string][1].append(
                            pattern[string][0][-1][2])
            # check for third arguments
            if ("'" not in line):
                for tag in pattern[string][1]:
                    if tag in line:
                        pattern[string][2].append(line.strip(" \n"))

        # search for pedeSteererMethod
        if ("process.AlignmentProducer.algoConfig.pedeSteerer.method" in line):
            additionalData.pedeSteererMethod = line.split("'")[1]

        # search for pedeSteererOptions
        if ("process.AlignmentProducer.algoConfig.pedeSteerer.options" in line):
            for lineNumber in range(index + 1, index + 15):
                if ("]" in mergeFile[lineNumber]):
                    break
                additionalData.pedeSteererOptions.append(mergeFile[lineNumber].strip("', \n"))

        # search for pedeSteererpedeCommand
        if ("process.AlignmentProducer.algoConfig.pedeSteerer.pedeCommand" in line):
            additionalData.pedeSteererpedeCommand = line.split("'")[1]

    return additionalData
