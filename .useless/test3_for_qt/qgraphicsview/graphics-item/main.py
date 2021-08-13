import sys
import cgitb

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from scene import GraphicScene
from view import GraphicView

cgitb.enable(format("text"))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.scene = GraphicScene(self)
        self.view = GraphicView(self.scene, self)

        self.setMinimumHeight(500)
        self.setMinimumWidth(500)
        self.setCentralWidget(self.view)
        self.setWindowTitle("Graphics Demo")


def demo_run():
    app = QApplication(sys.argv)
    demo = MainWindow()
    # compatible with Mac Retina screen.
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # show up
    demo.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    demo_run()
