import sys

from PyQt5.QtWidgets import QApplication

if not __name__ == "__main__":
    from .Clipper import Clipper
    from .Model import Entity
else:
    from lib.clipper2.lib.Clipper import Clipper
    from lib.clipper2.lib.Model import Entity


class Ctrl:
    def __init__(self):
        self.clipper = Clipper()
        self.entity = Entity()
        self.init_controller()

    def init_controller(self):
        self.init_clipper_controller()

    def start(self):
        self.clipper.show()

    def init_clipper_controller(self):
        def resizeEvent(*args):
            self.clipper.container0.resize(self.clipper.width(), self.clipper.height())
            self.clipper.widget_button_show_rightsidebar.move(self.clipper.geometry().width() - 20,
                                                              self.clipper.geometry().height() / 2)

            pass

        self.clipper.resizeEvent = resizeEvent


if __name__ == "__main__":
    app = QApplication(sys.argv)
    controller = Ctrl()
    controller.start()

    sys.exit(app.exec_())
