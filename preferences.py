"""
Application preferences window
"""

from PyQt4 import QtGui, QtCore

from logging import warning

import qthelpers
from qthelpers import app, dynamically_translated, TranslationsList


@dynamically_translated
class Preferences(QtGui.QDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.dynTr(self.setWindowTitle).translate('Preferences', 'Preferences')

		# Language setting control

		language_label = QtGui.QLabel()
		self.dynTr(language_label.setText).translate('Preferences', 'Language')

		language_list = qthelpers.TranslationsList(
			translate_current_locale=lambda: app.translate('Preferences', 'Current locale'))

		# Create window layout
		layout = QtGui.QGridLayout()
		layout.addWidget(language_label, 0, 0)
		layout.addWidget(language_list, 0, 1)

		# Block window resizing (its size will depend only on child widgets)
		layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

		self.setLayout(layout)

	def closeEvent(self, e):
		QtGui.QDialog.closeEvent(self, e)

		# notify application, that the preferences were closed
		# (so that it could release pointer to this window)
		app.inst.closePreferencesWindow()
