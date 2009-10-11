import sys
from PyQt4 import QtGui, QtCore

from dbwindow import DBWindow

app = QtGui.QApplication(sys.argv)
main = DBWindow()

main.show()

class MainMenu(QtGui.QMenuBar):

	def __init__(self):
		QtGui.QMenuBar.__init__(self)

		file = self.addMenu('&File')
		edit = self.addMenu('&Edit')
		view = self.addMenu('&View')
		tools = self.addMenu('&Tools')

main_menu = MainMenu()

sys.exit(app.exec_())
