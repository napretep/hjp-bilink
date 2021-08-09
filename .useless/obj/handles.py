import aqt, time
from aqt import mw
from anki.cards import Card
from aqt.reviewer import Reviewer
from . import funcs, clipper_imports, all_objs, events, signals

print, _ = clipper_imports.funcs.logger(__name__)


def on_notes_will_be_deleted_handle(self, nids):
    DB = clipper_imports.objs.SrcAdmin.DB
    for nid in nids:
        ids = mw.col.getNote(nid).card_ids()
        for cid in ids:
            DB.go(DB.table_clipbox).del_card_id(DB.where_maker(LIKE=True, colname="card_id", vals=f"%{cid}%"), str(cid),
                                                callback=None)
    DB.end()


def on_reviewer_did_answer_card_handle(reviewer: Reviewer, card: Card, ease: int):
    funcs.PDFprev_close(card_id=card.id, all=True)


# def on_PDFprev_save_clipbox_handle(data,progress_signal,worker_quit_signal):
#
#     for card_desc,clipboxli in event.data:
#         if card_desc
#
#     event.worker_quit_signal.emit()

def on_currentEdit_will_show_handle(*args, **kwargs):
    card_id = mw.reviewer.card.id
    funcs.PDFprev_close(card_id=card_id, all=True)


def on_state_did_change_handle(new_state: str, old_state: str):
    # print(f"""new_state={new_state},old_state={old_state}""")
    if new_state == "review" and mw.reviewer.card is not None:
        all_objs.mw_current_card_id = mw.reviewer.card.id

    if new_state != old_state and old_state == "review" and all_objs.mw_current_card_id is not None:
        funcs.PDFprev_close(card_id=all_objs.mw_current_card_id, all=True)
        all_objs.mw_current_card_id = None
