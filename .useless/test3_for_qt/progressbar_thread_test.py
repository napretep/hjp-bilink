import sys
import time

from PyQt5.QtWidgets import QMainWindow, QApplication, \
    QPushButton, QProgressBar
from PyQt5.QtCore import QBasicTimer, pyqtSignal, QThread


class QProgressBarExample(QMainWindow):
    on_progress = pyqtSignal(object)
    on_progress_worker = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.progressbar_obj1 = QProgressBar(self)
        self.progressbar_obj1.setGeometry(30, 40, 200, 25)
        self.button_obj1 = QPushButton(u'update in main', self)
        self.button_2 = QPushButton(u"update in thread", self)
        self.button_obj1.move(40, 80)
        self.on_progress.connect(self.progressbar_obj1.setValue)
        self.on_progress_worker.connect(progress_worker)
        self.button_obj1.clicked.connect(self.on_button_clicked)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle(u'QProgressBar')
        self.show()

    def on_button_clicked(self):
        p = Thread(self)
        p.start()


class Thread(QThread):
    on_stop = pyqtSignal()

    def __init__(self, superior: "QProgressBarExample"):
        super().__init__(superior)
        self.superior = superior
        self.on_stop.connect(self.on_stop_handle)

    def on_stop_handle(self):
        self.quit()

    def run(self):
        progress_worker(self.superior.on_progress)


def progress_worker(progress_signal):
    for i in range(101):
        progress_signal.emit(i)
        time.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = QProgressBarExample()
    sys.exit(app.exec_())
