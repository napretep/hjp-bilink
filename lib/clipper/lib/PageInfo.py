from PyQt5.QtGui import QPixmap

from .fitz import fitz
from .tools.funcs import pixmap_page_load


class PageInfo:
    def __init__(self, PDFpath: "str", pagenum=0, ratio=1):
        self.doc = fitz.open(PDFpath)
        self.pagenum = pagenum
        self.ratio = ratio
        self.pagepixmap = QPixmap(pixmap_page_load(self.doc, self.pagenum, ratio=ratio))

if __name__ == "__main__":
    pass