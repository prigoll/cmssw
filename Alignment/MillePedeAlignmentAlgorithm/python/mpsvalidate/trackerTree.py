#!/usr/bin/env python

##########################################################################
##
# Check if there is the trackerTree.root file.
##

import logging
import os


def check(config):
    logger = logging.getLogger("mpsvalidate")
    logger.info("Check if TrackerTree.root file exists")

    # check if file exists
    if (not os.path.isfile(os.path.join(config.mpspath, "TrackerTree.root"))):
        logger.info("TrackerTree.root file does not exist. It will be created now.")
        
        os.system("cmsRun {0}".format(os.path.join(config.mpspath, "trackerTree_cfg.py")))