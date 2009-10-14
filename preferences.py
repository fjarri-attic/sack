from PyQt4 import QtGui, QtCore

from appglobals import *


class Preferences(QtGui.QDialog):

	def __init__(self):
		QtGui.QDialog.__init__(self)

		self.setWindowTitle(app.translate('Preferences', 'Preferences'))

		available_languages = self._findTranslationFiles()
		lang_from_config = app.settings.value('ui/language')
		self._language = QtGui.QComboBox()
		for i, e in enumerate(available_languages):
			short_name, full_name = e
			self._language.insertItem(i, full_name, short_name)
			if short_name == lang_from_config:
				self._language.setCurrentIndex(i)
		self._language.currentIndexChanged.connect(self._languageChanged)


		layout = QtGui.QVBoxLayout()
		layout.addWidget(self._language)

		self.setLayout(layout)

	@QtCore.pyqtSlot(int)
	def _languageChanged(self, index):
		short_name = self._language.itemData(index)
		app.settings.setValue('ui/language', short_name)
		app.inst.reloadTranslator.emit()

	def _findTranslationFiles(self):
		translations_dir = QtCore.QDir(':/translations')
		file_names = translations_dir.entryList(['sack.*.qm'],
			QtCore.QDir.Files, QtCore.QDir.Name)

		translator = QtCore.QTranslator()

		languages = []
		for file_name in file_names:
			translator.load(translations_dir.filePath(file_name))
			full_name = translator.translate('Language', 'Full Name')
			short_name = translator.translate('Language', 'Short Name')
			languages.append((short_name, full_name))

		return languages

	def closeEvent(self, e):
		QtGui.QDialog.closeEvent(self, e)
		app.inst.closePreferencesWindow.emit()
