import sys
import time

from PyQt5.QtWidgets import QMainWindow, QApplication, \
    QPushButton, QProgressBar, QVBoxLayout, QDialog
from PyQt5.QtCore import QBasicTimer, pyqtSignal, QThread


class QProgressBarExample(QDialog):
    on_progress = pyqtSignal(object)
    on_progress_worker = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout(self)
        self.progressbar_obj1 = QProgressBar(self)
        self.startbutton = QPushButton(u'start', self)
        self.stopbutton = QPushButton("stop", self)
        self.on_progress.connect(self.progressbar_obj1.setValue)
        self.on_progress_worker.connect(progress_worker)
        self.startbutton.clicked.connect(self.on_button_clicked)
        self.stopbutton.clicked.connect(self.on_stop_clicked)
        vbox.addWidget(self.progressbar_obj1)
        vbox.addWidget(self.startbutton)
        vbox.addWidget(self.stopbutton)
        self.setLayout(vbox)
        self.setWindowTitle(u'QProgressBar')
        self.show()

    def on_stop_clicked(self):
        print("stopped")
        self.p.terminate()

    def on_button_clicked(self):
        self.p = Thread(self)
        self.p.start()


class Thread(QThread):
    on_stop = pyqtSignal()

    def __init__(self, superior: "QProgressBarExample"):
        super().__init__(superior)
        self.superior = superior
        self.on_stop.connect(self.on_stop_handle)

    def on_stop_handle(self):
        self.quit()

    def run(self):
        # self.superior.on_progress_worker.emit(self.superior.on_progress)
        # while 1:
        #     self.msleep(100)
        progress_worker(self.superior.on_progress)


def progress_worker(progress_signal: "pyqtSignal"):
    for i in range(101):
        progress_signal.emit(i)
        time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = QProgressBarExample()
    sys.exit(app.exec_())
