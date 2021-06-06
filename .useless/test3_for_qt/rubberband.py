import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class ResizableRubberBand(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ResizableRubberBand, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.SubWindow)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(
            QtWidgets.QSizeGrip(self), 0,
            QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        layout.addWidget(
            QtWidgets.QSizeGrip(self), 0,
            QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)
        self._band = QtWidgets.QRubberBand(
            QtWidgets.QRubberBand.Rectangle, self)
        self._band.show()
        self.show()

    def resizeEvent(self, event):
        size = QtCore.QSize(3, 4)
        size.scale(self.size(), QtCore.Qt.KeepAspectRatio)
        self.resize(size)
        self._band.resize(self.size())


class MyView(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(MyView, self).__init__(parent)

        self.button = QtWidgets.QPushButton('Show Rubber Band')
        self.button.clicked.connect(self.handleButton)
        self.label = QtWidgets.QLabel()
        self.label.setScaledContents(True)
        self.label.setPixmap(QtGui.QPixmap('icono.png'))
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def handleButton(self):
        self.band = ResizableRubberBand(self.label)
        self.band.setGeometry(50, 50, 150, 300)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyView()
    window.show()
    window.setGeometry(100, 100, 500, 300)
    sys.exit(app.exec_())
