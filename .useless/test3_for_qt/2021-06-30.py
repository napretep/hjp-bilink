import sys
import subprocess
import time
import win32gui

from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMdiArea
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout


class Example(QMainWindow):

    def __init__(self):
        super().__init__()
        self.p = QProcess()
        self.layout = QVBoxLayout()
        self.mdi = QMdiArea()
        self.widget = QWidget()
        self.initUI()

    def initUI(self):
        import threading
        t = threading.Thread(target=self.runExe)
        t.start()

        hwnd1 = win32gui.FindWindowEx(0, 0, "CalcFrame", "计算器")
        start = time.time()
        while hwnd1 == 0:
            time.sleep(0.01)
            hwnd1 = win32gui.FindWindowEx(0, 0, "CalcFrame", "计算器")
            end = time.time()
            if end - start > 5:
                return
        window = QWindow.fromWinId(hwnd1)

        self.createWindowContainer(window, self)
        self.setGeometry(500, 500, 450, 400)
        self.show()

    @staticmethod
    def runExe():
        exePath = "C:\\Windows\\system32\\calc.exe"
        subprocess.Popen(exePath)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
