"""
Main class for Database window
"""

from PyQt4 import QtGui, QtCore

import brain

from globals import *


@dynamically_translated
class DBWindow(QtGui.QMainWindow):

	def __init__(self, file_name, new_file):
		QtGui.QMainWindow.__init__(self)

		self.setWindowTitle(file_name)
		self._connection = brain.connect(None, file_name,
			open_existing=(0 if new_file else 1))

		tabbar = QtGui.QTabWidget()

		tabbar.setTabsClosable(True)
		tabbar.setUsesScrollButtons(True)
		tabbar.setMovable(True)

		tabwidget = QtGui.QWidget()

		tabbar.addTab(tabwidget, 'first')
		tabbar.addTab(QtGui.QWidget(), 'second')

		x = ObjectWidget('blablablablablablabla', tabwidget)
		x.move(0, 0)

		tags_dock = QtGui.QDockWidget()
		self.dynTr(tags_dock.setWindowTitle).translate('DBWindow', 'Tags')
		shelf_dock = QtGui.QDockWidget()
		self.dynTr(shelf_dock.setWindowTitle).translate('DBWindow', 'Shelf')

		self.setCentralWidget(tabbar)
		self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, tags_dock)
		self.addDockWidget(QtCore.Qt.RightDockWidgetArea, shelf_dock)

		self.resize(app.settings.value('dbwindow/width'),
			app.settings.value('dbwindow/height'))

		self.dynTr(self._setStatusBar).refresh()

	def _setStatusBar(self):
		self.statusBar().showMessage(app.translate('DBWindow', 'Ready'))


class ObjectWidget(QtGui.QLabel):

	def __init__(self, title, parent):
		QtGui.QLabel.__init__(self, "", parent)

		self._title = title
		self.setFrameStyle(QtGui.QFrame.StyledPanel + QtGui.QFrame.Plain)

		self._redraw()

	def _redraw(self):
		metrics = self.fontMetrics()
		height = metrics.height()

		symbols_num = app.settings.value('ui/object_widget_size')
		self.setMinimumWidth(metrics.width('a' * symbols_num))

		internal_width = self.rect().width()
		title = self._title
		if metrics.width(title) > internal_width:
			counter = len(title) - 1
			while metrics.width(title + "...", counter) > internal_width and counter > 0:
				counter -= 1
			title = title[:counter] + "..."

		self.setText(title)
