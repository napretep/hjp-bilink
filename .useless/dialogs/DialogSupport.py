import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QApplication

alipayDir =fr"C:\Users\Administrator\AppData\Roaming\Anki2\addons21\hjp-bilink\lib\resource\pic\alipay.jpg"
weixinpayDir =fr"C:\Users\Administrator\AppData\Roaming\Anki2\addons21\hjp-bilink\lib\resource\pic\weixinpay.jpg"

class SupportDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.alipayPic = QPixmap(alipayDir)
        self.alipaylabel = QLabel(self)
        self.alipaylabel.setPixmap(self.alipayPic)
        self.alipaylabel.setScaledContents(True)
        self.alipaylabel.setMaximumSize(300,300)
        self.weixinpaylabel = QLabel(self)
        self.weixinpaylabel.setPixmap(QPixmap(weixinpayDir))
        self.weixinpaylabel.setScaledContents(True)
        self.weixinpaylabel.setMaximumSize(300,300)
        self.desclabel = QLabel(self)
        self.desclabel.setText("点赞、转发、分享给更多人，也是一种支持！")
        self.desclabel.setAlignment(Qt.AlignCenter)
        self.v_layout = QVBoxLayout(self)
        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.weixinpaylabel)
        self.h_layout.setStretch(0,1)
        self.h_layout.setStretch(1,1)
        self.h_layout.addWidget(self.alipaylabel)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addWidget(self.desclabel)
        self.setMaximumSize(400,400)
        self.setLayout(self.v_layout)
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    f = SupportDialog()
    f.show()
    sys.exit(app.exec_())

