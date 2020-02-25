from __future__ import print_function
__author__ = "Gianluca Santoni"
__copyright__ = "Copyright 20150-2019"
__credits__ = ["Gianluca Santoni, Alexander Popov"]
__license__ = ""
__version__ = "1.0"
__maintainer__ = "Gianluca Santoni"
__email__ = "gianluca.santoni@esrf.fr"
__status__ = "Beta"


from PyQt5 import QtGui, QtCore, QtWidgets
import os, sys

from textSummary import generateLogSummary
#a class to generate the results widget.
#will be used as a tab in the main window

class resultsSummary(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.resultsLayout= QtWidgets.QVBoxLayout(self)
        self.setGeometry(100, 100, 500, 500)
        self.Workdir= os.getcwd()
#the title of the results summary
        self.Title=QtWidgets.QLabel(self)
        self.Title.setText('Summary of the results')
        self.resultSummary= QtWidgets.QTextEdit()
        self.resultsLayout.addWidget(self.Title)
        self.resultsLayout.addWidget(self.resultSummary)
        self.setText()

    def setText(self):
#the text edit to sum up results
        generateLogSummary(self.Workdir+'/.cc_cluster.log')
        text = open(self.Workdir+'/.cc_summary.txt').read()
        self.resultSummary.setPlainText(text)
        print(text)

def main():
#Can be launched alone to viasualize the results
#without loading all the program
    app = QtWidgets.QApplication(sys.argv)
    ex = resultsSummary()
    ex.show()
    sys.exit(app.exec_())      

if __name__== '__main__':
    main()
