#! /usr/bin/env python
from __future__ import print_function

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
#from scipy.cluster import hierarchy
#import collections
#import operator
#from time import sleep
import os
import subprocess
#import ccCluster classes

from resultsTab import resultsTab
from summary import resultsSummary
from clustering import Clustering


# Insert parse  to change the file path from command line

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i","--DISTfile", dest="DISTfile", default=None, help="Distance file from ccCalc module")
parser.add_argument("-f", dest="structures", default= None ,  type=str, nargs='+', help='The list of refined structures to merge')
#argument not currently in use, commented out
#parser.add_argument("-o","--outname", dest="outname", default='Dendrogram', help="output dendogram file name")
parser.add_argument("-t", "--threshold", dest="threshold", help="Distance threshold for clustering")
parser.add_argument("-s", "--shuffle", dest="shuffle",action="store_true",default=False, help="Activates the XSCALE Shuffle function")
parser.add_argument("-p", "--process",action="store_true", dest="shell", default=False, help="Launch program in shell mode. Need to specify the threshold value")
parser.add_argument("-c", "--count",action="store_true", dest="count", default=False, help="Counts datasets in the biggest cluster and exit")
parser.add_argument("-e", "--estimation",action="store_true", dest="est", default=False, help="Tries to guess an optimal threshold value")
parser.add_argument("-u", dest="cell", default= False , action="store_true" , help='Unit cell based clustering. requires list of input files')
#Minimal for completeness is currently broken
#parser.add_argument("-m", dest="minimal", default= False , action="store_true" , help='Gives minimal threshold for completeness')


#parser.print_help()
args= parser.parse_args()

#Startup message

print("""ccCluster - HCA for protein crystallography 
G. Santoni and A. Popov, 2015-2019
              v .   ._, |_  .,
           `-._\/  .  \ /    |/_
               \\  _\, y | \//
         _\_.___\\, \\/ -.\||
           `7-,--.`._||  / / ,
           /'     `-. `./ / |/_.'
                     |    |//
                     |_    /
                     |-   |
                     |   =|
                     |    |
--------------------/ ,  . \--------._
""")


#Suggest to run ccCalc if no correlation file is provided
#if args.DISTfile is None:
#    print('no inputs specified, please run ccCalc before')
#else:
#    correlationFile=args.DISTfile


##
#Call to ccCalc if no distances founf but files listed

if args.DISTfile is None: 
    if args.structures is None:
        print('no inputs specified, please run ccCalc before')
        exit()
    else:
        #Run ccCalc with initial args list
        hklin = " ".join(str(x) for x in args.structures)
        C = subprocess.Popen('ccCalc -f %s'%(hklin), cwd=os.getcwd())
        #C = subprocess.Popen('/opt/pxsoft/bin/ccCalc', '-h',cwd=os.getcwd())
        correlationFile=('ccCluster_log.txt')
else:
    correlationFile=args.DISTfile



CC = Clustering(correlationFile)
Tree = CC.avgTree()
etiquets=CC.createLabels()
threshold = CC.thrEstimation()
fileType = CC.inputType()

# #Main part of the program
# #with the different options, we can chose 
# # to process through the shell,
# #count the multiplicity of the highest cluster


def main():
    if args.threshold:
        threshold = args.threshold
    else:
        threshold= CC.thrEstimation()

    if args.shell:
        CC.checkMultiplicity(threshold)
        if fileType=="HKL":
            CC.prepareXSCALE('ano',threshold)
            CC.scaleAndMerge('ano',threshold)
            CC.flatClusterPrinter(threshold, etiquets, 'ano')
        elif fileType=="mtz":
            CC.preparePointless('ano',threshold)
            CC.pointlessRun('ano',threshold)
            CC.flatClusterPrinter(threshold, etiquets, 'ano')
        else:            print("Unknown input file format.")
    elif args.count:
        CC.checkMultiplicity(threshold)
    elif args.est:
        a = CC.thrEstimation()
        print(a)
    elif args.shuffle:
        CC.shuffleXscale('ano',threshold)
if __name__== '__main__':
    main()
