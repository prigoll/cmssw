#!/usr/bin/env python

##########################################################################
##
##  Set the style of the output
##

from ROOT import TPaveText

######################################################################
# creates the identification text in the top left corner
#

def identification(config):
    text = TPaveText(0.0, 0.95, 1.0, 1.0, "blNDC")
    text.AddText(config.message)
    text.SetBorderSize(0)
    text.SetTextAlign(12)
    text.SetTextSizePixels(10)
    text.SetTextFont(82)
    text.SetFillColor(0)
    return text