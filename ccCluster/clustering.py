from __future__ import print_function
__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 20150-2019"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"




from scipy.cluster import hierarchy
import scipy
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import os
import numpy as np
import subprocess
import collections
import operator
import stat
import json
import random


class Clustering():
    """
    parse cc_calc output and perform HCA
    at each call, it generates the distance matrix
    You get the dendrogram through Clustering.tree()

    """
    def __init__(self, ccCalcOutput):
        self.ccFile= ccCalcOutput
        self.CurrentDir = os.getcwd()
        self.ccTable, self.Dimension = self.parseCCFile()
        self.createLabels()
        self.previousProcess()


    def previousProcess(self):
        """
        Lists all the clusters which have already been processed from a log file.
        Updates the global variable alreadyDone
        """
        self.alreadyDone= []
        if os.path.isfile(os.getcwd()+'/.cc_cluster.log'):
            with open(os.getcwd()+'/.cc_cluster.log') as log:
                for line in log:
                    L = line.split(',')
                    self.alreadyDone.append([L[1], L[2].strip(), L[3].strip()])

    def parseCCFile(self):
        """
        Gets data from ccCalc ouput file and populates a numpy array with the distances
        """
        with open(self.ccFile, 'r') as f:
            dataArr = None
            data=[]
            Index = []
            for line in f:
                if line.strip() == 'Correlation coefficients':
                    break
            for line in f:
                dataline= line.rstrip().split()
                data.append(dataline)
                Index.append(int(dataline[0])+1)
                Index.append(int(dataline[1])+1)
        Dimension=max(Index)
        dataArr = np.array(data,dtype=(float))
        return dataArr, Dimension

    def createLabels(self):
        """
        Gets the labels from the ccCalc output with the input file names
        """        
        self.labelList= []
        with open(self.ccFile) as f:   
            for line in f:
                if line.strip() == 'Labels':
                    break
            for line in f:
                if line.strip() == 'Correlation coefficients':
                    break
                goodLine = line.split()
                self.labelList.append("%s"%(goodLine[2].strip('\n')))
        return self.labelList
        

    def inputType(self):
        """
        return input file type. Either mtz or HLK
        """        
        element = self.labelList[0]
        extension = element.split('.')[-1]
        print(extension)
        return extension
    
    def tree(self):
        """
        Returns the HCA dendrogrm, using the complete linkage method
        """        
        data = self.ccTable
        Matrix=np.zeros((self.Dimension,self.Dimension))

        reducedArray=[]
        for line in data:
            if line != None and len(line) != 0:
                 Matrix[int(line[0]),int(line[1])]= line[2]
                 Matrix[int(line[1]),int(line[0])]= line[2]


        for x in range(0,self.Dimension):
            for y in range(x+1,self.Dimension):
                reducedArray.append(Matrix[x,y])

        Distances = np.array(reducedArray, dtype=(float))
        self.Tree =hierarchy.linkage(Distances, 'complete')
        return self.Tree

    def avgTree(self):
        """
        Returns the HCA dendrogrm, using the average linkage method
        """        
        data = self.ccTable
        Matrix=np.zeros((self.Dimension,self.Dimension))

        reducedArray=[]
        for line in data:
            if line != None and len(line) != 0:
                 Matrix[int(line[0]),int(line[1])]= line[2]
                 Matrix[int(line[1]),int(line[0])]= line[2]
        for x in range(0,self.Dimension):
            for y in range(x+1,self.Dimension):
                reducedArray.append(Matrix[x,y])

        Distances = np.array(reducedArray, dtype=(float))
        self.Tree =hierarchy.linkage(Distances, 'average')

        return self.Tree

    def flatClusterPrinter(self, thr, labelsList, anomFlag):
        """
        Prints the flat cluster at a chosen threshold to a .json file
        """        
        FlatC=hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        clusterToJson={}
        clusterToJson['HKL']=[]
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        clusterFile =  open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/flatCluster.json'%(float(thr),Best, anomFlag), 'w')        
        for cluster, hkl in zip(FlatC, labelsList):
            clusterToJson['HKL'].append({
                'input_file':hkl,
                'cluster':str(cluster)
                })
        print(clusterToJson)
        j = json.dumps(clusterToJson, indent=4)
        print(j, file=clusterFile)

# function to pipe HCA into codgas for subsequent GA analysis.

    def passOInfoToGA(self, thr, labelsList, anomFlag)
        FlatC=hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        codgasINP =  open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/codgas.INP'%(float(thr),Best, anomFlag), 'w')
        for cluster, dataset in zip(FlatC, labelsList):
            print("%s %s"%(dataset, cluster), codgasINP)
        
        
    def thrEstimation(self):
        """
        Estimates the threshold for optimal clustering, based on the multiplicity of the biggest cluster
        """             
        x = 0.00
        dx = 0.05
        countsList = []
        x_list = []
        while x < 1:
            
            FlatC = hierarchy.fcluster(self.Tree, x, criterion='distance')
            counter=collections.Counter(FlatC)
            Best = max(counter.items(), key=operator.itemgetter(1))[0]
            countsList.append(counter[Best])        
            x+= dx
            x_list.append(x)
        dy = np.diff(countsList)

        for a, b in zip (x_list, dy):
            if b == max(dy):
                return a

    def checkMultiplicity(self, thr):
        """
        Prints the multiplicity of the biggest cluster at a given threshold
        """                
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        print('You are clustering with a threshold of %s'%(thr))
        print('The biggest cluster contains %s datasets from a total of %s'%(counter[Best], len(self.labelList)))


    def completenessEstimation(self):
        x = 0.00
        dx = 0.05
        while x > 1:
            FlatC = hierarchy.fcluster(self.Tree, x, criterion='distance')
            counter=collections.Counter(FlatC)
            Best = max(counter.items(), key=operator.itemgetter(1))[0]


