#! /usr/bin/env libtbx.python
from __future__ import print_function, absolute_import 

__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 20150-2019"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"




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
    """
    docsting here
    This clas is used to calculate distances based on the cc between the datasets.
    it works when no input files is provided.
    """
    def __init__(self):
        self.LogFile=open('ccClusterLog.txt', 'w')
        self.CurrentDir= os.getcwd()
        self.argList=[]
        for root, dirs, files in os.walk('.'):
            directory=root.lstrip('.')
            folder=self.CurrentDir+directory
#            if 'XDS_ASCII.HKL' in files:
#                self.argList.append(folder+'/XDS_ASCII.HKL')
            structures = [folder+'/'+fi for fi in files if fi.endswith(".HKL")]
        self.argList = structures
        self.Arrays= self.loadReflections()
        #self.writeLog()
        self.results = self.calcSerial()
        #self.writeLog()

        
    def loadReflections(self):
        """
        Loads a file using cctbx and puts the corresponding miller array in a dictionary.
        Dictionary keys are the filenames given as input.
        """
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
        """
        Writes labels and distance matrix to a plain text file
        """
        print('Labels', file=self.LogFile)
        for n in enumerate(self.argList):
            print('INPUT_FILE: %s   %s'%(n[0], os.path.abspath(n[1])),file=self.LogFile)
        print('Correlation coefficients', file=self.LogFile)
        for L in self.results:
            print('%s   %s   %s'%(L[0], L[1], L[2]), file=self.LogFile)

    def ccPrint(self,  arglist):
        """
        Calculates and returns cc between input files.
        Returns the matrix element for being written in the log file
        """
        
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
        return gen1.__next__(), gen2.__next__(),sqrt(1.0001-cc**2)


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
        return gen1.__next__(), gen2.__next__(), max(variation)

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

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            cc= I_ext1.correlation(I_ext2, assert_is_similar_symmetry= False).coefficient()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            cc=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.__next__(), gen2.__next__(),sqrt(1.0001-cc**2)


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
        return gen1.__next__(), gen2.__next__(), max(variation)

    def cellSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.cellPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)



class ccList():
    """
    docsting here
    This class is used to calculate distances based on the cc between the datasets.
    it works with a list input files from args.parser
    """
    def __init__(self, Arglist):
        self.LogFile=open('ccClusterLog.txt', 'w')
        self.GAfolder = os.mkdir('GA')
        self.GAinput = open('GA/codgas.INP', 'w')
        self.CurrentDir= os.getcwd()
        self.argList= Arglist
        self.Arrays= self.loadReflections()
        self.results = self.calcSerial()
        self.simpleAvgCell()


        
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

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            cc= I_ext1.correlation(I_ext2, assert_is_similar_symmetry= False).coefficient()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            cc=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.__next__(), gen2.__next__(),sqrt(1.0001-cc**2)

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
# simple tool for avg unit cell, parsing directly the HKL file.
    def simpleAvgCell(self):
        A = []
        B = []
        C = []
        Al= []
        Be= []
        Ga= []
        for x in self.argList:
            with open(x, 'r') as fi:
                for ln in fi:
                    if ln.startswith('!SPACE_GROUP_NUMBER'):
                        sgline = ln.split()
                        sg = sgline[1]
                    if ln.startswith('!UNIT_CELL_CONSTANTS'):
                        params = ln.split()
                        a, b, c = params[1], params[2], params[3]
                        alfa, beta, gamma = params[4], params[5], params[6]
                        print(a,b,c)
                        A.append(float(a))
                        B.append(float(b))
                        C.append(float(c))
                        Al.append(float(alfa))
                        Be.append(float(beta))
                        Ga.append(float(gamma))
        print(sg, file=self.GAinput) 
        print(sum(A)/len(A), sum(B)/len(B), sum(C)/len(C),sum(Al)/len(Al), sum(Be)/len(Be),sum(Ga)/len(Ga), file=self.GAinput)
            
            
    
