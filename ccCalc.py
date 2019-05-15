#! /usr/bin/env libtbx.python
from __future__ import print_function

from iotbx.reflection_file_reader import any_reflection_file
from iotbx.xds.integrate_hkl import reader
import cctbx.miller as mil
from math import *
import collections
import itertools
import argparse
import struct
import os
import multiprocessing


###
#Load files and create arrays
#
######

#Class to calc correlation on all data in tree of subfolders
class ccCalc():
    def __init__(self):
        self.LogFile=open('ccClusterLog.txt', 'w')
        self.CurrentDir= os.getcwd()
        self.argList=[]
        for root, dirs, files in os.walk('.'):
            directory=root.lstrip('.')
            folder=self.CurrentDir+directory
            if 'XDS_ASCII.HKL' in files:
                self.argList.append(folder+'/XDS_ASCII.HKL')
        self.Arrays= self.loadReflections()
        #self.writeLog()
        self.results = self.calcSerial()
        #self.writeLog()

        
    def loadReflections(self):
        Arrays = {}
        for x in self.argList:
            hklFile = any_reflection_file(x)
            Arrays[x]= hklFile.as_miller_arrays()
            print('File %s has been loaded'%(x))
            #Printing output file
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], os.path.abspath(n[1])),file=self.LogFile)
        return Arrays

    def writeLog(self):
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], os.path.abspath(n[1])),file=self.LogFile)
        print('Correlation coefficients', file=self.LogFile)
        for L in self.results:
            print('%s   %s   %s'%(L[0], L[1], L[2]), file=self.LogFile)

    def ccPrint(self,  arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        for x in Array1:
            if x.is_xray_intensity_array():
                I_obs1=x
                break
        for x in Array2:
            if x.is_xray_intensity_array():
                I_obs2=x
                break

        # I_obs1 = Array1[3]
        # I_obs2 = Array2[3]
        # #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)


        #print I_obs1.correlation(I_obs2, use_binning=False).coefficient()

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            cc= I_ext1.correlation(I_ext2, assert_is_similar_symmetry= False).coefficient()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            cc=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.next(), gen2.next(),sqrt(1.0001-cc**2)


    def cellPrint( arglist):
        HKLarrays
        Array1 = HKLarrays[arglist[0]]
        Array2 =HKLarrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        b1 = Array1
        b2 = Array2

        I_obs1 = b1[0]
        I_obs2 = b2[0]
        #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)
        uc1 = I_obs1.unit_cell().parameters()
        uc2 = I_obs2.unit_cell().parameters()
        a1, b1, c1 = uc1[0], uc1[1], uc1[2]
        a2, b2, c2 = uc2[0], uc2[1], uc2[2]
        variation = [fabs(a1-a2)/min(a1,a2),fabs(b1-b2)/min(b1,b2),fabs(c1-c2)/min(c1, c2)]
        return gen1.next(), gen2.next(), max(variation)

    def calcSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.ccPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)

    def calcAll(self):
        proc = Pool(4)
        a, b, cc = zip(*proc.map(self.ccPrint, itertools.combinations(self.Arrays, 2)))
        L = zip(a, b, cc)
        return L

#class for unit cell without input filenames
    
