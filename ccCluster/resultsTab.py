<<<<<<< HEAD:ccCluster/resultsTab.py
=======
from __future__ import print_function

>>>>>>> master:resultsTab.py
__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 20150-2019"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"





from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# implement the default mpl key bindings


import sys
import os
import subprocess


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class resultsTab(QtWidgets.QWidget):

    def __init__(self, thr,cls, anom, num):
        QtWidgets.QWidget.__init__(self)
        self.CurrentDir= os.getcwd()
        self.plotList= []
        self.tabLayout= QtWidgets.QVBoxLayout(self)
        self.Picture= QtGui.QPixmap(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/Dendrogram.png'%(float(thr), cls, anom))
        self.ImageBox = QtWidgets.QLabel(self)
        self.ImageBox.setPixmap(self.Picture)
        self.ImageBox.setMaximumSize(400,150)
        self.ImageBox.setScaledContents(True)
        self.Title=QtWidgets.QLabel(self)
        self.Title.setText('Threshold %.2f, Cluster %s, %s, %s datasets'%(float(thr), cls, anom, num))
        self.Text= QtWidgets.QTextEdit()

    #self.LogFile=open(self.CurrentDir+'/cc_Cluster_%.2f_%s/XSCALE.LP'%(float(thr), cls)).read()
        self.statsPlot = Figure()
        self.Ax= self.statsPlot.add_subplot(111)
        self.statsCanvas = FigureCanvas(self.statsPlot)
        self.statsBar= NavigationToolbar(self.statsCanvas, self)
        self.statsCanvas.setMinimumSize(700, 500)

        with open(self.CurrentDir+'/cc_Cluster_%.2f_%s_%s/XSCALE.LP'%(float(thr), cls, anom), 'r') as LogFile:
            for line in LogFile:
                if line.strip().startswith('LIMIT'):
                    break
            for line in LogFile:
                break
            for line in LogFile:
                if line.strip().startswith('total'):
                    break
                self.plotList.append(line.split())
                self.Text.append(line.strip())
#        self.Text.setText(self.LogFile)

#Buttons to plot stats

        self.buttonBar = QtWidgets.QWidget()
        self.barLayout= QtWidgets.QHBoxLayout(self.buttonBar)

        self.ccVsR= QtWidgets.QPushButton()
        self.ccVsR.setText(_fromUtf8("Compl. vs Res"))
        self.ccVsR.clicked.connect(lambda:self.plotStats(0,4,"Compl. vs Res" ))

        self.compVsR= QtWidgets.QPushButton()
        self.compVsR.setText(_fromUtf8("cc vs Res"))
        self.compVsR.clicked.connect(lambda:self.plotStats(0,10,"cc vs Res" ))

        self.RobsVsR= QtWidgets.QPushButton()
        self.RobsVsR.setText(_fromUtf8("Robs vs Res"))
        self.RobsVsR.clicked.connect(lambda:self.plotStats(0,5, "Robs vs Res" ))

        self.IsigmaVsR= QtWidgets.QPushButton()
        self.IsigmaVsR.setText(_fromUtf8("I/sigmaI vs Res"))
        self.IsigmaVsR.clicked.connect(lambda:self.plotStats(0,8,"I/sigmaI vs Res" ))

        self.SanoVsR= QtWidgets.QPushButton()
        self.SanoVsR.setText(_fromUtf8("Sig. Ano. vs Res"))
        self.SanoVsR.clicked.connect(lambda:self.plotStats(0,12,"Sig. Ano. vs Res" ))

        self.barLayout.addWidget(self.ccVsR)
        self.barLayout.addWidget(self.compVsR)
        self.barLayout.addWidget(self.RobsVsR)
        self.barLayout.addWidget(self.SanoVsR)
        self.barLayout.addWidget(self.IsigmaVsR)

        self.tabLayout.addWidget(self.Title)
        self.tabLayout.addWidget(self.ImageBox)
        self.tabLayout.addWidget(self.Text)
        self.tabLayout.addWidget(self.buttonBar)
        self.tabLayout.addWidget(self.statsBar)
        self.tabLayout.addWidget(self.statsCanvas)
        
    def plotStats(self, res, value, title):
#        plt.xkcd()
        self.Ax.clear()
        plotDataX= []
        plotDataY= []
        for el in self.plotList:
            plotDataX.append(float(el[res])) 
            plotDataY.append(float(el[value].strip('*').strip('%')))
        self.Ax.plot(plotDataX, plotDataY, 'r-^')
        self.Ax.set_xlim(10,0)
        self.Ax.set_title(title)
        self.statsCanvas.draw()

