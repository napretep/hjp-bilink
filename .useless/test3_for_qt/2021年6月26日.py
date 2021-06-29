from PyQt5 import QtGui, QtCore
import os
import time

from PyQt5.QtWidgets import QWidget, QGridLayout, QProgressBar, QLabel, QMainWindow, QApplication


class MyBar(QWidget):
    i = 0
    style = ''' 
    QProgressBar
    {
        border: 2px solid grey;
        border-radius: 5px;
        text-align: center;
    }
    '''

    def __init__(self):
        super(MyBar, self).__init__()
        grid = QGridLayout()

        self.bar = QProgressBar()
        self.bar.setMaximum(1)
        self.bar.setMinimum(0)

        self.bar.setStyleSheet(self.style)

        self.bar.setRange(0, 0)

        self.label = QLabel("Nudge")
        self.label.setStyleSheet("QLabel { font-size: 20px }")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        grid.addWidget(self.bar, 0, 0)
        grid.addWidget(self.label, 0, 0)
        self.setLayout(grid)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.bar = MyBar()

        self.setCentralWidget(self.bar)


if __name__ == '__main__':
    app = QApplication([])
    win = MainWindow()
    win.show()
    QApplication.instance().exec_()
