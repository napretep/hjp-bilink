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
import sys
from ..debugState import *
from typing import Union, Callable
# from . import G

try:
    from aqt import profiler
except:
    profiler = None


def pointVersion():
    from anki.buildinfo import version
    return int(version.split(".")[-1])


class Utils:
    """一些兼容性工具"""

    @staticmethod
    def isQt6():

        # if ISDEBUG and ISLOCALDEBUG:
        #     print("调试阶段可自己选择anki版本")
        #     return True

        try:
            import PyQt6
            return True
        except:
            return False

    pass


try:
    import aqt
    ISLOCAL = False
except:
    ISLOCAL = True

class Anki:
    """"""
    isQt6 = Utils.isQt6()
    print(f"是Qt6吗?{isQt6}")
    if not ISLOCAL:
        from anki import notes, cards, utils, hooks
        import aqt
        class Lang:
            from anki import utils, lang
            if pointVersion() > 49:
                currentLang = lang.current_lang
            else:
                currentLang = lang.currentLang
    else:
        from anki import notes, cards, utils, hooks
        class Lang:
            currentLang = None

        class aqt:
            mw = None

    pass

isMac = is_mac = sys.platform.startswith("darwin")
isWin=is_win = sys.platform.startswith("win32")
# also covers *BSD
isLin = not isMac and not isWin


# else:
mw = Anki.aqt.mw
from aqt.utils import tooltip, showInfo
from aqt.utils import saveGeom, restoreGeom, tr
from aqt import dialogs, AnkiQt, gui_hooks
from aqt.browser import Browser, SidebarItem, SidebarItemType, SidebarTreeView
from aqt.browser.previewer import \
    BrowserPreviewer, Previewer, MultiCardPreviewer
from aqt.editor import Editor, EditorWebView
from aqt.addcards import AddCards
from aqt.operations.card import set_card_deck
from aqt.reviewer import Reviewer, RefreshNeeded, V3CardInfo
from aqt.webview import AnkiWebView
from aqt.operations.scheduling import answer_card

# 兼容格式: classEnum.Name

# NEEDQT6 = ISQT6 if ISLOCALDEBUG else Anki.isQt6

