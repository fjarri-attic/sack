class SackError(Exception):
	pass

class ParserError(SackError):
	def __init__(self, message, starting_position, ending_position):
		self.starting_position = starting_position
		self.ending_position = ending_position
