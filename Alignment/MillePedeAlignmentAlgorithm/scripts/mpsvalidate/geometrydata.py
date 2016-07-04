#!/usr/bin/env python

##########################################################################
# Geometry data
##

class GeometryData:
    """ Class which holds the geometry data of a ObjId
    """

    def __init__(self, name, discriminator, number_per_disicriminator):
        self.name = name
        self.discriminator = discriminator
        self.number_per_disicriminator = number_per_disicriminator


data = {-1: GeometryData("notfound", [], []),
        0: GeometryData("invalid", [], []),
        1: GeometryData("AlignableDetUnit", [], []),
        2: GeometryData("AlignableDet", [], []),
        3: GeometryData("TPBModule", [], []),
        4: GeometryData("TPBLadder", [], []),
        5: GeometryData("TPBLayer", [], []),
        6: GeometryData("TPBHalfBarrel", [], []),
        7: GeometryData("TPBBarrel", [], []),
        8: GeometryData("TPEModule", [], []),
        9: GeometryData("TPEPanel", [], []),
        10: GeometryData("TPEBlade", [], []),
        11: GeometryData("TPEHalfDisk", [], []),
        12: GeometryData("TPEHalfCylind", [], []),
        13: GeometryData("TPEEndcap", [], []),
        14: GeometryData("TIBModule", [], []),
        15: GeometryData("TIBString", [], []),
        16: GeometryData("TIBSurface", [], []),
        17: GeometryData("TIBHalfShell", [], []),
        18: GeometryData("TIBLayer", [], []),
        19: GeometryData("TIBHalfBarrel", [], []),
        20: GeometryData("TIBBarrel", [], []),
        21: GeometryData("TIDModule", [], []),
        22: GeometryData("TIDSide", [], []),
        23: GeometryData("TIDRing", [], []),
        24: GeometryData("TIDDisk", [], []),
        25: GeometryData("TIDEndcap", [], []),
        26: GeometryData("TOBModule", [], []),
        27: GeometryData("TOBRod", [], []),
        28: GeometryData("TOBLayer", [], []),
        29: GeometryData("TOBHalfBarrel", [], []),
        30: GeometryData("TOBBarrel", [], []),
        31: GeometryData("TECModule", [], []),
        32: GeometryData("TECRing", [], []),
        33: GeometryData("TECPetal", [], []),
        34: GeometryData("TECSide", [], []),
        35: GeometryData("TECDisk", [], []),
        36: GeometryData("TECEndcap", [], []),
        37: GeometryData("Pixel", [], []),
        38: GeometryData("Strip", [], []),
        39: GeometryData("Tracker", [], []),
        100: GeometryData("AlignableDTBarrel", [], []),
        101: GeometryData("AlignableDTWheel", [], []),
        102: GeometryData("AlignableDTStation", [], []),
        103: GeometryData("AlignableDTChamber", [], []),
        104: GeometryData("AlignableDTSuperLayer", [], []),
        105: GeometryData("AlignableDTLayer", [], []),
        106: GeometryData("AlignableCSCEndcap", [], []),
        107: GeometryData("AlignableCSCStation", [], []),
        108: GeometryData("AlignableCSCRing", [], []),
        109: GeometryData("AlignableCSCChamber", [], []),
        110: GeometryData("AlignableCSCLayer", [], []),
        111: GeometryData("AlignableMuon", [], []),
        112: GeometryData("Detector", [], []),
        1000: GeometryData("Extras", [], []),
        1001: GeometryData("BeamSpot", [], [])
        }