if Utils.isQt6():
    from PyQt6 import QtGui, QtCore, QtWidgets
    from PyQt6.QtCore import *
    from PyQt6.QtWidgets import *
    from PyQt6.QtGui import *
    from PyQt6.QtWebEngineWidgets import *
    from PyQt6.QtWebEngineCore import *

    # QSettings_NativeFormat = QSettings.Format.NativeFormat



    class TextFlag:
        TextSingleLine = Qt.TextFlag.TextSingleLine
        TextDontClip = Qt.TextFlag.TextDontClip
        TextExpandTabs = Qt.TextFlag.TextExpandTabs
        TextShowMnemonic = Qt.TextFlag.TextShowMnemonic
        TextWordWrap = Qt.TextFlag.TextWordWrap
        TextWrapAnywhere = Qt.TextFlag.TextWrapAnywhere
        TextHideMnemonic = Qt.TextFlag.TextHideMnemonic
        TextDontPrint = Qt.TextFlag.TextDontPrint
        TextIncludeTrailingSpaces = Qt.TextFlag.TextIncludeTrailingSpaces
        TextJustificationForced = Qt.TextFlag.TextJustificationForced


    class QAbstractItemViewSelectionBehavior:
        SelectItems = QAbstractItemView.SelectionBehavior.SelectItems
        SelectRows = QAbstractItemView.SelectionBehavior.SelectRows
        SelectColumns = QAbstractItemView.SelectionBehavior.SelectColumns


    class DragDropMode:
        NoDragDrop = QAbstractItemView.DragDropMode.NoDragDrop
        InternalMove = QAbstractItemView.DragDropMode.InternalMove
        DragDrop = QAbstractItemView.DragDropMode.DragDrop


    class PenStyle:
        SolidLine = Qt.PenStyle.SolidLine
        DashLine = Qt.PenStyle.DashLine
        DotLine = Qt.PenStyle.DotLine
        DashDotLine = Qt.PenStyle.DashDotLine
        DashDotDotLine = Qt.PenStyle.DashDotDotLine
        CustomDashLine = Qt.PenStyle.CustomDashLine


    class QAbstractItemViewSelectMode:
        ExtendedSelection = QAbstractItemView.SelectionMode.ExtendedSelection
        SingleSelection = QAbstractItemView.SelectionMode.SingleSelection
        NoSelection = QAbstractItemView.SelectionMode.NoSelection


    class dropIndicatorPosition:
        OnItem = QAbstractItemView.DropIndicatorPosition.OnItem
        OnViewport = QAbstractItemView.DropIndicatorPosition.OnViewport
        BelowItem = QAbstractItemView.DropIndicatorPosition.BelowItem
        AboveItem = QAbstractItemView.DropIndicatorPosition.AboveItem


    class ItemDataRole:
        DisplayRole = Qt.ItemDataRole.DisplayRole
        UserRole = Qt.ItemDataRole.UserRole
        EditRole = Qt.ItemDataRole.EditRole


    class ViewportUpdateMode:
        FullViewportUpdate = QGraphicsView.ViewportUpdateMode.FullViewportUpdate


    class DragMode:
        ScrollHandDrag = QGraphicsView.DragMode.ScrollHandDrag
        RubberBandDrag = QGraphicsView.DragMode.RubberBandDrag
        NoDrag = QGraphicsView.DragMode.NoDrag


    class QGraphicsRectItemFlags:
        ItemIsMovable = QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable
        ItemIsSelectable = QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable
        ItemSendsGeometryChanges = QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges


    class AlignmentFlag:
        AlignCenter = Qt.AlignmentFlag.AlignCenter
        AlignVCenter = Qt.AlignmentFlag.AlignVCenter
        AlignHCenter = Qt.AlignmentFlag.AlignHCenter
        AlignRight = Qt.AlignmentFlag.AlignRight
        AlignLeft = Qt.AlignmentFlag.AlignLeft
        AlignTop = Qt.AlignmentFlag.AlignTop
        AlignBottom = Qt.AlignmentFlag.AlignBottom
        AlignAbsolute = Qt.AlignmentFlag.AlignAbsolute
        AlignBaseline = Qt.AlignmentFlag.AlignBaseline
