from PyQt5.QtWidgets import QApplication

from lib.PagePicker import PagePicker
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    q = PagePicker()
    sys.exit(app.exec_())
