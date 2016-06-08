#!/usr/bin/env python

##########################################################################
##  Creates beamer out of the histograms, parsed data and a given template.
##

from mpsvalidate.classes import LogData, GeometryGetter

import os
import string

# create class to have delimiter %% which is not used in latex
class TexTemplate(string.Template):
    delimiter = "%%"
    
class Out:
    def __init__(self):
        self.text = ""
    
    def addSlide(self, head, text):
        self.text += "\\begin{{frame}}[t]{{{0}}}\n".format(head)
        self.text += text
        self.text += "\\end{frame}\n"
        
    def addFragileSlide(self, head, text):
        self.text += "\\begin{{frame}}[fragile=singleslide]{{{0}}}\n".format(head)
        self.text += text
        self.text += "\\end{frame}\n"
        

def create(pedeDump, outputFile, config):
    
    # load template
    with open("./mpsvalidate/beamer_template.tex", "r") as template:
        data = template.read()
        template.close()
    
    # create object where data could be substituted
    data = TexTemplate(data)
    
    # output string
    out = Out()
        
    # pede.dump.gz
    if (pedeDump.sumValue != 0):
        text = r"\begin{{align*}}Sum(Chi^2)/Sum(Ndf) &= {0}\\ &= {1}\end{{align*}}".format(pedeDump.sumSteps, pedeDump.sumValue)
    else:
        text = r"\begin{{align*}}Sum(W*Chi^2)/Sum(Ndf)/<W> &= {0}\\ &= {1}\end{{align*}}".format(pedeDump.sumSteps, pedeDump.sumWValue)
    text += r"with correction for down-weighting: {0}\\".format(pedeDump.correction)
    text += r"Peak dynamic memory allocation: {0} GB\\".format(pedeDump.memory)
    text += r"Total time: {0} h {1} m {2} s\\".format(pedeDump.time[0], pedeDump.time[1], pedeDump.time[2])
    text += r"Number of records: {0}\\".format(pedeDump.nrec)
    text += r"Total number of parameters: {0}\\".format(pedeDump.ntgb)
    text += r"Number of variable parameters: {0}\\".format(pedeDump.nvgb)
    out.addSlide("pede.dump.gz", text)
    
    text = r"Warning:\\"
    for line in pedeDump.warning:
        
        # check if line empty
        if line.replace(r" ", r""):
            text += "\\begin{verbatim}"
            text += line
            text += "\\end{verbatim}\n"
    
    out.addFragileSlide("Warning", text)


    # humanreadable names
    names = {"xyz": "Translation", "rot": "Rotation", "dist": "Deformation"}

    # big Structures
    
    big = [x for x in config.outputList if (x.plottype == "big")]
    

    for i in big:
        text = "\\framesubtitle{{{0}}}\n".format(names[i.parameter])
        text += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(config.outputPath, i.filename)
        
        out.addSlide("High level structures", text)
            

    # hole modules
    
    # check if there are module plots
    if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "")):
        
        # loop over all structures
        for moduleName in GeometryGetter.namebStruct:
            
            # check if there is a plot for this module
            if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "" and x.name == moduleName)):
                
                # loop over modes
                for mode in ["xyz", "rot", "dist"]:
                    
                    
                    # get module plot
                    module = [x for x in config.outputList if (x.plottype == "mod" and x.number == "" and x.name == moduleName and x.parameter==mode)]
                    # get list of sub module plots
                    moduleSub = [x for x in config.outputList if (x.plottype == "subMod" and x.number != "" and x.name == moduleName and x.parameter==mode)]
                
                    # check if plot there is a plot in this mode
                    if module:
                        text = "\\framesubtitle{{{0}}}\n".format(moduleName+" "+names[mode])
                        text += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(config.outputPath, module[0].filename)
                        
                        out.addSlide("Modules", text)
                        
                        # loop over submodules
                        for plot in moduleSub:
                            text = "\\framesubtitle{{{0}}}\n".format(moduleName+str(plot.number)+" "+names[mode])
                            text += "\includegraphics[width=\linewidth]{{{0}/plots/pdf/{1}.pdf}}\n".format(config.outputPath, plot.filename)
                            
                            out.addSlide("Modules", text)

    
    data = data.substitute(out=out.text)
    
    # TODO path
    with open("{0}/{1}".format(config.outputPath, outputFile), "w") as output:
        output.write(data)
        output.close()
    
    # TODO run pdflatex
    os.system("pdflatex -output-directory={0}  {1}/{2}".format(config.outputPath, config.outputPath, outputFile) )
