#! /users/gsantoni/Downloads/cctbx_build/bin/libtbx.python
from __future__ import print_function

__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 2015"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "0.2"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"


from numpy import arange, sin, pi
from PyQt4 import QtGui, QtCore
from math import sqrt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar



# implement the default mpl key bindings
from matplotlib.figure import Figure
from scipy.cluster import hierarchy
from scipy.spatial import distance
import collections
import operator
import sys
import scipy
from time import sleep
import os
import numpy as np
import subprocess
import shutil


from resultsTab import resultsTab
from summary import resultsSummary
from clustering import Clustering
import CalcClass

# Insert parse  to change the file path from command line

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i","--XSCALEfile", dest="XSCALEfile", default=None, help="XSCALE.LP from overall processing")
parser.add_argument("-o","--outname", dest="outname", default='Dendrogram', help="output dendogram file name")
parser.add_argument("-t", "--threshold", dest="threshold", help="Distance threshold for clustering")
parser.add_argument("-p", "--shell",action="store_true", dest="shell", default=False, help="Launch program in shell mode. Need to specify the threshold value")
parser.add_argument("-c", "--count",action="store_true", dest="count", default=False, help="Counts datasets in the biggest cluster and exit")
parser.add_argument("-e", "--estimation",action="store_true", dest="est", default=False, help="Tries to guess an optimal threshold value")
parser.add_argument("-f", dest="HKLlist", default= None ,  type=str, nargs='+', help='The list of refined structures to merge')
#Minimal for completeness
parser.add_argument("-m", dest="minimal", default= False , action="store_true" , help='Gives minimal threshold for completeness')

#parser.print_help()
args= parser.parse_args()

#Startup message

