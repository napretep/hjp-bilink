import sys,os

from PyQt5.QtGui import QImage, QPixmap
from fitz import fitz
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget


class PDFReader(QDialog):
    def __init__(self):
        super().__init__()

        doc = fitz.open("./resource/徐森林_数学分析_第8章.pdf") #加载的是文档
        page = doc.load_page(1) #加载的是页面
        pix = page.getPixmap() #将页面渲染为图片
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap()
        pixmap.convertFromImage(pageImage)
        self.pdfview = QLabel()
        self.pdfview.setPixmap(QPixmap(pixmap))
        self.pdfview.resize(pixmap.size())
        self.v_layout = QVBoxLayout(self)
        self.v_layout.addWidget(self.pdfview)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print("self.doc")
    reader = PDFReader()
    doc = fitz.open("./resource/徐森林_数学分析_第8章.pdf")  # 加载的是文档
    page = doc.load_page(0)  # 加载的是页面
    pix = page.getPixmap()  # 将页面渲染为图片

    print("self.doc.__str__()")
    sys.exit(app.exec_())