class cellCalc():
    def __init__(self):
        self.LogFile=open('cellClusterLog.txt', 'w')
        self.CurrentDir= os.getcwd()
        self.argList=[]
        for root, dirs, files in os.walk('.'):
            directory=root.lstrip('.')
            folder=self.CurrentDir+directory
            if 'XDS_ASCII.HKL' in files:
                self.argList.append(folder+'/XDS_ASCII.HKL')
        self.Arrays= self.loadReflections()
        #self.writeLog()
        self.results = self.cellSerial()
        #self.writeLog()

        
    def loadReflections(self):
        Arrays = {}
        for x in self.argList:
            hklFile = any_reflection_file(x)
            Arrays[x]= hklFile.as_miller_arrays()
            print('File %s has been loaded'%(x))
            #Printing output file
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], os.path.abspath(n[1])),file=self.LogFile)
        return Arrays

    def writeLog(self):
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], os.path.abspath(n[1])),file=self.LogFile)
        print('Correlation coefficients', file=self.LogFile)
        for L in self.results:
            print('%s   %s   %s'%(L[0], L[1], L[2]), file=self.LogFile)

    def ccPrint(self,  arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        for x in Array1:
            if x.is_xray_intensity_array():
                I_obs1=x
                break
        for x in Array2:
            if x.is_xray_intensity_array():
                I_obs2=x
                break

        # I_obs1 = Array1[3]
        # I_obs2 = Array2[3]
        # #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)


        #print I_obs1.correlation(I_obs2, use_binning=False).coefficient()

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            cc= I_ext1.correlation(I_ext2, assert_is_similar_symmetry= False).coefficient()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            cc=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.next(), gen2.next(),sqrt(1.0001-cc**2)


    def cellPrint(self, arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        b1 = Array1
        b2 = Array2

        I_obs1 = b1[0]
        I_obs2 = b2[0]
        #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)
        uc1 = I_obs1.unit_cell().parameters()
        uc2 = I_obs2.unit_cell().parameters()
        a1, b1, c1 = uc1[0], uc1[1], uc1[2]
        a2, b2, c2 = uc2[0], uc2[1], uc2[2]
        variation = [fabs(a1-a2)/min(a1,a2),fabs(b1-b2)/min(b1,b2),fabs(c1-c2)/min(c1, c2)]
        return gen1.next(), gen2.next(), max(variation)

    def cellSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.cellPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)




#Calculate cc, but works if you specify a list of HKL files:

class ccList():
    def __init__(self, Arglist):
        self.LogFile=open('ccClusterLog.txt', 'w')
        self.CurrentDir= os.getcwd()
        self.argList= Arglist
        self.Arrays= self.loadReflections()
        self.results = self.calcSerial()


        
    def loadReflections(self):
        Arrays = {}
        for x in self.argList:
            if reader.is_integrate_hkl_file(x):
                Arrays[x]= reader().as_miller_arrays(x)
            else:
                hklFile = any_reflection_file(x)
                Arrays[x]= hklFile.as_miller_arrays()
            print('File %s has been loaded'%(x))
            #Printing output file
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], n[1]),file=self.LogFile)
        return Arrays

    def writeLog(self):
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], n[1]),file=self.LogFile)
        print('Correlation coefficients', file=self.LogFile)
        for L in self.results:
            print('%s   %s   %s'%(L[0], L[1], L[2]), file=self.LogFile)

    def ccPrint(self,  arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        for x in Array1:
            if x.is_xray_intensity_array():
                I_obs1=x
                break
        for x in Array2:
            if x.is_xray_intensity_array():
                I_obs2=x
                break

        # I_obs1 = Array1[3]
        # I_obs2 = Array2[3]
        # #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)


        #print I_obs1.correlation(I_obs2, use_binning=False).coefficient()

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            cc= I_ext1.correlation(I_ext2, assert_is_similar_symmetry= False).coefficient()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            cc=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.next(), gen2.next(),sqrt(1.0001-cc**2)

    def calcSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.ccPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)

    def calcAll(self):
        proc = Pool(4)
        a, b, cc = zip(*proc.map(self.ccPrint, itertools.combinations(self.Arrays, 2)))
        L = zip(a, b, cc)
        return L

#calculate unit cell distance, with list of input files

class cellList():
    def __init__(self, Arglist):
        self.LogFile=open('cellClusterLog.txt', 'w')
        self.CurrentDir= os.getcwd()
        self.argList= Arglist
        self.Arrays= self.loadReflections()
        self.results = self.cellSerial()


        
    def loadReflections(self):
        Arrays = {}
        for x in self.argList:
            if reader.is_integrate_hkl_file(x):
                Arrays[x]= reader().as_miller_arrays(x)
            else:
                hklFile = any_reflection_file(x)
                Arrays[x]= hklFile.as_miller_arrays()
            print('File %s has been loaded'%(x))
            #Printing output file
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], n[1]),file=self.LogFile)
        return Arrays

    def writeLog(self):
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], n[1]),file=self.LogFile)
        print('Correlation coefficients', file=self.LogFile)
        for L in self.results:
            print('%s   %s   %s'%(L[0], L[1], L[2]), file=self.LogFile)

    def cellPrint(self, arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        b1 = Array1
        b2 = Array2

        I_obs1 = b1[0]
        I_obs2 = b2[0]
        #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)
        uc1 = I_obs1.unit_cell().parameters()
        uc2 = I_obs2.unit_cell().parameters()
        a1, b1, c1 = uc1[0], uc1[1], uc1[2]
        a2, b2, c2 = uc2[0], uc2[1], uc2[2]
        variation = [fabs(a1-a2)/min(a1,a2),fabs(b1-b2)/min(b1,b2),fabs(c1-c2)/min(c1, c2)]
        return gen1.next(), gen2.next(), max(variation)

    def cellSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.cellPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)