else:

    # from PyQt5 import Qt
    from PyQt5 import QtGui, QtCore
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
    from PyQt5.QtWebEngineWidgets import *
    # if not ISLOCALDEBUG:
    Qt.WidgetAttribute.WA_DeleteOnClose = Qt.WA_DeleteOnClose
    QSettings_NativeFormat = QSettings.NativeFormat
    class QPainter_RenderHint:
        Antialiasing = QPainter.Antialiasing
        TextAntialiasing = QPainter.TextAntialiasing
        SmoothPixmapTransform = QPainter.SmoothPixmapTransform
        LosslessImageRendering = QPainter.LosslessImageRendering
    QPainter.RenderHint.Antialiasing = QPainter.Antialiasing
    QPainter.RenderHint.TextAntialiasing = QPainter.TextAntialiasing
    QPainter.RenderHint.SmoothPixmapTransform = QPainter.SmoothPixmapTransform
    # QPainter.RenderHint.VerticalSubpixelPositioning=QPainter.VerticalSubpixelPositioning
    QPainter.RenderHint.LosslessImageRendering = QPainter.LosslessImageRendering
    Qt.MouseButton.NoButton = Qt.NoButton
    Qt.MouseButton.AllButtons = Qt.AllButtons
    Qt.MouseButton.LeftButton = Qt.LeftButton
    Qt.MouseButton.RightButton = Qt.RightButton
    Qt.MouseButton.MiddleButton = Qt.MiddleButton
    Qt.KeyboardModifier.NoModifier = Qt.NoModifier
    Qt.KeyboardModifier.ShiftModifier = Qt.ShiftModifier
    Qt.KeyboardModifier.ControlModifier = Qt.ControlModifier
    Qt.KeyboardModifier.AltModifier = Qt.AltModifier
    Qt.KeyboardModifier.MetaModifier = Qt.MetaModifier
    Qt.KeyboardModifier.KeypadModifier = Qt.KeypadModifier
    Qt.KeyboardModifier.GroupSwitchModifier = Qt.GroupSwitchModifier
    Qt.Key.Key_Return = Qt.Key_Return
    Qt.ContextMenuPolicy.NoContextMenu = Qt.NoContextMenu
    Qt.ContextMenuPolicy.PreventContextMenu = Qt.PreventContextMenu
    Qt.ContextMenuPolicy.DefaultContextMenu = Qt.DefaultContextMenu
    Qt.ContextMenuPolicy.ActionsContextMenu = Qt.ActionsContextMenu
    Qt.ContextMenuPolicy.CustomContextMenu = Qt.CustomContextMenu
    Qt.ItemFlag.NoItemFlags = Qt.NoItemFlags
    Qt.ItemFlag.ItemIsSelectable = Qt.ItemIsSelectable
    Qt.ItemFlag.ItemIsEditable = Qt.ItemIsEditable
    Qt.ItemFlag.ItemIsDragEnabled = Qt.ItemIsDragEnabled
    Qt.ItemFlag.ItemIsDropEnabled = Qt.ItemIsDropEnabled
    Qt.ItemFlag.ItemIsUserCheckable = Qt.ItemIsUserCheckable
    Qt.ItemFlag.ItemIsEnabled = Qt.ItemIsEnabled
    Qt.ItemFlag.ItemIsAutoTristate = Qt.ItemIsAutoTristate
    Qt.ItemFlag.ItemNeverHasChildren = Qt.ItemNeverHasChildren
    Qt.ItemFlag.ItemIsUserTristate = Qt.ItemIsUserTristate
    Qt.WindowType.Widget = Qt.Widget
    Qt.WindowType.Window = Qt.Window
    Qt.WindowType.Dialog = Qt.Dialog
    Qt.WindowType.Sheet = Qt.Sheet
    Qt.WindowType.Drawer = Qt.Drawer
    Qt.WindowType.Popup = Qt.Popup
    Qt.WindowType.Tool = Qt.Tool
    Qt.WindowType.ToolTip = Qt.ToolTip
    Qt.WindowType.SplashScreen = Qt.SplashScreen
    Qt.WindowType.SubWindow = Qt.SubWindow
    Qt.WindowType.ForeignWindow = Qt.ForeignWindow
    Qt.WindowType.CoverWindow = Qt.CoverWindow
    Qt.TextFlag.TextWordWrap = Qt.TextWordWrap
    QLineF.IntersectionType = QLineF.IntersectType
    QLineF.IntersectionType.NoIntersection = QLineF.NoIntersection
    QLineF.IntersectionType.BoundedIntersection = QLineF.BoundedIntersection
    QLineF.IntersectionType.UnboundedIntersection = QLineF.UnboundedIntersection
    QHeaderView.ResizeMode.Interactive = QHeaderView.Interactive
    QHeaderView.ResizeMode.Fixed = QHeaderView.Fixed
    QHeaderView.ResizeMode.Stretch = QHeaderView.Stretch
    QHeaderView.ResizeMode.ResizeToContents = QHeaderView.ResizeToContents
    QGraphicsLineItem.GraphicsItemFlag.ItemIsSelectable = QGraphicsLineItem.ItemIsSelectable
    QAbstractItemView.ScrollMode.ScrollPerPixel = QAbstractItemView.ScrollPerPixel

    class QStyle_StateFlag:
        State_Selected = QStyle.State_Selected

    class PenStyle:
        SolidLine = Qt.SolidLine
        DashLine = Qt.DashLine
        DotLine = Qt.DotLine
        DashDotLine = Qt.DashDotLine
        DashDotDotLine = Qt.DashDotDotLine
        CustomDashLine = Qt.CustomDashLine


    class DragDropMode:
        NoDragDrop = QAbstractItemView.NoDragDrop
        InternalMove = QAbstractItemView.InternalMove
        DragDrop = QAbstractItemView.DragDrop


    class QAbstractItemViewSelectMode:
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
        BoundingRectViewportUpdate = QGraphicsView.BoundingRectViewportUpdate
        SmartViewportUpdate = QGraphicsView.SmartViewportUpdate
        MinimalViewportUpdate = QGraphicsView.MinimalViewportUpdate

    class QGraphicsRectItemFlags:
        ItemIsMovable = QGraphicsRectItem.ItemIsMovable
        ItemIsSelectable = QGraphicsRectItem.ItemIsSelectable
        ItemSendsGeometryChanges = QGraphicsRectItem.ItemSendsGeometryChanges


    class ItemDataRole:
        DisplayRole = Qt.DisplayRole
        UserRole = Qt.UserRole
        EditRole = Qt.EditRole


    class AlignmentFlag:
        AlignCenter = Qt.AlignCenter
        AlignVCenter = Qt.AlignVCenter
        AlignHCenter = Qt.AlignHCenter
        AlignRight = Qt.AlignRight
        AlignLeft = Qt.AlignLeft
        AlignTop = Qt.AlignTop
        AlignBottom = Qt.AlignBottom
        AlignAbsolute = Qt.AlignAbsolute
        AlignBaseline = Qt.AlignBaseline


    class QAbstractItemViewSelectionBehavior:
        SelectItems = QAbstractItemView.SelectItems
        SelectRows = QAbstractItemView.SelectRows
        SelectColumns = QAbstractItemView.SelectColumns


    class TextFlag:
        TextSingleLine = Qt.TextSingleLine
        TextDontClip = Qt.TextDontClip
        TextExpandTabs = Qt.TextExpandTabs
        TextShowMnemonic = Qt.TextShowMnemonic
        TextWordWrap = Qt.TextWordWrap
        TextWrapAnywhere = Qt.TextWrapAnywhere
        TextHideMnemonic = Qt.TextHideMnemonic
        TextDontPrint = Qt.TextDontPrint
        TextIncludeTrailingSpaces = Qt.TextIncludeTrailingSpaces
        TextJustificationForced = Qt.TextJustificationForced

