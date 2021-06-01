#test2 目标: 在scene中添加PDF页面

import sys,os

from PyQt5.QtGui import QImage, QPixmap
from fitz import fitz
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget, QGraphicsScene, QGraphicsView, \
    QGraphicsItem

def composer(*args):
    next = args[-1]
    for i in range(len(args)-1, 0, -1):
        next = args[i](next)

class PDFReader(QDialog):
    def __init__(self,PDFpath):
        super().__init__()
        self.doc = fitz.open(PDFpath) #加载的是文档
        self.scene = QGraphicsScene(self)
        self.pdfview = QGraphicsView(self.scene,self)
        for i in range(3):
            page = self.pixmap_page_load(i)
            self.scene.addPixmap(page).setFlag(QGraphicsItem.ItemIsMovable)

        self.pdfview.setGeometry(0,0,self.width(),self.height())
        self.resizeEvent=self.OnResize
        self.show()

    def OnResize(self,*args):
        self.pdfview.setGeometry(0, 0, self.width(), self.height())

    def pixmap_page_load(self,pagenum):
        page = self.doc.load_page(pagenum)  # 加载的是页面
        pix = page.getPixmap()  # 将页面渲染为图片
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888 #渲染的格式
        pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
        pixmap = QPixmap()
        pixmap.convertFromImage(pageImage) #转为pixmap
        return QPixmap(pixmap)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    reader = PDFReader("./resource/徐森林_数学分析_第8章.pdf")
    sys.exit(app.exec_())
