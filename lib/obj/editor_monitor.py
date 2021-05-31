import anki.notes
from aqt.editor import Editor
from aqt.utils import tooltip, showInfo

from .utils import browser_refresh,webview_refresh
from .backlink_reader import BackLinkReader
from .handle_backlink import backlink_append, backlink_append_remove

def handle_editor_did_load_note(editor:Editor):#editor_did_load_note
    """从field中提取html字符串，然后再从其中提取出反向链接"""
    note = editor.note
    self_card_id = editor.note.card_ids()[0].__str__() if len(editor.note.card_ids())>0 else None
    if self_card_id is not None:
        return
    backlink_monitor_setup(self_card_id,note)



def backlink_monitor_setup(self_card_id,note):
    htmltxt = "\n".join(note.fields)
    backlink = set([x["card_id"] for x in BackLinkReader(html_str=htmltxt).backlink_get()])
    needrefresh = backlink_append(self_card_id, backlink)
    note.hjp_bilink_backlink = backlink
    if needrefresh:
        webview_refresh(True)



def backlink_realtime_check(txt,editor:Editor):
    if editor.note is None:
        tooltip("editor.note is None")
        return txt
    self_card_id = editor.note.card_ids()[0]
    HTML_str = txt + "\n".join(editor.note.fields)
    nowbacklink = set([x["card_id"] for x in BackLinkReader(html_str=HTML_str).backlink_get()])
    # tooltip("now:"+nowbacklink.__str__())
    originbacklink = editor.note.hjp_bilink_backlink
    if nowbacklink!= originbacklink:
        editor.note.flush()
        backlink_append_remove(self_card_id,nowbacklink,originbacklink)
        editor.note.hjp_bilink_backlink = nowbacklink
        webview_refresh(True)
    return txt

def handle_editor_did_unfocus_field(changed: bool, note: anki.notes.Note,current_field_idx: int):
    if note is None:
        return changed
    changed=field_unfocus_backlink_check(changed,note)
    return changed

def field_unfocus_backlink_check(changed: bool, note: anki.notes.Note):
    if len(note.card_ids())==0:
        return changed
    if not hasattr(note,"hjp_bilink_backlink"):
        return changed
    HTML_str = "\n".join(note.fields)
    nowbacklink = set([x["card_id"] for x in BackLinkReader(html_str=HTML_str).backlink_get()])
    self_card_id = note.card_ids()[0]
    originbacklink = note.hjp_bilink_backlink
    if nowbacklink!= originbacklink and originbacklink is not None:
        backlink_append_remove(self_card_id,nowbacklink,originbacklink)
        note.hjp_bilink_backlink = nowbacklink
        webview_refresh(True)
    return changed


def handle_editor_will_munge_html(text, editor):
    pass