#function to define a distance based on common reflections

class commonList():
    def __init__(self, Arglist):
        self.LogFile=open('Common.txt', 'w')
        self.CurrentDir= os.getcwd()
        self.argList= Arglist
        self.Arrays= self.loadReflections()
        self.results = self.calcSerial()


        
    def loadReflections(self):
        Arrays = {}
        for x in self.argList:
            if reader.is_integrate_hkl_file(x):
                Arrays[x]= reader().as_miller_arrays(x)
            else:
                hklFile = any_reflection_file(x)
                Arrays[x]= hklFile.as_miller_arrays()
            print('File %s has been loaded'%(x))
            #Printing output file
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], n[1]),file=self.LogFile)
        return Arrays

    def writeLog(self):
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], n[1]),file=self.LogFile)
        print('Correlation coefficients', file=self.LogFile)
        for L in self.results:
            print('%s   %s   %s'%(L[0], L[1], L[2]), file=self.LogFile)

    def ccPrint(self,  arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        for x in Array1:
            if x.is_xray_intensity_array():
                I_obs1=x
                break
        for x in Array2:
            if x.is_xray_intensity_array():
                I_obs2=x
                break

        # I_obs1 = Array1[3]
        # I_obs2 = Array2[3]
        # #Common1, Common2  = I_obs1.common_sets(I_obs2, assert_is_similar_symmetry= False)


        #print I_obs1.correlation(I_obs2, use_binning=False).coefficient()

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            common= ExtCommon1.size()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            common=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.next(), gen2.next(), 1000/common

    def calcSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.ccPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)

    def calcAll(self):
        proc = Pool(4)
        a, b, cc = zip(*proc.map(self.ccPrint, itertools.combinations(self.Arrays, 2)))
        L = zip(a, b, cc)
        return L




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", dest="structures", default= None ,  type=str, nargs='+', help='The list of refined structures to merge')
    parser.add_argument("-u", dest="cell", default= False , action="store_true" , help='Unit cell based clustering. requires list of input files')
    parser.add_argument("-c", dest="common", default= False , action="store_true" , help='Experimental class based on common reflections only')
    args= parser.parse_args()

    #HKLarrays = ccCalc.loadReflections(args.structures)


    CurrentDir= os.getcwd()
    if args.structures is None:
        if args.cell:
            print('No input specified, calculating cell distance')
            print('this might take a while')
            ccCalc()
            correlationFile='cellClusterLog.txt'
        else:
            print('No input specified, calculating Correlation coefficients')
            print('this might take a while')
            ccCalc()
            correlationFile='ccClusterLog.txt'
    elif args.cell:
        print("Calculating unit cell distance between specified files")
        cellList(args.structures)
        correlationFile='cellClusterLog.txt'
    elif args.common :
        print('Warning! I am using the experimental common reflections feature!')
        commonList(args.structures)
        correlationFile='Common.txt'
    else:
        print("Calculating CC between specified files")
        ccList(args.structures)
        correlationFile='ccClusterLog.txt'


"""Region commented out from older version.
Check that everything is still running

"""
    # if args.outname:
    #     LogFile= open(args.outname, 'w')
    # elif args.compl:
    #     LogFile= open('CellClusterLog.txt', 'w')
    # else:
    #     LogFile= open('ccClusterLog.txt', 'w')
    # proc = multiprocessing.Pool(processes=8)
    # print('Read all input files')

    # if args.compl:
    #     a, b, cc = zip(*proc.map(cellPrint, itertools.combinations(HKLarrays, 2)))
    #     print('Done!')
    # else:
    #     a, b, cc = zip(*proc.map(ccPrint, itertools.combinations(HKLarrays, 2)))
    #     print('Done!')

    # #Printing output file
    # print('Labels', file=LogFile)
    # for n in enumerate(args.structures):
    #     print('INPUT_FILE: %s   %s'%(n[0], os.path.abspath(n[1])),file=LogFile)


    # print('Correlation coefficients', file=LogFile)
    # print(a)
    # for L in zip(a, b, cc):
    #     print('%s   %s   %s'%(L[0], L[1], L[2]), file=LogFile)

if __name__== '__main__':
    main()
