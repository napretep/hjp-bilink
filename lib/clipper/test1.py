from PyQt5.QtWidgets import QApplication

from lib.PagePicker import PagePicker
from lib.ConfigTable import ConfigTable
import sys
from lib.fitz import fitz

if __name__ == '__main__':
    doc: "fitz.Document" = fitz.open(
        r"C:\Users\Administrator\Downloads\Fishv3216\Fish-v3216\kpdf\2021年浙江师范大学教师教育学院822计算机与网络之计算机网络技术与应用考研冲刺模拟五套题.pdf")

    # app = QApplication(sys.argv)
    # # q = ConfigTable()
    # q = PagePicker(pageNum=0,
    #                pdfDirectory=r"C:\Users\Administrator\Downloads\Functional Python Programming Discover the power of functional programming, generator functions, lazy evaluation, the built-in itertools library, and monads by Steven F. Lott (z-lib.org).pdf")
    # q.start(0)
    # sys.exit(app.exec_())
