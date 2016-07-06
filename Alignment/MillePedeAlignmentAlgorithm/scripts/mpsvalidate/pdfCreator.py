#!/usr/bin/env python

##########################################################################
# Creates pdf out of the histograms, parsed data and a given template.
##

import os
import string

from mpsvalidate.classes import LogData, MonitorData
from mpsvalidate.geometry import Alignables, Structure


# create class to have delimiter %% which is not used in latex


class TexTemplate(string.Template):
    delimiter = "%%"


def create(alignables, pedeDump, outputFile, config):

    # load template
    with open("./mpsvalidate/tex_template.tex", "r") as template:
        data = template.read()
        template.close()

    # create object where data could be substituted
    data = TexTemplate(data)

    # output string
    out = ""

    # general information

    out += "\section{{General information}}\n"

    if (config.message):
        out += "Project: {{{0}}}\n".format(config.message)

    # pede.dump.gz

    out += "\section{{Pede monitoring information}}\n"
    if (pedeDump.sumValue != 0):
        out += r"\begin{{align*}}Sum(Chi^2)/Sum(Ndf) &= {0}\\ &= {1}\end{{align*}}".format(
            pedeDump.sumSteps, pedeDump.sumValue)
    else:
        out += r"\begin{{align*}}Sum(W*Chi^2)/Sum(Ndf)/<W> &= {0}\\ &= {1}\end{{align*}}".format(
            pedeDump.sumSteps, pedeDump.sumWValue)
    out += r"with correction for down-weighting: {0}\\".format(
        pedeDump.correction)
    out += r"Peak dynamic memory allocation: {0} GB\\".format(pedeDump.memory)
    out += r"Total time: {0} h {1} m {2} s\\".format(
        pedeDump.time[0], pedeDump.time[1], pedeDump.time[2])
    out += r"Number of records: {0}\\".format(pedeDump.nrec)
    out += r"Total number of parameters: {0}\\".format(pedeDump.ntgb)
    out += r"Number of variable parameters: {0}\\".format(pedeDump.nvgb)
    out += r"Warning:\\"
    for line in pedeDump.warning:

        # check if line empty
        if line.replace(r" ", r""):
            out += "\\begin{verbatim}"
            out += line
            out += "\\end{verbatim}\n"

    out += "\section{{Parameter plots}}\n"

    # high level structures

    big = [x for x in config.outputList if (x.plottype == "big")]

    if big:
        out += "\subsection{{High-level parameters}}\n"
        for i in big:
            out += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(
                config.outputPath, i.filename)

    # time (IOV) dependent plots

    time = [x for x in config.outputList if (x.plottype == "time")]

    if time:
        out += "\subsection{{High-level parameters versus time (IOV)}}\n"
        # get list with names of the structures
        for structure in [x.name for x in time if x.parameter == "xyz"]:
            out += "\subsubsection{{{0}}}\n".format(structure)
            for mode in ["xyz", "rot"]:
                filename = [x.filename for x in time if (
                    x.parameter == mode and x.name == structure)][0]
                out += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(
                    config.outputPath, filename)

    # hole modules

    # check if there are module plots
    if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "")):
        out += "\subsection{{Module-level parameters}}\n"

        # loop over all structures
        for moduleName in [x.name for x in alignables.structures]:

            # check if there is a plot for this module
            if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "" and x.name == moduleName)):
                out += "\subsubsection{{{0}}}\n".format(moduleName)
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
                        out += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(
                            config.outputPath, module[0].filename)

                        # loop over submodules
                        for plot in moduleSub:
                            out += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(
                                config.outputPath, plot.filename)

    # table of input files with number of tracks
    out += "\section{Datasets with tracks}\n"
    out += """\\begin{table}
        \centering
        \caption{Datasets with tracks}
        \\begin{tabular}{cc}
        \hline
        Dataset & Number of used tracks \\\\
        \hline \n"""
    for monitor in MonitorData.monitors:
        out += "{0} & {1}\\\\\n".format(monitor.name, monitor.ntracks)
    out += """\hline
              \end{tabular}\n
              \end{table}"""

    # plot taken from the millePedeMonitor_merge.root file

    if any(x for x in config.outputList if x.plottype == "monitor"):
        out += "\section{{Monitor plots}}\n"

        lastdataset = ""
        for plot in [x for x in config.outputList if x.plottype == "monitor"]:
            # all plots of a dataset together in one section
            if (lastdataset != plot.name):
                out += "\subsection{{{0}}}".format(plot.name)
            lastdataset = plot.name
            out += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(
                config.outputPath, plot.filename)

    data = data.substitute(out=out)

    with open("{0}/{1}".format(config.outputPath, outputFile), "w") as output:
        output.write(data)
        output.close()

    # TODO run pdflatex
    for i in range(2):
        os.system("pdflatex -output-directory={0}  {1}/{2}".format(
            config.outputPath, config.outputPath, outputFile))
