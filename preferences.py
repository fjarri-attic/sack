from PyQt4 import QtGui, QtCore

from appglobals import *

class Preferences(QtGui.QMainWindow):

	def __init__(self):
		QtGui.QMainWindow.__init__(self)

	def closeEvent(self, e):
		QtGui.QMainWindow.closeEvent(self, e)
		app.inst.closePreferencesWindow.emit()
