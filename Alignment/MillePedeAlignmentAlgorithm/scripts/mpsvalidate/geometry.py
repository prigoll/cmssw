#!/usr/bin/env python

##########################################################################
# Classes which provide the geometry information.
##

from ROOT import TFile, TTree
from mpsvalidate import geometrydata


class Alignables:
    """ Creates a list of the aligned strucutres. Get the signature out of the
    TrackerTree.root file.
    """

    def __init__(self):
        # list of Structure objects, contains structures which were aligned
        self.structures = []

    def name_by_objid(self, objid):
        return geometrydata.data[objid].name

    def get_discriminator(self, objid):
        return geometrydata.data[objid].discriminator

    def create_list(self, MillePedeUser):
        # loop over output TTree
        for line in MillePedeUser:
            # check which structures were aligned
            if (line.ObjId != 1 and 999999 not in map(abs, line.Par)):
                # create new structure object
                name = self.name_by_objid(line.ObjId)
                signature = self.get_signature(line.Id)
                discriminator = self.get_discriminator(line.ObjId)
                # TODO children
                # create structure
                self.structures.append(
                    Structure(name, signature, discriminator))
                # add detids
                self.structure[-1].detids = self.get_detids(signature, discriminator)

    def get_signature(self, detid):
        # get the signature of a structure
        # open TrackerTree.root file
        treeFile = TFile("mpsvalidate/TrackerTree.root")
        tree = treeFile.Get("TrackerTreeGenerator/TrackerTree/TrackerTree")

        for line in tree:
            if (line.RawId == detid):
                return Signature(layer=line.Layer, side=line.Side, half=line.Half, rod=line.Rod, ring=line.Ring, petal=line.Petal, blade=line.Blade, panel=line.Panel, outerinner=line.OuterInner, module=line.Module, rodal=line.RodAl, bladeal=line.BladeAl, nstrips=line.NStrips)

    def get_detids(self, signature, discriminator):
        # list of all detids in the structure
        detids = []
        # open TrackerTree.root file
        treeFile = TFile("mpsvalidate/TrackerTree.root")
        tree = treeFile.Get("TrackerTreeGenerator/TrackerTree/TrackerTree")

        for line in tree:
            # check if line is part of the structure
            if (signature.compare(line, discriminator)):
                detids.append(line.RawId)
        return detids


class Signature:
    """ Signature to identify a DetId in the TrackerTree.root file
    """

    def __init__(self, layer=0, side=0, half=0, rod=0, ring=0, petal=0, blade=0,
                 panel=0, outerinner=0, module=0, rodal=0, bladeal=0, nstrips=0):
        # layer
        self.layer = layer
        self.side = side
        self.half = half
        self.rod = rod
        self.ring = ring
        self.petal = petal
        self.blade = blade
        self.panel = panel
        self.outerinner = outerinner
        self.module = module
        self.rodal = rodal
        self.bladeal = bladeal
        self.nstrips = nstrips

    def compare(self, line, discriminator):

        if ("layer" not in discriminator):
            if (line.Layer != self.layer):
                return False

        if ("side" not in discriminator):
            if (line.Side != self.side):
                return False

        if ("half" not in discriminator):
            if (line.Half != self.half):
                return False

        if ("rod" not in discriminator):
            if (line.Rod != self.rod):
                return False

        if ("ring" not in discriminator):
            if (line.Ring != self.ring):
                return False

        if ("petal" not in discriminator):
            if (line.Petal != self.petal):
                return False

        if ("blade" not in discriminator):
            if (line.Blade != self.blade):
                return False

        if ("panel" not in discriminator):
            if (line.Panel != self.panel):
                return False

        if ("outerinner" not in discriminator):
            if (line.OuterInner != self.outerinner):
                return False

        '''
        if ("module" not in discriminator):
            if (line.Module != self.module):
                return False

        if ("rodal" not in discriminator):
            if (line.RodAl != self.rodal):
                return False

        if ("bladeal"" not in discriminator):
            if (line.BladeAl != self.bladeal):
                return False

        if ("nstrips" not in discriminator):
            if (line.NStrips != self.nstrips):
                return False
        '''

        return True


class Structure:
    """ A object represents a physical strucutre
    """

    def __init__(self, name, signature, discriminator):
        # name of the structure
        self.name = ""
        # signature to identify the DetIds which belong to the structure
        self.signature = None
        # fields which allow to discriminate the parts of the structure
        self.discriminator = []
        # all DetIds which belong to this structure
        self.detids = []
        # signatures of all parts of the structure
        self.children = []
