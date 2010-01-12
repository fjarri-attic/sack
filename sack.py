import sys
import qthelpers
import application

qthelpers.log.init()
qthelpers.importResources()
app = application.Application(sys.argv)
sys.exit(app.exec_())
