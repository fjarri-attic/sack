import sys

import application
import loghelpers
import sack_qrc

loghelpers.init()
app = application.Application(sys.argv)
sys.exit(app.exec_())
