import time

from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QBrush, QPen, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsLineItem, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem, \
    QFileDialog, QGraphicsPixmapItem

from lib.fitz import fitz


def pixmap_page_load(doc: "fitz.Document", pagenum, ratio=1):
    page: "fitz.Page" = doc.load_page(pagenum)  # 加载的是页面
    pix: "fitz.Pixmap" = page.getPixmap(matrix=fitz.Matrix(ratio, ratio))  # 将页面渲染为图片
    fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888  # 渲染的格式

    pageImage = QImage(pix.samples, pix.width, pix.height, pix.stride, fmt)
    pixmap = QPixmap()
    pixmap.convertFromImage(pageImage)  # 转为pixmap
    return QPixmap(pixmap)


class MyGraphicRect2(QGraphicsItem):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.setPos(self.x, self.y)
        self.color = QColor('red')

        self.setAcceptDrops(True)
        self.setCursor(Qt.OpenHandCursor)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setAcceptHoverEvents(True)

    def setColor(self, color):
        self.color = QColor(color)

    def boundingRect(self):
        return QRectF(self.x, self.y, self.width, self.height)

    def paint(self, painter, options, widget):
        painter.setPen(QPen(QColor('black')))
        painter.setBrush(self.color)
        painter.drawRect(self.x, self.y, self.width, self.height)


class MoveThread(QThread):
    s = pyqtSignal(int, int)

    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def run(self):
        doc = fitz.open(self.directory)

        for i in range(len(doc)):
            # pixmap = pixmap_page_load(doc,i)
            time.sleep(.05)
            self.s.emit(i, i)


class MyGraphicScene(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rect = QRectF(0, 0, 800, 800)
        self.Scene = QGraphicsScene(self.rect)
        self.View = QGraphicsView()
        self.View.setCacheMode(QGraphicsView.CacheNone)
        self.View.setDragMode(QGraphicsView.RubberBandDrag)
        self.sceneConfig()
        self.displayUI()

    def sceneConfig(self):
        self.Scene.setBackgroundBrush(QBrush(QColor('yellow'), Qt.SolidPattern))

        self.item1 = MyGraphicRect2(100, 100, 100, 100)
        self.Scene.addItem(self.item1)
        line = QGraphicsLineItem(80, 38, 84, 38)
        self.Scene.addItem(line)
        self.View.setScene(self.Scene)

    def updatePosition(self, x, y):
        doc = fitz.open(self.dir)
        Pixmap: "QPixmap" = pixmap_page_load(doc, x)
        item = QGraphicsPixmapItem(Pixmap)
        item.setFlag(QGraphicsItem.ItemIsSelectable, True)
        item.setFlag(QGraphicsItem.ItemIsMovable, True)
        item.setFlag(QGraphicsItem.ItemIsFocusable, True)
        item.setPos(x * 10, y * 10)
        self.Scene.addItem(item)
        # self.Scene.addItem(item1)

    def displayUI(self):
        print('Is scene active', self.Scene.isActive())
        self.dir, _ = QFileDialog.getOpenFileName(None, "选取文件", ".", "(*.pdf)")
        # directory = ''
        self.setCentralWidget(self.View)
        self.th = MoveThread(self.dir)
        self.th.s.connect(self.updatePosition)
        self.th.start()
        self.resize(1000, 1000)
        self.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    m = MyGraphicScene()

    sys.exit(app.exec_())
