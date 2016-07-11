#!/usr/bin/env python

##########################################################################
# Creates html out of the histograms, parsed data and a given template.
##

import os
import string

from Alignment.MillePedeAlignmentAlgorithm.mpsvalidateclasses import PedeDumpData
from Alignment.MillePedeAlignmentAlgorithm.mpsvalidategeometry import Alignables, Structure


# create class to have delimiter %% which is not used in latex


class TexTemplate(string.Template):
    delimiter = "%%"


def create(alignables, pedeDump, outputFile, config):

    # load template
    with open("./mpsvalidate/html_template.html", "r") as template:
        data = template.read()
        template.close()

    # create object where data could be substituted
    data = TexTemplate(data)

    # output string
    out = ""

    # general information

    out += "<h1>General information</h1>\n"

    if (config.message):
        out += "Project: {0}\n".format(config.message)

    # pede.dump.gz

    out += "<h1>Pede monitoring information</h1>\n"
    if (pedeDump.sumValue != 0):
        out += r"Sum(Chi^2)/Sum(Ndf) &= {0}<br> &= {1}".format(
            pedeDump.sumSteps, pedeDump.sumValue)
    else:
        out += r"Sum(W*Chi^2)/Sum(Ndf)/<W> &= {0}<br> &= {1}".format(
            pedeDump.sumSteps, pedeDump.sumWValue)
    out += r"with correction for down-weighting: {0}<br>".format(
        pedeDump.correction)
    out += r"Peak dynamic memory allocation: {0} GB<br>".format(
        pedeDump.memory)
    out += r"Total time: {0} h {1} m {2} s<br>".format(
        pedeDump.time[0], pedeDump.time[1], pedeDump.time[2])
    out += r"Number of records: {0}<br>".format(pedeDump.nrec)
    out += r"Total number of parameters: {0}<br>".format(pedeDump.ntgb)
    out += r"Number of variable parameters: {0}<br>".format(pedeDump.nvgb)
    out += r"Warning:<br>"
    for line in pedeDump.warning:

        # check if line empty
        if line.replace(r" ", r""):
            out += line

    # high level structures

    big = [x for x in config.outputList if (x.plottype == "big")]

    if big:
        out += "<h1>High-level parameters</h1>\n"
        for i in big:
            out += "<a href='plots/pdf/{0}.pdf'><img src='plots/png/{0}.png'></a>\n".format(
                i.filename)

    # time (IOV) dependent plots

    time = [x for x in config.outputList if (x.plottype == "time")]

    if time:
        out += "<h1>High-level parameters versus time (IOV)</h1>\n"
        # get list with names of the structures
        for structure in [x.name for x in time if x.parameter == "xyz"]:
            out += "<h2>{0}<h2>\n".format(structure)
            for mode in ["xyz", "rot"]:
                filename = [x.filename for x in time if (
                    x.parameter == mode and x.name == structure)][0]
                out += "<a href='plots/pdf/{0}.pdf'><img src='plots/png/{0}.png'></a>\n".format(
                    filename)

    # hole modules

    # check if there are module plots
    if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "")):
        out += "<h1>Module-level parameters</h1>\n"

        # loop over all structures
        for moduleName in [x.name for x in alignables.structures]:

            # check if there is a plot for this module
            if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "" and x.name == moduleName)):
                out += "<h2>{0}</h2>\n".format(moduleName)

                # loop over modes
                for mode in ["xyz", "rot", "dist"]:

                    # get module plot
                    module = [x for x in config.outputList if (
                        x.plottype == "mod" and x.number == "" and x.name == moduleName and x.parameter == mode)]
                    # get list of sub module plots
                    moduleSub = [x for x in config.outputList if (
                        x.plottype == "subMod" and x.number != "" and x.name == moduleName and x.parameter == mode)]

                    # check if plot there is a plot in this mode
                    if module:
                        out += "<a href='plots/pdf/{0}.pdf'><img src='plots/png/{0}.png'></a>\n".format(module[
                                                                                                        0].filename)

                        # loop over submodules
                        for plot in moduleSub:
                            out += "<a href='plots/pdf/{0}.pdf'><img src='plots/png/{0}.png'></a>\n".format(
                                plot.filename)

    # plot taken from the millePedeMonitor_merge.root file

    if any(x for x in config.outputList if x.plottype == "monitor"):
        out += "<h1>Monitor</h1>\n"
        for plot in [x for x in config.outputList if x.plottype == "monitor"]:
            out += "<h3>{0}</h3>\n".format(plot.name)
            out += "<a href='plots/pdf/{0}.pdf'><img src='plots/png/{0}.png'></a>\n".format(
                plot.filename)

    data = data.substitute(message=config.message, out=out)

    with open("{0}/{1}".format(config.outputPath, outputFile), "w") as output:
        output.write(data)
        output.close()
