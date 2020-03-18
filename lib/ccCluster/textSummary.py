from __future__ import print_function
import os, sys


class generateLogSummary():
    def __init__(self, clustering):
        self.Workdir = os.getcwd()
        self.resultsList = []
        with open(clustering) as f:
            for line in f:
                L = line.split(',')
                self.resultsList.append([float(L[1]), L[2].strip(), L[3].strip()])

        self.generateLog()

#the key function, prepares the text 
#to be printed for the users

    def generateLog(self):
        simpleSummary = open(self.Workdir+'/.cc_summary.txt', 'w' )      

        #sort by completeness and print to file
        complList =   self.sortByPosition(self.populateList(), 6)
        c1 = complList[-1]
        c2 = complList[-2]
        c3 = complList[-3]
        complText=""" 

ccCluster
Created by Gianluca Santoni.

This is summary of your current clusterings:
The 3 most complete datasets are: 

%s_%s, with a completeness of %s in the highest resolution shell
%s_%s, with a completeness of %s in the highest resolution shell
%s_%s, with a completeness of %s in the highest resolution shell

            """%(c1[0],c1[1], c1[6], c2[0],c2[1], c2[6], c3[0],c3[1], c3[6])

        resolList = self.sortByPosition(self.populateList(), 2)
        r1 = resolList[0]
        r2 = resolList[1]
        r3 = resolList[2]

        resolText='''
Considering the cc as a cutoff condition, the highest resolution datasets are:

%s_%s, with a resolution of %s
%s_%s, with a resolution of %s
%s_%s, with a resolution of %s
''' %(r1[0],r1[1], r1[2], r2[0],r2[1], r2[2], r3[0],r3[1], r3[2])  

        print(complText, file= simpleSummary)
        print(resolText, file= simpleSummary)

    def populateList(self):
        highResStats = []
        for el in self.resultsList:
            highResStats.append(self.getMaxResolution(el[0], el[1], el[2]))
        return highResStats

    def getMaxResolution(self, thr, cl, ano):
        highResLine = []
        with open(self.Workdir+'/cc_Cluster_%.2f_%s_%s/XSCALE.LP'%(float(thr), cl, ano), 'r') as LogFile:
            for line in LogFile:
                if line.strip().startswith('LIMIT'):
                    break
            for line in LogFile:
                break
            for line in LogFile:
                if line.strip().startswith('total'):
                    break
                L = line.split()
                if '*' in L[10]:
                    highResLine = [s.strip('%') for s in L]
                    highResLine.insert(0, thr)
                    highResLine.insert(1, cl)
        return   highResLine

    def sortByPosition(self, list, stat):
        return sorted(list, key= lambda x:float(x[stat]))


def main():
    app = generateLogSummary('.cc_cluster.log')
    with open('.cc_summary.txt') as f:
        for line in f:
            print(line.strip())

if __name__=='__main__':
    main()
