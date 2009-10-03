import unittest

def tokenize(condition):

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

	while len(characters) > 0:
		c = characters.pop()
		if state == INTERMEDIATE:
			if c in ['(', ')', '=', '~']:
				tokens.append(c)
			elif c in ['<', '>']:
				state = READING_OPERATOR
				buffer += c
			elif c == ' ' or c == '\t':
				continue
			else:
				if c == '"':
					state = READING_QUOTED_STRING
				else:
					state = READING_UNQUOTED_STRING
					buffer += c
		elif state == READING_OPERATOR:
			if c == '=':
				buffer += c
			else:
				characters.append(c)
			tokens.append(buffer)
			buffer = ""
			state = INTERMEDIATE
		elif state == READING_QUOTED_STRING:
			if c == '\\':
				state = READING_ESCAPED_CHARACTER
			elif c == '"':
				tokens.append(buffer)
				buffer = ""
				state = INTERMEDIATE
			else:
				buffer += c
		elif state == READING_UNQUOTED_STRING:
			if c in [' ', '\t', '=', '<', '>', '~', ')', '(']:
				characters.append(c)
				tokens.append(buffer)
				buffer = ""
				state = INTERMEDIATE
			else:
				buffer += c
		elif state == READING_ESCAPED_CHARACTER:
			buffer += c
			state = READING_QUOTED_STRING

	if len(buffer) > 0:
		tokens.append(buffer)

	return tokens


class TokenizerTests(unittest.TestCase):

	def testValidStrings(self):
		tests = {
			r'elem=1': ['elem', '=', '1'],
			r'elem="value"': ['elem', '=', 'value'],
			r'elem <= "va\"\\lue"': ['elem', '<=', 'va"\\lue'],
			r'(elem ~"va lue") and (elem2 >= 3.456)': ['(', 'elem', '~', 'va lue', ')',
				'and', '(', 'elem2', '>=', '3.456', ')']
		}

		for s in tests:
			self.assertEqual(tests[s], tokenize(s))

def suite():
	res = unittest.TestSuite()
	res.addTests(unittest.TestLoader().loadTestsFromTestCase(TokenizerTests))
	return res

if __name__ == "__main__":
	unittest.TextTestRunner().run(suite())
