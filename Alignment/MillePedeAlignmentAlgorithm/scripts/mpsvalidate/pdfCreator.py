#!/usr/bin/env python

##########################################################################
##  Creates pdf out of the histograms, parsed data and a given template.
##

from mpsvalidate.classes import LogData, GeometryGetter

import os
import string

# create class to have delimiter %% which is not used in latex
class TexTemplate(string.Template):
    delimiter = "%%"
    

def create(outputFile, config):
    
    # load template
    with open("./mpsvalidate/tex_template.tex", "r") as template:
        data = template.read()
        template.close()
    
    # create object where data could be substituted
    data = TexTemplate(data)
    
    # output string
    out = ""


    # big Structures
    
    big = [x for x in config.outputList if (x.plottype == "big")]
    
    if big:
        out += "\section{{Big structures}}\n"
        for i in big:
            out += "\subsection{{{0}}}\n".format(i.parameter)
            out += "\includegraphics[width=\linewidth]{{{0}/plots/{1}}}\n".format(config.outputPath, i.filename)
            

    # hole modules
    
    # check if there are module plots
    if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "")):
        out += "\section{{Modules}}\n"
        
        # loop over all structures
        for moduleName in GeometryGetter.namebStruct:
            
            # check if there is a plot for this module
            if any(x for x in config.outputList if (x.plottype == "mod" and x.number == "" and x.name == moduleName)):
                out += "\subsection{{{0}}}\n".format(moduleName)
                
                # loop over modes
                for mode in ["xyz", "rot", "dist"]:
                    
                    
                    # get module plot
                    module = [x for x in config.outputList if (x.plottype == "mod" and x.number == "" and x.name == moduleName and x.parameter==mode)]
                    # get list of sub module plots
                    moduleSub = [x for x in config.outputList if (x.plottype == "subMod" and x.number != "" and x.name == moduleName and x.parameter==mode)]
                
                    # check if plot there is a plot in this mode
                    if module:
                        out += "\subsubsection{{{0}}}\n".format(mode)
                        out += "\includegraphics[width=\linewidth]{{{0}/plots/{1}}}\n".format(config.outputPath, module[0].filename)
                        
                        # loop over submodules
                        for plot in moduleSub:
                            out += "\includegraphics[width=\linewidth]{{{0}/plots/{1}}}\n".format(config.outputPath, plot.filename)

    
    data = data.substitute(out=out)
    
    # TODO path
    with open("{0}/{1}".format(config.outputPath, outputFile), "w") as output:
        output.write(data)
        output.close()
    
    # TODO run pdflatex
    os.system("pdflatex -output-directory={0}  {1}/{2}".format(config.outputPath, config.outputPath, outputFile) )
    

if __name__ == "__main__":
    create("tex_template.tex", "aaaa.tex", "asdf")