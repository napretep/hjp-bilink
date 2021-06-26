from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QToolButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt


class CardinfosPreviewer(QDialog):
    pass


class CardinfosExecutor(QDialog):
    pass


class CardinfosPreviewConfirm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.button_ok = QToolButton(self)
        self.button_no = QToolButton(self)
        self.question_label = QLabel(self)
        self.init_UI()
        # self.show()

    def init_UI(self):
        self.setWindowFlag(Qt.Tool)
        self.question_label.setText("执行操作前是否预览卡片?\ndo you want to preview the card infos before execution?")
        self.button_ok.setText("ok")
        self.button_no.setText("no")
        v_box = QVBoxLayout(self)
        h_box = QHBoxLayout()
        h_box.setAlignment(Qt.AlignRight)
        h_box.addWidget(self.button_ok)
        h_box.addWidget(self.button_no)
        v_box.addWidget(self.question_label)
        v_box.addLayout(h_box)
        self.setLayout(v_box)

    def init_events(self):
        self.button_no.clicked.connect(self.on_button_no_clicked_handle)
        self.button_ok.clicked.connect(self.on_button_ok_clicked_handle)

    def on_button_no_clicked_handle(self):
        print("execute")
        self.close()

    def on_button_ok_clicked_handle(self):
        print("preview")
        self.close()

    pass
