import os.path
from configparser import RawConfigParser

_MAIN_CONFIG_NAME = 'config.ini'
_LANG_FOLDER_NAME = 'lang'

class _ConfigWrapper:

	def __init__(self, filename):
		self._config_obj = RawConfigParser()
		self._config_obj.read(filename)

	def __getattr__(self, name):
		return _SectionWrapper(self._config_obj, name)

class _SectionWrapper:
	def __init__(self, config_obj, section_name):
		self._config_obj = config_obj
		self._section_name = section_name

	def __getattr__(self, name):
		return self._config_obj.get(self._section_name, name)

options = None
lang = None

def init(dir=None):

	global options, lang

	if dir is None:
		dir = os.path.dirname(os.path.abspath(__file__))

	options = _ConfigWrapper(os.path.join(dir, _MAIN_CONFIG_NAME))

	lang_name = options.ui.language + ".ini"
	lang = _ConfigWrapper(os.path.join(dir, _LANG_FOLDER_NAME, lang_name))
