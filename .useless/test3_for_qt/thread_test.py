import time

from PyQt5.QtCore import QRectF, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QColor, QBrush, QPen
from PyQt5.QtWidgets import QApplication, QGraphicsLineItem, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsItem


def pixmap_page_load(doc: "fitz.Document", pagenum, ratio=1, size=QSize(600, 800)):
    """从self.doc读取page,再转换为pixmap"""
    page: "fitz.Page" = doc.load_page(pagenum)  # 加载的是页面
    # print(ratio.__str__())
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
    s = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()

    def run(self):
        for i in range(1, 50):
            time.sleep(.01)
            self.s.emit(30, 0)


class MyGraphicScene(QMainWindow):
    def __init__(self):
        super().__init__()
        self.rect = QRectF(0, 0, 800, 800)
        self.Scene = QGraphicsScene(self.rect)
        self.View = QGraphicsView()
        self.View.setCacheMode(QGraphicsView.CacheNone)
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
        self.item1.moveBy(x, y)

    def displayUI(self):
        print('Is scene active', self.Scene.isActive())
        self.setCentralWidget(self.View)
        self.th = MoveThread()
        self.th.s.connect(self.updatePosition)
        self.th.start()
        self.resize(1000, 1000)
        self.show()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    m = MyGraphicScene()

    sys.exit(app.exec_())
