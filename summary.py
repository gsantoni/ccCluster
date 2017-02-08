from PyQt4 import QtGui, QtCore
import os, sys

from textSummary import generateLogSummary
#a class to generate the results widget.
#will be used as a tab in the main window

class resultsSummary(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.resultsLayout= QtGui.QVBoxLayout(self)
        self.setGeometry(100, 100, 500, 500)
        self.Workdir= os.getcwd()
#the title of the results summary
        self.Title=QtGui.QLabel(self)
        self.Title.setText('Summary of the results')
        self.resultSummary= QtGui.QTextEdit()
        self.resultsLayout.addWidget(self.Title)
        self.resultsLayout.addWidget(self.resultSummary)
        self.setText()

    def setText(self):
#the text edit to sum up results
        generateLogSummary(self.Workdir+'/.cc_cluster.log')
        text = open(self.Workdir+'/.cc_summary.txt').read()
        self.resultSummary.setPlainText(text)
        print text

def main():
#Can be launched alone to viasualize the results
#without loading all the program
    app = QtGui.QApplication(sys.argv)
    ex = resultsSummary()
    ex.show()
    sys.exit(app.exec_())      

if __name__== '__main__':
    main()
