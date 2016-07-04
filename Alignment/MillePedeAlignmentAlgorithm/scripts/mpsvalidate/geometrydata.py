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


data = {-1: GeometryData("notfound", 0, 0),
        0: GeometryData("invalid", 0, 0),
        1: GeometryData("AlignableDetUnit", 0, 0),
        2: GeometryData("AlignableDet", 0, 0),
        3: GeometryData("TPBModule", 0, 0),
        4: GeometryData("TPBLadder", 0, 0),
        5: GeometryData("TPBLayer", 0, 0),
        6: GeometryData("TPBHalfBarrel", 0, 0),
        7: GeometryData("TPBBarrel", 0, 0),
        8: GeometryData("TPEModule", 0, 0),
        9: GeometryData("TPEPanel", 0, 0),
        10: GeometryData("TPEBlade", 0, 0),
        11: GeometryData("TPEHalfDisk", 0, 0),
        12: GeometryData("TPEHalfCylind", 0, 0),
        13: GeometryData("TPEEndcap", 0, 0),
        14: GeometryData("TIBModule", 0, 0),
        15: GeometryData("TIBString", 0, 0),
        16: GeometryData("TIBSurface", 0, 0),
        17: GeometryData("TIBHalfShell", 0, 0),
        18: GeometryData("TIBLayer", 0, 0),
        19: GeometryData("TIBHalfBarrel", 0, 0),
        20: GeometryData("TIBBarrel", 0, 0),
        21: GeometryData("TIDModule", 0, 0),
        22: GeometryData("TIDSide", 0, 0),
        23: GeometryData("TIDRing", 0, 0),
        24: GeometryData("TIDDisk", 0, 0),
        25: GeometryData("TIDEndcap", 0, 0),
        26: GeometryData("TOBModule", 0, 0),
        27: GeometryData("TOBRod", 0, 0),
        28: GeometryData("TOBLayer", 0, 0),
        29: GeometryData("TOBHalfBarrel", 0, 0),
        30: GeometryData("TOBBarrel", 0, 0),
        31: GeometryData("TECModule", 0, 0),
        32: GeometryData("TECRing", 0, 0),
        33: GeometryData("TECPetal", 0, 0),
        34: GeometryData("TECSide", 0, 0),
        35: GeometryData("TECDisk", 0, 0),
        36: GeometryData("TECEndcap", 0, 0),
        37: GeometryData("Pixel", 0, 0),
        38: GeometryData("Strip", 0, 0),
        39: GeometryData("Tracker", 0, 0),
        100: GeometryData("AlignableDTBarrel", 0, 0),
        101: GeometryData("AlignableDTWheel", 0, 0),
        102: GeometryData("AlignableDTStation", 0, 0),
        103: GeometryData("AlignableDTChamber", 0, 0),
        104: GeometryData("AlignableDTSuperLayer", 0, 0),
        105: GeometryData("AlignableDTLayer", 0, 0),
        106: GeometryData("AlignableCSCEndcap", 0, 0),
        107: GeometryData("AlignableCSCStation", 0, 0),
        108: GeometryData("AlignableCSCRing", 0, 0),
        109: GeometryData("AlignableCSCChamber", 0, 0),
        110: GeometryData("AlignableCSCLayer", 0, 0),
        111: GeometryData("AlignableMuon", 0, 0),
        112: GeometryData("Detector", 0, 0),
        1000: GeometryData("Extras", 0, 0),
        1001: GeometryData("BeamSpot", 0, 0)
        }
