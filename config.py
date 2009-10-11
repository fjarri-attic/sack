import os.path
from configparser import RawConfigParser

_MAIN_CONFIG_NAME = 'config.ini'

class _ConfigWrapper:
	def __init__(self, config_obj):
		self._config_obj = config_obj

	def __getattr__(self, name):
		return _SectionWrapper(self._config_obj, name)

class _SectionWrapper:
	def __init__(self, config_obj, section_name):
		self._config_obj = config_obj
		self._section_name = section_name

	def __getattr__(self, name):
		return self._config_obj.get(self._section_name, name)

_config_obj = RawConfigParser()
config = _ConfigWrapper(_config_obj)

def read(dir=None):
	if dir is None:
		dir = os.path.dirname(os.path.abspath(__file__))
	_config_obj.read(os.path.join(dir, _MAIN_CONFIG_NAME))
