# -*- coding: utf-8 -*-
"""
__project_ = 'hjp-bilink'
__file_name__ = 'compatible_import.py'
__author__ = '十五'
__email__ = '564298339@qq.com'
__time__ = '2021/8/9 11:46'
为了考虑兼容性而统一处理他们
目前2022年6月29日02:32:11,49版没有问题.用的是3.8的Python
54的Qt6和5版用的都是3.9.7的python

"""


def pointVersion():
    from anki.buildinfo import version
    return int(version.split(".")[-1])

class Utils:
    """一些兼容性工具"""
    @staticmethod
    def isQt6():
        try:
            import PyQt6
            return True
        except:
            return False
    pass


class Anki:
    """"""

    isQt6 = Utils.isQt6()
    from anki import notes,cards,utils,hooks
    class Lang:
        from anki import utils, lang
        if pointVersion() > 49:
            currentLang = lang.current_lang
        else:
            currentLang = lang.currentLang
    import aqt
    if isQt6:
        import PyQt6 as pyqt
    else:
        import PyQt5 as pyqt
    pass




if Anki.isQt6 :
    from PyQt6.QtCore import QSettings
    from PyQt6.QtWidgets import QAbstractItemView,QGraphicsView,QGraphicsRectItem,QMessageBox,QInputDialog,QWidget
    QSettings_NativeFormat = QSettings.Format.NativeFormat
    class DragDropMode:
        NoDragDrop=QAbstractItemView.DragDropMode.NoDragDrop
        InternalMove = QAbstractItemView.DragDropMode.InternalMove
        DragDrop =  QAbstractItemView.DragDropMode.DragDrop
    class SelectMode:
        ExtendedSelection = QAbstractItemView.SelectionMode.ExtendedSelection
        SingleSelection = QAbstractItemView.SelectionMode.SingleSelection
        NoSelection = QAbstractItemView.SelectionMode.NoSelection
    class dropIndicatorPosition:
        OnItem = QAbstractItemView.DropIndicatorPosition.OnItem
        OnViewport = QAbstractItemView.DropIndicatorPosition.OnViewport
        BelowItem = QAbstractItemView.DropIndicatorPosition.BelowItem
        AboveItem = QAbstractItemView.DropIndicatorPosition.AboveItem
    class ViewportUpdateMode:
        FullViewportUpdate =QGraphicsView.ViewportUpdateMode.FullViewportUpdate

    class DragMode:
        ScrollHandDrag = QGraphicsView.DragMode.ScrollHandDrag
        RubberBandDrag = QGraphicsView.DragMode.RubberBandDrag
        NoDrag = QGraphicsView.DragMode.NoDrag

    class QGraphicsRectItemFlags:
        ItemIsMovable = QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable
        ItemIsSelectable = QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        ItemSendsGeometryChanges = QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges

else:
    from PyQt5.QtCore import QSettings
    from PyQt5.QtWidgets import QAbstractItemView,QGraphicsView,QGraphicsRectItem,QMessageBox,QInputDialog,QWidget
    QSettings_NativeFormat = QSettings.NativeFormat
    class DragDropMode:
        NoDragDrop = QAbstractItemView.NoDragDrop
        InternalMove = QAbstractItemView.InternalMove
        DragDrop = QAbstractItemView.DragDrop
    class SelectMode:
        ExtendedSelection = QAbstractItemView.ExtendedSelection
        SingleSelection = QAbstractItemView.SingleSelection
        NoSelection = QAbstractItemView.NoSelection
    class dropIndicatorPosition:
        OnItem = QAbstractItemView.OnItem
        OnViewport = QAbstractItemView.OnViewport
        BelowItem = QAbstractItemView.BelowItem
        AboveItem = QAbstractItemView.AboveItem

    class DragMode:
        ScrollHandDrag = QGraphicsView.ScrollHandDrag
        RubberBandDrag = QGraphicsView.RubberBandDrag
        NoDrag = QGraphicsView.NoDrag
    class ViewportUpdateMode:
        FullViewportUpdate = QGraphicsView.FullViewportUpdate
    class QGraphicsRectItemFlags:
        ItemIsMovable = QGraphicsRectItem.ItemIsMovable
        ItemIsSelectable = QGraphicsRectItem.ItemIsSelectable
        ItemSendsGeometryChanges = QGraphicsRectItem.ItemSendsGeometryChanges

mw=Anki.aqt.mw