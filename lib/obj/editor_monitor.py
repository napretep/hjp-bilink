import anki.notes
from PyQt5.QtCore import QTimer
from aqt.editor import Editor
from aqt.utils import tooltip, showInfo
from . import signals
from . import clipper_imports
from .utils import browser_refresh, webview_refresh
from .backlink_reader import BackLinkReader
from .handle_backlink import backlink_append, backlink_append_remove

print, _ = clipper_imports.funcs.logger(__name__)


def handle_editor_did_load_note(editor: Editor):  # editor_did_load_note
    """从field中提取html字符串，然后再从其中提取出反向链接"""

    if editor.parentWindow.__class__.__name__ == "AddCards":
        return

    if editor.parentWindow.__class__.__name__ == "Browser":
        pass
    if editor.parentWindow.__class__.__name__ in ["EditCurrent", "EditNoteWindowFromThisLinkAddon"]:
        pass

    note = editor.note

    self_card_id = editor.note.card_ids()[0].__str__() if len(editor.note.card_ids()) > 0 else None
    if self_card_id is not None:
        backlink_monitor_setup(self_card_id, note)


def backlink_monitor_setup(self_card_id, note):
    if note is None:
        raise ValueError("note is None")
    htmltxt = "\n".join(note.fields)
    backlink = set([x["card_id"] for x in BackLinkReader(html_str=htmltxt).backlink_get()])
    needrefresh = backlink_append(self_card_id, backlink)
    note.hjp_bilink_backlink = backlink


def handle_editor_will_munge_html(text, editor: "Editor"):
    if editor.parentWindow.__class__.__name__ == "AddCards":
        return text
    note = editor.note
    self_card_id = editor.note.card_ids()[0]
    nowbacklink = set([x["card_id"] for x in BackLinkReader(html_str=text).backlink_get()])
    # self_card_id = note.card_ids()[0]
    if not hasattr(note, "hjp_bilink_backlink"):
        note.hjp_bilink_backlink = nowbacklink
        return text
    else:
        originbacklink = note.hjp_bilink_backlink
        if nowbacklink != originbacklink:
            backlink_append_remove(self_card_id, nowbacklink, originbacklink)
            note.hjp_bilink_backlink = nowbacklink
            # signals.all.on_data_refresh_webview.emit()
            # QTimer().singleShot(100,lambda : webview_refresh(True))
            # QTimer().singleShot(100,signals.all.on_data_refresh_webview.emit)
            QTimer().singleShot(100, signals.ALL.on_data_refresh_all.emit)

    return text
