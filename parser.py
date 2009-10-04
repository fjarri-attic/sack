import unittest

def _tokenize(condition):
	"""
	Transform a string with condition to a list of tokens:
	(string, starting position, ending position, quoted)
	'quoted' is a boolean parameter, equal to True if the source of the token
	was a quoted string.
	"""

	# states
	INTERMEDIATE = 0
	READING_OPERATOR = 1
	READING_QUOTED_STRING = 2
	READING_UNQUOTED_STRING = 3
	READING_ESCAPED_CHARACTER = 4

	tokens = []
	state = INTERMEDIATE
	buffer = ""
	characters = list(reversed(condition))

	position = -1 # current cursor position in source string
	starting_position = 0 # position of current buffer's starting character in source string

	while len(characters) > 0:
		c = characters.pop()
		position += 1

		if state == INTERMEDIATE:
			if c in ['(', ')', '=', '~']:
				tokens.append((c, position, position, False))
			elif c in ['<', '>']:
				state = READING_OPERATOR
				starting_position = position
				buffer += c
			elif c == ' ' or c == '\t':
				continue
			else:
				if c == '"':
					state = READING_QUOTED_STRING
					starting_position = position
				else:
					state = READING_UNQUOTED_STRING
					starting_position = position
					buffer += c
		elif state == READING_OPERATOR:
			if c == '=':
				buffer += c
			else:
				characters.append(c)
				position -= 1
			tokens.append((buffer, starting_position, position, False))
			buffer = ""
			state = INTERMEDIATE
		elif state == READING_QUOTED_STRING:
			if c == '\\':
				state = READING_ESCAPED_CHARACTER
			elif c == '"':
				tokens.append((buffer, starting_position, position, True))
				buffer = ""
				state = INTERMEDIATE
			else:
				buffer += c
		elif state == READING_UNQUOTED_STRING:
			if c in [' ', '\t', '=', '<', '>', '~', ')', '(']:
				characters.append(c)
				position -= 1
				tokens.append((buffer, starting_position, position, False))
				buffer = ""
				state = INTERMEDIATE
			else:
				buffer += c
		elif state == READING_ESCAPED_CHARACTER:
			buffer += c
			state = READING_QUOTED_STRING

	if len(buffer) > 0:
		tokens.append((buffer, starting_position, position,
			(state == READING_QUOTED_STRING)))

	return tokens


class TokenizerTests(unittest.TestCase):

	def testTransformations(self):
		tests = {
			r'elem=1': [('elem', 0, 3, False), ('=', 4, 4, False), ('1', 5, 5, False)],
			r'elem="value"': [('elem', 0, 3, False), ('=', 4, 4, False),
				('value', 5, 11, True)],
			r'elem <= "va\"\\lue"': [('elem', 0, 3, False),
				('<=', 5, 6, False), ('va"\\lue', 8, 18, True)],
			r'(elem ~"va lue") and (elem2 >= 3.456)':
				[('(', 0, 0, False), ('elem', 1, 4, False), ('~', 6, 6, False),
				('va lue', 7, 14, True), (')', 15, 15, False), ('and', 17, 19, False),
				('(', 21, 21, False), ('elem2', 22, 26, False), ('>=', 28, 29, False),
				('3.456', 31, 35, False), (')', 36, 36, False)]
		}

		for s in tests:
			self.assertEqual(tests[s], _tokenize(s))

def suite():
	res = unittest.TestSuite()
	res.addTests(unittest.TestLoader().loadTestsFromTestCase(TokenizerTests))
	return res

if __name__ == "__main__":
	unittest.TextTestRunner().run(suite())
