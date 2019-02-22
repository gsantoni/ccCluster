from __future__ import print_function

from scipy.cluster import hierarchy
import scipy
import matplotlib.pyplot as plt
import os
import numpy as np
import subprocess
import collections
import operator
import stat
import json

#parse cc_calc output and perform HCA
#at each call, it generates the distance matrix
# You get the dendrogram through Clustering.tree()

class Clustering():
    def __init__(self, ccCalcOutput):
        self.ccFile= ccCalcOutput
        self.CurrentDir = os.getcwd()
        #run parser
        self.ccTable, self.Dimension = self.parseCCFile()
        self.createLabels()
        self.previousProcess()
        A = self.tree()

    def previousProcess(self):
        self.alreadyDone= []
        if os.path.isfile(os.getcwd()+'/.cc_cluster.log'):
            with open(os.getcwd()+'/.cc_cluster.log') as log:
                for line in log:
                    L = line.split(',')
                    self.alreadyDone.append([L[1], L[2].strip(), L[3].strip()])

    def parseCCFile(self):
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
        

#changed, now the distance is defined directly by ccCalc
    def tree(self):
        data = self.ccTable
        Matrix=np.zeros((self.Dimension,self.Dimension))

        reducedArray=[]
        for line in data:
                #print line
            if line is not None and len(line) is not 0:
                 Matrix[int(line[0]),int(line[1])]= line[2]
                 Matrix[int(line[1]),int(line[0])]= line[2]


        for x in range(0,self.Dimension):
            for y in range(x+1,self.Dimension):
                reducedArray.append(Matrix[x,y])

        Distances = np.array(reducedArray, dtype=(float))
        self.Tree =hierarchy.linkage(Distances, 'complete')

        return self.Tree

#new function, chose the average linkage
    def avgTree(self):
        data = self.ccTable
        Matrix=np.zeros((self.Dimension,self.Dimension))

        reducedArray=[]
        for line in data:
                #print line
            if line is not None and len(line) is not 0:
                 Matrix[int(line[0]),int(line[1])]= line[2]
                 Matrix[int(line[1]),int(line[0])]= line[2]
        for x in range(0,self.Dimension):
            for y in range(x+1,self.Dimension):
                reducedArray.append(Matrix[x,y])

        Distances = np.array(reducedArray, dtype=(float))
        self.Tree =hierarchy.linkage(Distances, 'average')

        return self.Tree

#Funtion added to plot dendrogram in shell mode only.
#still not funtioninhg
#Uncomment when will be needed
    def createDendrogram(self, thr, pos=None):
        X = hierarchy.dendrogram(self.Tree, color_threshold=thr)
        plt.draw()

#Function to return flat cluster to a text file
#will be included in the output folder for the cluster

    def flatClusterPrinter(self, thr, labelsList, anomFlag):
        FlatC=hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        clusterToJson={}
        clusterToJson['HKL']=[]
        Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
        clusterFile= open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/flatCluster.txt'%(float(thr),Best, anomFlag), 'a')
        for cluster, hkl in zip(FlatC, labelsList):
            clusterToJson['HKL'].append({
                'input_file':hkl,
                'cluster':str(cluster)
                })
        print(clusterToJson)
        with open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/flatCluster.json'%(float(thr),Best, anomFlag), 'w') as fp:
            json.dump(clusterToJson, fp)

                

        
    def thrEstimation(self):
        x = 0.00
        dx = 0.05
        countsList = []
        x_list = []
        while x < 1:
            
            FlatC = hierarchy.fcluster(self.Tree, x, criterion='distance')
            counter=collections.Counter(FlatC)
            Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
            countsList.append(counter[Best])        
            x+= dx
            x_list.append(x)
        dy = np.diff(countsList)

        for a, b in zip (x_list, dy):
            if b == max(dy):
                return a

    def checkMultiplicity(self, thr):
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')
        counter=collections.Counter(FlatC)
        Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
        print('You are clustering with a threshold of %s'%(thr))
        print('The biggest cluster contains %s datasets from a total of %s'%(counter[Best], len(self.labelList)))


    def completenessEstimation(self):
        x = 0.00
        dx = 0.05
        while x > 1:
            FlatC = hierarchy.fcluster(self.Tree, x, criterion='distance')
            counter=collections.Counter(FlatC)
            Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
            
    # def minimalForCompleteness(self):
    #     print("Running estimator for minimal threshold for completeness")
    #     labels=self.createLabels()
    #     x = 0.00
    #     dx = 0.05
    #     countsList = {}
    #     x_list = []
    #     while x < 1:
    #         Arrays= {}
    #         FlatC = hierarchy.fcluster(self.Tree, x, criterion='distance')
    #         counter=collections.Counter(FlatC)
    #         Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
    #         toProcess=[Best]
    #         y=0
    #         for cluster, filename in zip(FlatC,labels):
    #             if cluster in toProcess:
    #                 hklFile = any_reflection_file(filename)
    #                 b= hklFile.as_miller_arrays()
    #                 for column in b:
    #                     if column.is_xray_intensity_array():
    #                         Arrays[y]=column
    #                         break
    #                 y+=1
    #         try:
    #             Arr = Arrays[0]
    #         except:
    #             countsList.append(0)
    #         for label in range(1, y):
    #             try:
    #                 Arr = Arr.concatenate(Arrays[label])
    #             except:
    #                 pass
    #         countsList[x]=(Arr.completeness())
    #         x+= dx
    #    # return minimal for max
    #     L = []
    #     for key in countsList:
    #         if countsList[key]>0.98:
    #             L.append(key)
    #     L.sort()
    #     return L[0]

      
    def merge(self, anomFlag, thr):
        FlatC = hierarchy.fcluster(self.Tree, thr, criterion='distance')
        Log = open(self.CurrentDir+'/.cc_cluster.log', 'a')
        counter=collections.Counter(FlatC)
        Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
        Process = True
#change checkboxes to standard variables
        if Process:
            ToProcess = [Best]    
        else:
            ToProcess = set(Clusters)
            for key in ToProcess:
                if counter[key]==1:
                    ToProcess = [x for x in ToProcess if x != key]



#Processing pipeline, 
#Does all the XSCALE run
        for x in ToProcess:
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
            if cluster in ToProcess:
                OUT = open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/XSCALE.INP'%(float(thr),cluster,anomFlag), 'a')
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),cluster,anomFlag), 'a')
                print ('INPUT_FILE= ../%s'%(filename), file=OUT)
                #print ('INCLUDE_RESOLUTION_RANGE=20, 1.8', file=OUT)
                print ('MINIMUM_I/SIGMA= 0', file=OUT)
                print ('XDSIN ../%s'%(filename), file= Pointless)
                OUT.close()
                Pointless.close()
        #optional run of XSCALE

        newProcesses=[]
        for x in ToProcess:
            if [thr,x, anomFlag] not in  self.alreadyDone:
                self.createDendrogram(thr)
                plt.savefig(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/Dendrogram.png'%(float(thr),x,anomFlag))
                P= subprocess.Popen('xscale_par',cwd=self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/'%(float(thr), x, anomFlag))     
                P.wait()
                print('Cluster, %s , %s , %s'%(float(thr),x, anomFlag), file=Log)             
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag), 'a')
                print('COPY \n bg\n TOLERANCE 4 \n eof', file= Pointless)
                Pointless.close()
                st = os.stat(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag ))
                os.chmod(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(float(thr),x,anomFlag ), st.st_mode | 0o111)              
                newProcesses.append([thr,x, anomFlag])


                
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
