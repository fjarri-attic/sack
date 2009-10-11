import sys
from PyQt4 import QtGui, QtCore

from dbwindow import DBWindow

app = QtGui.QApplication(sys.argv)
main = DBWindow()

main.show()

menubar = QtGui.QMenuBar()
file = menubar.addMenu('&File')
edit = menubar.addMenu('&Edit')
tools = menubar.addMenu('&Tools')

sys.exit(app.exec_())
