import sys

from PyQt5.QtWidgets import QApplication
if __name__ == "__main__":
    pass
else:
    from . import exports

if __name__ == "__main__":
    from lib.Clipper import Clipper
    from lib.Model import Entity
    from lib.PagePicker import PagePicker

    e = Entity()
    app = QApplication(sys.argv)
    p = Clipper(entity=e)
    p.start()
    p.exec()

    sys.exit(app.exec_())
