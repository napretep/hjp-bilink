import aqt
from aqt import mw
from anki.cards import Card
from aqt.reviewer import Reviewer
from . import funcs, clipper_imports, all_objs

print, _ = clipper_imports.funcs.logger(__name__)


def on_reviewer_did_answer_card_handle(reviewer: Reviewer, card: Card, ease: int):
    funcs.PDFprev_close(card_id=card.id, all=True)


def on_currentEdit_will_show_handle(**kwargs):
    card_id = mw.reviewer.card.id
    funcs.PDFprev_close(card_id=card_id, all=True)


def on_state_did_change_handle(new_state: str, old_state: str):
    # print(f"""new_state={new_state},old_state={old_state}""")
    if new_state == "review":
        all_objs.mw_current_card_id = mw.reviewer.card.id

    if new_state != old_state and old_state == "review":
        funcs.PDFprev_close(card_id=all_objs.mw_current_card_id, all=True)
        all_objs.mw_current_card_id = None
