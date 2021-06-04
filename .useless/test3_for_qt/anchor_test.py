from PyQt5.QtCore import QSizeF, Qt
from PyQt5.QtWidgets import (QApplication, QGraphicsAnchorLayout,
                             QGraphicsProxyWidget, QGraphicsScene, QGraphicsView, QGraphicsWidget,
                             QPushButton, QSizePolicy)


def createItem(minimum, preferred, maximum, name):
    w = QGraphicsProxyWidget()

    w.setWidget(QPushButton(name))
    w.setMinimumSize(minimum)
    w.setPreferredSize(preferred)
    w.setMaximumSize(maximum)
    w.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    return w


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 800, 480)

    minSize = QSizeF(30, 100)
    prefSize = QSizeF(210, 100)
    maxSize = QSizeF(300, 100)

    a = createItem(minSize, prefSize, maxSize, "A")
    b = createItem(minSize, prefSize, maxSize, "B")
    c = createItem(minSize, prefSize, maxSize, "C")
    d = createItem(minSize, prefSize, maxSize, "D")
    e = createItem(minSize, prefSize, maxSize, "E")
    f = createItem(QSizeF(30, 50), QSizeF(150, 50), maxSize, "F")
    g = createItem(QSizeF(30, 50), QSizeF(30, 100), maxSize, "G")

    l = QGraphicsAnchorLayout()
    l.setSpacing(0)

    w = QGraphicsWidget(None, Qt.Window)
    w.setPos(20, 20)
    w.setLayout(l)

    # Vertical.
    l.addAnchor(a, Qt.AnchorLeft, l, Qt.AnchorLeft)
    l.addAnchor(b, Qt.AnchorRight, l, Qt.AnchorRight)
    l.addAnchor(l, Qt.AnchorLeft)

    scene.addItem(w)
    scene.setBackgroundBrush(Qt.darkGreen)

    view = QGraphicsView(scene)
    view.show()

    sys.exit(app.exec_())