class Qt_ItemDataRole:
    UserRole=Qt.ItemDataRole.UserRole if Utils.isQt6() else Qt.UserRole

class QAbstractItemView_SelectionBehavior:
    SelectRows = QAbstractItemView.SelectionBehavior.SelectRows if Utils.isQt6() else QAbstractItemView.SelectRows

class QAbstractItemView_EditTrigger:
    NoEditTriggers = QAbstractItemView.EditTrigger.NoEditTriggers if Utils.isQt6() else QAbstractItemView.NoEditTriggers

class QItemSelectionModel_SelectionFlag:
    Select = QItemSelectionModel.SelectionFlag.Select if Utils.isQt6() else QItemSelectionModel.Select

class QStyle_StateFlag:
    State_Selected = QStyle.StateFlag.State_Selected if Utils.isQt6() else QStyle.State_Selected

class QMessageBox_StandardButton:
    Yes = QMessageBox.StandardButton.Yes if Utils.isQt6() else QMessageBox.Yes
    No = QMessageBox.StandardButton.No if Utils.isQt6() else QMessageBox.No


def qconnect(
    signal: Union[Callable, pyqtSignal, pyqtBoundSignal], func: Callable
) -> None:
    """Helper to work around type checking not working with signal.connect(func)."""
    signal.connect(func)  # type: ignore
#
# if ISDEBUG:
#     tooltip = print