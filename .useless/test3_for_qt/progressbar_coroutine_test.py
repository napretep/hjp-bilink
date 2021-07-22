import sys, asyncio
from PyQt5.QtWidgets import QApplication, \
    QPushButton, QProgressBar, QVBoxLayout, QDialog
from PyQt5.QtCore import pyqtSignal


class QProgressBarExample(QDialog):
    on_progress = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.progressbar_obj1 = QProgressBar(self)
        self.button_obj1 = QPushButton(u'start', self)
        v = QVBoxLayout(self)
        list(map(lambda x: v.addWidget(x), [self.progressbar_obj1, self.button_obj1]))
        self.setLayout(v)
        self.on_progress.connect(self.progressbar_obj1.setValue)
        # self.button_obj1.clicked.connect(lambda :)
        self.show()
        asyncio.run(self.on_button_clicked())

    async def on_button_clicked(self):
        await (progress_worker(self.on_progress))


async def progress_worker(progress_signal):
    for i in range(101):
        progress_signal.emit(i)
        await asyncio.sleep(0.1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = QProgressBarExample()
    sys.exit(app.exec_())
