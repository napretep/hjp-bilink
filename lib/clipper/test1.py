from PyQt5.QtWidgets import QApplication

from lib.PagePicker import PagePicker
from lib.ConfigTable import ConfigTable
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # q = ConfigTable()
    q = PagePicker(pageNum=0,
                   pdfDirectory=r"C:\Users\Administrator\Downloads\Functional Python Programming Discover the power of functional programming, generator functions, lazy evaluation, the built-in itertools library, and monads by Steven F. Lott (z-lib.org).pdf")
    q.start(0)
    sys.exit(app.exec_())
