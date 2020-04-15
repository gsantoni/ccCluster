#! /usr/bin/env python3
from __future__ import print_function, absolute_import

__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 20150-2019"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"




import matplotlib.pyplot as plt
import sys
import os
import subprocess

#import ccCluster classes to run the soft
from .ccCalc import ccList
from .clustering import Clustering


# Insert parse  to change the file path from command line

import argparse



def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="structures", default= None ,  type=str, nargs='+', help='The list of refined structures to merge')
    args= parser.parse_args()
    ccList(args.structures)
    correlationFile='ccClusterLog.txt'
    CC = Clustering(correlationFile)
    Tree = CC.avgTree()
    etiquets=CC.createLabels()
    threshold = CC.thrEstimation()
    fileType = CC.inputType()
    if fileType=="HKL":
        CC.prepareXSCALE('ano',threshold)
        CC.scaleAndMerge('ano',threshold)
        CC.flatClusterPrinter(threshold, etiquets, 'ano')
    elif fileType=="mtz":
        CC.preparePointless('ano',threshold)
        CC.pointlessRun('ano',threshold)
        CC.flatClusterPrinter(threshold, etiquets, 'ano')
    


if __name__ =='__main__' :
    main()
