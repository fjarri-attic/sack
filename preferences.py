from PyQt4 import QtGui, QtCore

from globals import *


@dynamically_translated
class Preferences(QtGui.QDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.dynTr(self.setWindowTitle).translate('Preferences', 'Preferences')

		self._language = self._createTranslationsList()
		self._language.currentIndexChanged.connect(self._languageChanged)
		self.dynTr(self._setCurrentLocaleString).refresh()

		layout = QtGui.QVBoxLayout()
		layout.addWidget(self._language)

		self.setLayout(layout)

	@QtCore.pyqtSlot(int)
	def _languageChanged(self, index):
		short_name = self._language.itemData(index)
		app.settings.setValue('ui/language', short_name)
		app.inst.reloadTranslator.emit()

	def _setCurrentLocaleString(self):
		self._language.setItemText(0,
			app.translate('Preferences', 'Current locale'))

	def _createTranslationsList(self):

		language_list = QtGui.QComboBox()
		translation_files = findTranslationFiles()
		lang_from_config = app.settings.value('ui/language')

		languages = [(None, '')]
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
		app.inst.closePreferencesWindow.emit()