#following function outputs the UC parameter and SG to be sent to codgas, using CCTBX
    def getUnitCell(self, arg):
        Array1 = arg
        b1 = Array1
        I_obs1 = b1[0]
        uc1 = I_obs1.unit_cell().parameters()
        a1, b1, c1 = uc1[0], uc1[1], uc1[2]
        print(a1,b1,c1)
        return a1, b1, c1

    def calcAvgCell(self):
        A = []
        B = []
        C = []
        for x in self.Arrays:
            a, b, c = self.getUnitCell(x)
            A.append(a)
            B.append(b)
            C.append(c)
            print('%s %s %s'%(a,b,c))
        avgA = sum(A)/len(A)
        avgB = sum(B)/len(B)
        avgC = sum(C)/len(C)
        print("%s %s %s "%(avgA, avgB, avgC), self.GAinput)



        
        


        
        
class cellList():
    """
    This class is used to calculate distances based on the unit cell variations between the datasets.
    it works with a list input files from args.parser
    """   
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
        uc1 = I_obs1.unit_cell().parameters()
        uc2 = I_obs2.unit_cell().parameters()
        a1, b1, c1 = uc1[0], uc1[1], uc1[2]
        a2, b2, c2 = uc2[0], uc2[1], uc2[2]
        variation = [fabs(a1-a2)/min(a1,a2),fabs(b1-b2)/min(b1,b2),fabs(c1-c2)/min(c1, c2)]
        return gen1.__next__(), gen2.__next__(), max(variation)

    def cellSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.cellPrint(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)



class blendList():
    """
    This class is used to calculate distances based on the blend LCV between the datasets.
    it works with a list input files from args.parser
    """     
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

    def diagonalCell(self, a, b, angle):
        cosArgument= radians(180-angle)
        diag = sqrt(a**2+b**2-2*a*b*cos(cosArgument))
        return diag
    
    def blendLCV(self, arglist):
        Array1 = self.Arrays[arglist[0]]
        Array2 = self.Arrays[arglist[1]]

        gen1 = (i for i,F in enumerate(self.argList) if F == arglist[0])
        gen2 = (i for i,F in enumerate(self.argList) if F == arglist[1])

        b1 = Array1
        b2 = Array2

        I_obs1 = b1[0]
        I_obs2 = b2[0]
        uc1 = I_obs1.unit_cell().parameters()
        uc2 = I_obs2.unit_cell().parameters()
        a1, b1, c1, al1, be1, ga1 = uc1[0], uc1[1], uc1[2], uc[3], uc[4] , uc[5]
        a2, b2, c2, al2, be2, ga2 = uc2[0], uc2[1], uc2[2], uc[3], uc[4] , uc[5]
        bdiag1 = self.diagonalCell(a1, b1, ga1)
        bdiag2 = self.diagonalCell(b1, c1, al1)
        bdiag3 = self.diagonalCell(c1, a1, be1)
        bdiag1 = self.diagonalCell(a2, b2, ga2)
        bdiag2 = self.diagonalCell(a2, b2, ga2)
        bdiag3 = self.diagonalCell(a2, b2, ga2)        

        #Calculate the LCV
        LCV = [fabs(adiag1-bdiag1)/min(adiag1,bdiag1),
               fabs(adiag2-bdiag2)/min(adiag2,bdiag2),
               fabs(adiag3-bdiag3)/min(adiag3, bdiag2)]
        return gen1.__next__(), gen2.__next__(), max(LCV)

    def cellSerial(self):
        print('Correlation coefficients', file=self.LogFile)
        for x in itertools.combinations(self.Arrays, 2):
            a, b, cc = self.blendLCV(x)
            print('%s   %s   %s'%(a , b , cc), file=self.LogFile)


class commonList():
    """
    EXPERIMENTAL CODE!!!!! Do not use
    This class is used to calculate distances based on the cc between the datasets.
    it works with a list input files from args.parser
    """ 
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

        I_ext1= I_obs1.generate_bijvoet_mates()
        I_ext2= I_obs2.generate_bijvoet_mates()
        try:
            ExtCommon1, ExtCommon2 = I_ext1.common_sets(I_ext2, assert_is_similar_symmetry= True)
            common= ExtCommon1.size()
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))
        except:
            common=0
            print('Calculated correlation between %s and %s'%(arglist[0],arglist[1]))         
        return gen1.__next__(), gen2.__next__(), 1000/common

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