# the list self.ToProcess is needed by the scaling routines
# fix all this new mess!
    def whatToProcess(self):
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')        
        counter=collections.Counter(FlatC)
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        Process = True
        #change checkboxes to standard variables
        if Process:
            self.ToProcess = [Best]    
        else:
            self.ToProcess = set(Clusters)
            for key in self.ToProcess:
                if counter[key]==1:
                    self.ToProcess = [x for x in self.ToProcess if x != key]
        return self.ToProcess


#Run XSCALE to merge the biggest cluster
#input files
#!!!! Will need to define the processes to run externally
#renaming function! Edit the calls in ccCluster accordingly
                    
    def prepareXSCALE(self, anomFlag, thr):
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        Process = True
#change checkboxes to standard variables
        if Process:
            self.ToProcess = [Best]    
        else:
            self.ToProcess = set(Clusters)
            for key in self.ToProcess:
                if counter[key]==1:
                    self.ToProcess = [x for x in self.ToProcess if x != key]
        for x in self.ToProcess:
            if [thr,x, anomFlag] not in  self.alreadyDone:
                os.mkdir(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s'%(float(thr),x, anomFlag))
                Xscale=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/XSCALE.INP'%(float(thr),x, anomFlag), 'a')
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag ), 'a')
                print('OUTPUT_FILE=scaled.hkl',file=Xscale)
                print('MERGE= TRUE', file=Xscale)
                print('pointless hklout clustered.mtz << eof', file=Pointless)
                if anomFlag=='ano':
                    print('FRIEDEL\'S_LAW= FALSE', file=Xscale)
                elif anomFlag=='no_ano':
                    print('FRIEDEL\'S_LAW= TRUE', file=Xscale)
                Xscale.close()
                Pointless.close()

        for cluster, filename in zip(FlatC,self.labelList):
            if cluster in self.ToProcess:
                OUT = open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/XSCALE.INP'%(float(thr),cluster,anomFlag), 'a')
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),cluster,anomFlag), 'a')
                print ('INPUT_FILE= ../%s'%(filename), file=OUT)
                #print ('INCLUDE_RESOLUTION_RANGE=20, 1.8', file=OUT)
                print ('MINIMUM_I/SIGMA= 0', file=OUT)
                print ('XDSIN ../%s'%(filename), file= Pointless)
                OUT.close()
                Pointless.close()

    def preparePointless(self, anomFlag, thr):
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        Process = True
#change checkboxes to standard variables
        if Process:
            self.ToProcess = [Best]    
        else:
            self.ToProcess = set(Clusters)
            for key in self.ToProcess:
                if counter[key]==1:
                    self.ToProcess = [x for x in self.ToProcess if x != key]
        for x in self.ToProcess:
            if [thr,x, anomFlag] not in  self.alreadyDone:
                os.mkdir(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s'%(float(thr),x, anomFlag))
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag ), 'a')
                print('pointless hklout clustered.mtz << eof', file=Pointless)
                print('XMLOUT pointlessLog.xml', file=Pointless)                
                Pointless.close()

        for cluster, filename in zip(FlatC,self.labelList):
            if cluster in self.ToProcess:
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),cluster,anomFlag), 'a')
                print ('HKLIN ../%s'%(filename), file= Pointless)
                Pointless.close()

