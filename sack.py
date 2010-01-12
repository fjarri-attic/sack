import sys
import qthelpers
import application

qthelpers.initLog()
qthelpers.importResources()
app = application.Application(sys.argv)
sys.exit(app.exec_())
