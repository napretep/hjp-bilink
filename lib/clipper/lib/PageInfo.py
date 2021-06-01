from .fitz import fitz
from .tools.funcs import pixmap_page_load

class PageInfo:
    def __init__(self,PDFpath,pagenum=0):
        self.doc=fitz.open(PDFpath)
        self.pagenum=pagenum
        self.pagepixmap=pixmap_page_load(self.doc,self.pagenum)

if __name__ == "__main__":
    pass