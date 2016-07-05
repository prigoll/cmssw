#!/usr/bin/env python

##########################################################################
# Classes which provide the geometry information.
##

from ROOT import TFile, TTree

from mpsvalidate import geometrydata


class Alignables:
    """ Creates a list of the aligned strucutres. Get the fields out of the
    TrackerTree.root file.
    """

    def __init__(self):
        # list of Structure objects, contains structures which were aligned
        self.structures = []

    def get_name_by_objid(self, objid):
        return geometrydata.data[objid].name

    def get_subdetid(self, objid):
        return geometrydata.data[objid].subdetid

    def get_discriminator(self, objid):
        return geometrydata.data[objid].discriminator

    def get_ndiscriminator(self, objid):
        return geometrydata.data[objid].ndiscriminator

    def create_list(self, MillePedeUser):
        # loop over output TTree
        for line in MillePedeUser:
            # check which structures were aligned
            if (line.ObjId != 1 and 999999 not in map(abs, line.Par)):
                # check if structure is not yet in the list
                if not any(x.name == self.get_name_by_objid(line.ObjId) for x in self.structures):
                    # create new structure object
                    name = self.get_name_by_objid(line.ObjId)
                    subdetid = self.get_subdetid(line.ObjId)
                    discriminator = self.get_discriminator(line.ObjId)
                    ndiscriminator = self.get_ndiscriminator(line.ObjId)
                    # TODO children
                    # create structure
                    self.structures.append(
                        Structure(name, subdetid, discriminator, ndiscriminator))
                    # add detids which belong to this structure
                    self.structures[-1].detids = self.get_detids(subdetid)

    def get_detids(self, subdetid):
        # list of all detids in the structure
        detids = []
        # open TrackerTree.root file
        treeFile = TFile("mpsvalidate/TrackerTree.root")
        tree = treeFile.Get("TrackerTreeGenerator/TrackerTree/TrackerTree")

        for line in tree:
            # check if line is part of the structure
            if (line.SubdetId == subdetid):
                detids.append(line.RawId)
        return detids


class Structure:
    """ A object represents a physical strucutre
    """

    def __init__(self, name, subdetid, discriminator, ndiscriminator):
        # name of the structure
        self.name = name
        # fields to identify the DetIds which belong to the structure
        self.subdetid = subdetid
        # fields which allow to discriminate the parts of the structure
        self.discriminator = discriminator
        # number per discriminator
        self.ndiscriminator = ndiscriminator
        # all DetIds which belong to this structure
        self.detids = []
        # fieldss of all parts of the structure
        self.children = []

    def get_name(self):
        return self.name

    def contains_detid(self, detid):
        if detid in self.detids:
            return True
        return False
