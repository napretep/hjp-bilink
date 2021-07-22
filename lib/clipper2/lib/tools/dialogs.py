from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QSpinBox, QTextEdit
from . import objs


class ClipboxInfo(QDialog):
    def __init__(self, info, clipbox=None, callback: "list[callable,callable,callable]" = None):
        super().__init__(clipbox)
        self.info: "dict" = info
        self.QA_spinbox = QSpinBox(self)
        self.textQA_spinbox = QSpinBox(self)
        self.text_ = QTextEdit(self)
        self.init_UI()
        self.callback = callback
        self.__event = {
            self.QA_spinbox.valueChanged: callback[0],
            self.textQA_spinbox.valueChanged: callback[1],
            self.text_.textChanged: self.on_text_changed
        }
        self.__all_event = objs.AllEventAdmin(self.__event)
        self.__all_event.bind()

    def on_text_changed(self):
        value = self.text_.toPlainText()
        self.callback[2](value)

    def init_UI(self):
        change_li = ["QA", "textQA", "text_"]
        # unchangeli = self.info.keys()
        f_layout = QFormLayout(self)
        for item in self.info.keys():
            if item not in change_li:
                f_layout.addRow(item, QLabel(str(self.info[item])))
        self.QA_spinbox.setValue(self.info["QA"])
        self.textQA_spinbox.setValue(self.info["textQA"])
        self.text_.setPlainText(self.info["text_"])
        f_layout.addRow("QA", self.QA_spinbox)
        f_layout.addRow("textQA", self.textQA_spinbox)
        f_layout.addRow("text", self.text_)
        self.setLayout(f_layout)