#Run XSCALE in the pre-determined folders.

    def scaleAndMerge(self, anomFlag, thr):
        newProcesses=[]
        for x in self.ToProcess:
            if [thr,x, anomFlag] not in  self.alreadyDone:
                #self.createDendrogram(thr)
                #plt.savefig(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/Dendrogram.png'%(float(thr),x,anomFlag))
                P= subprocess.Popen('xscale_par',cwd=self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/'%(float(thr), x, anomFlag))     
                P.wait()
#                print('Cluster, %s , %s , %s'%(float(thr),x, anomFlag), file=Log)             
                newProcesses.append([thr,x, anomFlag])

#run Pointless in each folder from the processing List
    def pointlessRun(self, anomFlag, thr):
        newProcesses=[]
        for x in self.ToProcess:
            if [thr,x, anomFlag] not in  self.alreadyDone:
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag), 'a')
                print('COPY \n bg\n TOLERANCE 4 \n eof', file= Pointless)
                Pointless.close()
                st = os.stat(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag ))
                os.chmod(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag ), st.st_mode | 0o111)       
                P = subprocess.Popen(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh > pointless.log')
                P.wait()





#run aimless on the output from pointless
#will run in folders with clustered.mtz file available.
#TBD: fix directories paths into the aimless.inp file
#also set all the proper input values into the function call
#path to aimless executable to be verified.

    def aimlessRun(self, anomFlag, thr):
        for x in self.toProcess:
            if [thr,x, anomFlag] not in  self.alreadyDone:
                f1= open("aimless.inp", 'w')
                runScript='''#!/bin/bash
source /opt/pxsoft/ccp4/vdefault/linux-x86_64/ccp4-7.0/setup-scripts/ccp4.setup-sh

aimless HKLIN {infile} << EOF
HKLOUT {setname}_aimless.mtz'
RESOLUTION LOW {resLow}  HIGH {resHigh}
OUTPUT MERGED
anomalous {anomflag}
EOF

#truncate: generate Fs
truncate hklin {setname}_aimless.mtz hklout {setname}_tr.mtz <<EOF-trunc
truncate yes
EOF-trunc


#unique: generate unique reflection set for rfree
unique HKLOUT x_unq.mtz << EOF
CELL {cell}
SYMMETRY '{SpaceGroup}'
LABOUT F=FUNI SIGF=SIGFUNI
RESOLUTION {resHigh}
EOF

#freerflag: generate free reflections
freerflag  HKLIN x_unq.mtz HKLOUT x_FreeR_unq.mtz <<EOF
FREERFRAC 0.05
END
EOF

#cad: combine free reflections with data
cad HKLIN1 x_FreeR_unq.mtz HKLIN2 {setname}_tr.mtz  HKLOUT {setname}_cad.mtz<<EOF
LABI FILE 1  E1=FreeR_flag
LABI FILE 2  ALLIN
END
EOF

freerflag  HKLIN {setname}_cad.mtz HKLOUT {setname}_scaled.mtz <<EOF
COMPLETE FREE=FreeR_flag
END
EOF
'''.format(infile = 'clustered.mtz', setname = 'clustered', resHigh = '1.0', resLow = '60', anomflag = 'ON', cell = cell, SpaceGroup = SpaceGroup)
                f1.write(runScript)
                f1.close()
                os.chmod(CurrentDir + '/aimless.inp', st.st_mode | 0o111)
                subprocess.call('./aimless.inp > aimless.log', cwd=CurrentDir, shell=True)
     

# A function to investigate the influence of reference file in merging results
                
    def shuffleXscale(self, anomFlag, thr):
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')
        Log = open(self.CurrentDir+'/.cc_cluster.log', 'a')
        counter=collections.Counter(FlatC)
        Best = max(counter.items(), key=operator.itemgetter(1))[0]
        print(Best)
        Process = True
        xscaleInputFiles=[]
#change checkboxes to standard variables
        if Process:
            self.ToProcess = [Best]    
        else:
            self.ToProcess = set(Clusters)
            for key in self.ToProcess:
                if counter[key]==1:
                    self.ToProcess = [x for x in self.ToProcess if x != key]
#Prepare list of filenames to shuffle over
        for cluster, filename in zip(FlatC, self.labelList):
            if cluster in self.ToProcess:
                xscaleInputFiles.append(filename)
        print(xscaleInputFiles)
#run XSCALE with random ordered files 20 times
        for x in range(0,20):
            os.mkdir(self.CurrentDir+'/thr_%.2f_run_%s'%(float(thr),x))
            Xscale=open(self.CurrentDir+'/thr_%.2f_run_%s/XSCALE.INP'%(float(thr),x), 'a')
            print('OUTPUT_FILE=scaled.hkl',file=Xscale)
            print('MERGE= TRUE', file=Xscale)
            print('FRIEDEL\'S_LAW=TRUE', file=Xscale )
            random.shuffle(xscaleInputFiles)
            for hkl in xscaleInputFiles:
                print ('INPUT_FILE= ../%s'%(hkl), file=Xscale)
                print ('MINIMUM_I/SIGMA= 0', file=Xscale)        
            P= subprocess.Popen('xscale_par',cwd=self.CurrentDir+'/thr_%.2f_run_%s'%(float(thr),x))     
            P.wait()
   
        
                        

                
def main():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog --XSCALEfile=<LP filename> --outname=<output dendogram>")

    parser.add_option("-o","--outname", dest="outname", default='Dendrogram', help="output dendogram file name")
    parser.add_option("-t", "--threshold", dest="threshold", default='0.4', help="Distance threshold for clustering")
    parser.add_option("-c", "--count",action="store_true", dest="count", default=False, help="Counts datasets in the biggest cluster and exit")
    (options, args) = parser.parse_args()

    thr = float(options.threshold)
    CC = Clustering('Cluster_log.txt')
    link = CC.tree()
    if options.count:
        CC.checkMultiplicity(thr)
        print(CC.thrEstimation())
    else:
        CC.checkMultiplicity(thr) 
        CC.merge('ano', thr)

if __name__== '__main__':
    main()
