"""
Application preferences window
"""

from PyQt4 import QtGui, QtCore

from globals import *


@dynamically_translated
class Preferences(QtGui.QDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.dynTr(self.setWindowTitle).translate('Preferences', 'Preferences')

		# Language setting control

		_language_label = QtGui.QLabel()
		self.dynTr(_language_label.setText).translate('Preferences', 'Language')

		self._language = self._createTranslationsList()
		self._language.currentIndexChanged.connect(self._languageChanged)
		self.dynTr(self._setCurrentLocaleString).refresh()

		# Create window layout

		layout = QtGui.QGridLayout()
		layout.addWidget(_language_label, 0, 0)
		layout.addWidget(self._language, 0, 1)

		# Block window resizing (its size will depend only on child widgets)
		layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)

		self.setLayout(layout)

	@QtCore.pyqtSlot(int)
	def _languageChanged(self, index):
		short_name = self._language.itemData(index)
		app.settings.setValue('ui/language', short_name)
		app.inst.reloadTranslator.emit()

	def _setCurrentLocaleString(self):
		"""
		Helper for dynamical translation which sets the name of
		first language list element.
		"""
		self._language.setItemText(0,
			app.translate('Preferences', 'Current locale'))

	def _createTranslationsList(self):
		"""
		Returns combobox, filled with available interface translations.
		Item data is a short name of the language, which serves as
		the key for searching this file later.
		"""

		language_list = QtGui.QComboBox()
		translation_files = findTranslationFiles()
		lang_from_config = app.settings.value('ui/language')

		languages = [(None, '')] # option for watching the current locale
		for short_name, full_name, _ in translation_files:
			languages.append((short_name, full_name))

		for i, e in enumerate(languages):
			short_name, full_name = e
			language_list.insertItem(i, full_name, short_name)
			if short_name == lang_from_config:
				language_list.setCurrentIndex(i)

		return language_list

	def closeEvent(self, e):
		QtGui.QDialog.closeEvent(self, e)

		# notify application, that the preferences were closed
		# (so that it could release pointer to this window)
		app.inst.closePreferencesWindow.emit()