print("""ccCluster - HCA for protein crystallography 
G. Santoni and A. Popov, 2015
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



if args.XSCALEfile is None:
    if args.HKLlist is None:
        print('No input specified, calculating Correlation coefficients')
        print('this might take a while')
        CalcClass.ccCalc()
        correlationFile='ccClusterLog.txt'
    else:
        print("Calculating CC between specified files")
        CalcClass.ccList(args.HKLlist)
        correlationFile='ccClusterLog.txt'
else:
    correlationFile=args.XSCALEfile



CC = Clustering(correlationFile)
Tree = CC.avgTree()
etiquets=CC.createLabels()
threshold = CC.thrEstimation()


#define Class for gui main window
#tabs for result and summary are generated 
#through different modules

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        global Tree
        global threshold
        global etiquets
        self.counter = 1
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setWindowTitle("Cluster and merge")
        MainWindow.resize(1215, 1000)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.processedValues = []
        self.threshold = threshold
        self.CurrentDir = os.getcwd()
        self.etiquets= etiquets


###########
#Buttons Widget:
#to contain all the buttons and inputs
#to run clusterings
###########

        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.centralWidgetLayout= QtGui.QHBoxLayout(self.centralwidget)
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setMaximumSize(200, 191)
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.PlotButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.PlotButton.setObjectName(_fromUtf8("PlotButton"))
        self.PlotButton.clicked.connect(self.createDendrogram)

        self.verticalLayout.addWidget(self.PlotButton)
        self.lineEdit = QtGui.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.verticalLayout.addWidget(self.lineEdit)
        self.checkBox = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.verticalLayout.addWidget(self.checkBox)
        self.anomBox = QtGui.QCheckBox(self.verticalLayoutWidget)
        self.anomBox.setChecked(True)
        self.checkBox.setObjectName(_fromUtf8("anomBox"))
        self.verticalLayout.addWidget(self.anomBox)
        self.processButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.processButton.setObjectName(_fromUtf8("processButton"))
        self.processButton.clicked.connect(self.processClusters)
        self.verticalLayout.addWidget(self.processButton)
        self.summaryButton= QtGui.QPushButton(self.verticalLayoutWidget)
        self.summaryButton.setObjectName(_fromUtf8("summaryButton"))
        self.summaryButton.clicked.connect(self.showSummary)
        self.verticalLayout.addWidget(self.summaryButton)
        
        self.centralWidgetLayout.addWidget(self.verticalLayoutWidget)

###########
#Tab Widget:
#to show Dendrogram and clustering results
#Each Run of XSCALE will create a new tab for results
###########

        self.verticalLayoutWidget_2 = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setMinimumSize(1020, 410)
        #self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(160, 0, 1021, 411))
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tabWidget = QtGui.QTabWidget(self.verticalLayoutWidget_2)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.Dendrogram = plt.figure()

        self.TreeCanvas = FigureCanvas(self.Dendrogram)
        cid = self.Dendrogram.canvas.mpl_connect('button_press_event', self.getThreshold)
        self.TreeBar= NavigationToolbar(self.TreeCanvas, self)
        self.createDendrogram()

        self.plotTab = QtGui.QWidget()
        self.plotTabLayout=QtGui.QVBoxLayout(self.plotTab)
        self.plotTabLayout.addWidget(self.TreeBar)
        self.plotTabLayout.addWidget(self.TreeCanvas)
        self.plotTab.setObjectName(_fromUtf8("plotTab"))
        self.tabWidget.addTab(self.plotTab, _fromUtf8("Dendrogram"))
        self.verticalLayout_2.addWidget(self.tabWidget)
        self.centralWidgetLayout.addWidget(self.verticalLayoutWidget_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        #self.menubar.setGeometry(QtCore.QRect(0, 0, 1215, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.statusbar.showMessage('Ready!')
        MainWindow.setStatusBar(self.statusbar)
##########
#Show previous results
# to be removed from the setupUi class
###########

        self.alreadyDone= []
        if os.path.isfile(os.getcwd()+'/.cc_cluster.log'):
            with open(os.getcwd()+'/.cc_cluster.log') as log:
                for line in log:
                    L = line.split(',')
                    try :
                        self.tabWidget.addTab(resultsTab(float(L[1]), L[2].strip(), L[3].strip(), L[4]),L[1]+L[2]+L[3].strip())
                        self.alreadyDone.append([L[1], L[2].strip(), L[3].strip()])

                    except:
                        self.tabWidget.addTab(resultsTab(float(L[1]), L[2].strip(), L[3].strip(), 'unk'),L[1]+L[2]+L[3].strip())
                        self.alreadyDone.append([L[1], L[2].strip(), L[3].strip()])

# L[1] = threshold, L[2]=number, L[3] = anomFlag

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Cluster and Merge", None))
        self.PlotButton.setText(_translate("MainWindow", "Plot Dendrogram", None))
        self.checkBox.setText(_translate("MainWindow", "Merge only biggest cluster", None))
        self.anomBox.setText(_translate("MainWindow", "Anomalous data", None))
        self.processButton.setText(_translate("MainWindow", "Merge clusters", None))
        self.summaryButton.setText(_translate("MainWindow", "Summary", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.TreeCanvas), _translate("MainWindow", "Dendrogram", None))
        #self.tabWidget.setTabText(self.tabWidget.indexOf(self.clusterTab), _translate("MainWindow", "Clustering result", None))
    def showSummary(self):
        self.sum = resultsSummary()
        self.sum.show()

    def createDendrogram(self):
        X = hierarchy.dendrogram(Tree, color_threshold=self.threshold)
        #self.textOutput.append('Plotted Dendrogram. Colored at a %s threshold for distance'%(threshold))
        self.TreeCanvas.draw()


    def getThreshold(self,event):
        self.coord = 0
        if event.ydata != None:
            self.coord = event.ydata
            #self.textOutput.append('Threshold is %s'%(self.coord))
            #self.thr = event.ydata
            self.threshold= float('%.2f'%(event.ydata))
            self.createDendrogram()
            self.statusbar.showMessage('New threshold value: %.2f'%(self.threshold))

    def onChanged(self, text):
        self.threshold = float(text)

    def processClusters(self):
        Log = open(self.CurrentDir+'/.cc_cluster.log', 'a')

        Clusters = hierarchy.fcluster(Tree, self.threshold, criterion='distance')
        counter=collections.Counter(Clusters)
        Best = max(counter.iteritems(), key=operator.itemgetter(1))[0]
        #Chose if process all or just biggest cluster

        if self.checkBox.isChecked():
            ToProcess = [Best]    
            self.statusbar.showMessage('Processing the best cluster. It contains %s datasets'%(counter[Best]))
        else:
            ToProcess = set(Clusters)
            for key in ToProcess:
                if counter[key]==1:
                    ToProcess = [x for x in ToProcess if x != key]

        #flag anomalus process or not
        if self.anomBox.isChecked():
            self.anomFlag= 'ano'
        else:
            self.anomFlag= 'no_ano'

        # Delete previous processings and create working directories
        for x in ToProcess:
            if [self.threshold,x, self.anomFlag] not in  self.alreadyDone:
                os.mkdir(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s'%(self.threshold,x, self.anomFlag))
                Xscale=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/XSCALE.INP'%(self.threshold,x, self.anomFlag), 'a')
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(self.threshold,x,self.anomFlag ), 'a')
                print('OUTPUT_FILE=scaled.hkl',file=Xscale)
                print('MERGE= TRUE', file=Xscale)
                print('pointless hklout clustered.mtz << eof', file=Pointless)
                if self.anomBox.isChecked():
                    print('FRIEDEL\'S_LAW= FALSE', file=Xscale)
                Xscale.close()
                Pointless.close()

        for cluster, filename in zip(Clusters,self.etiquets):
            if cluster in ToProcess:
                OUT = open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/XSCALE.INP'%(self.threshold,cluster,self.anomFlag), 'a')
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(self.threshold,cluster,self.anomFlag), 'a')
                print ('INPUT_FILE= ../%s'%(filename), file=OUT)
                #print ('INCLUDE_RESOLUTION_RANGE=20, 2', file=OUT)
                print ('MINIMUM_I/SIGMA= 0', file=OUT)
                print ('XDSIN ../%s'%(filename), file= Pointless)
                OUT.close()
                Pointless.close()
        #optional run of XSCALE
        
        for x in ToProcess:
            #newProcesses=[]
            if [self.threshold,x, self.anomFlag] not in  self.alreadyDone:
                self.statusbar.showMessage('XSCALE is processing cluster %.2f %s %s/'%(self.threshold, x,self.anomFlag))
                plt.savefig(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/Dendrogram.png'%(self.threshold,x,self.anomFlag))
                process = QtCore.QProcess(self)
                process.setWorkingDirectory(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/'%(self.threshold, x,self.anomFlag))
                process.start('xscale_par')
                print('Cluster, %s , %s , %s, %s'%(self.threshold,x, self.anomFlag, counter[x]), file=Log)             
                Pointless=open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(self.threshold,x,self.anomFlag), 'a')
                print('COPY \n RESOLUTION 20 2.0 \n TOLERANCE 4 \n eof', file= Pointless)
                Pointless.close()
                #newProcesses.append([self.threshold,x, self.anomFlag])
                L=[self.threshold,x, self.anomFlag, counter[x]]
            process.waitForFinished()
            process.exitStatus()
            sleep(0.5)
            st = os.stat(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(self.threshold,x,self.anomFlag ))
            os.chmod(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/launch_pointless.sh'%(self.threshold,x,self.anomFlag ), st.st_mode | 0o111)
            self.tabWidget.addTab(resultsTab(float(L[0]), L[1], L[2], L[3]), ('%.2f %s %s')%(float(L[0]), L[1], L[2]))
            self.alreadyDone.append([L[0], L[1], L[2]])
        self.statusbar.showMessage('Ready!')
        
        # for L in newProcesses:
        #     self.tabWidget.addTab(resultsTab(float(L[0]), L[1], L[2]), ('%.2f %s %s')%(float(L[0]), L[1], L[2]))
        #     self.alreadyDone.append([L[0], L[1], L[2]])



class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QMainWindow.__init__(self, parent, f)

        self.setupUi(self)


#Main part of the program
#with the different options, we can chose 
# to process through the shell,
#count the multiplicity of the highest cluster
#run the interface

def main():
    if args.threshold:
        threshold = args.threshold
    elif args.minimal:
        threshold = CC.minimalForCompleteness()
    else:
        threshold= CC.thrEstimation()

    if args.shell:
        CC.checkMultiplicity(threshold) 
        CC.merge('no_ano',threshold)
    elif args.count:
        CC.checkMultiplicity(threshold)
    elif args.est:
        a = CC.thrEstimation()
        print(a)
    else:
        app = QtGui.QApplication(sys.argv)
        ex = MainWindow()
        ex.show()
        sys.exit(app.exec_())      

if __name__== '__main__':
    main()
