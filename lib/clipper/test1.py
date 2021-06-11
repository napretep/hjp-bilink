from PyQt5.QtWidgets import QApplication

from lib.tools import objs
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    q = objs.ConfigTable()
    sys.exit(app.exec_())
