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
import time
import subprocess
from os.path import join , isfile
#import ccCluster classes to run the soft
from .ccCalc import ccList
from .clustering import Clustering


def main():
    workdir = os.getcwd()
    try:
        os.mkdir(workdir+'/HCA')
        os.chdir(workdir+'/HCA')
    except:
        os.chdir(workdir+'/HCA')        
    grenades_runs = [join(workdir,x) for x in os.listdir(workdir) if 'grenades' in x]
    succes = []
    failed = []
    shouldContinue = True
    while shouldContinue==True:
        time.sleep(5)
        for path in grenades_runs :
            if isfile(path+'/.SUCCESS') :
                success.append(path)
            elif isfile(path+'/.FAILED'):
                failed.append(path)
            else:
                
        if len(success)+len(failed)==len(folders):
            shouldContinue = False
    
    ccList(success)
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

    
