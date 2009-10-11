from PyQt4 import QtGui, QtCore

class DBWindow(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)

		tabbar = QtGui.QTabWidget()
		tabbar.addTab(QtGui.QWidget(), 'first')
		tabbar.addTab(QtGui.QWidget(), 'second')

		tags_dock = QtGui.QDockWidget('tags')
		shelf_dock = QtGui.QDockWidget('shelf')

		self.setCentralWidget(tabbar)
		self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tags_dock)
		self.addDockWidget(QtCore.Qt.RightDockWidgetArea, shelf_dock)

		self.resize(500, 300)
		self.setWindowTitle('Database')

		self.statusBar().showMessage('Ready')
