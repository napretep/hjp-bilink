"""
专门用来处理backlink是删除呢,还是添加呢
"""
from ..imports import common_tools, say
Anki = common_tools.compatible_import.Anki
if Anki.isQt6:
    from PyQt6.QtCore import QTimer
else:
    from PyQt5.QtCore import QTimer
from aqt.utils import tooltip
from .. import linkdata_admin

signals = common_tools.G.signals


def backlink_append_remove(self_card_id, nowbacklink, originbacklink):
    add = nowbacklink - originbacklink
    rm = originbacklink - nowbacklink
    if len(add) > 0:
        appended = backlink_append(self_card_id, add)
        tooltip(f"""{say("已建立反链")}：{add.__str__()}""")
    if len(rm) > 0:
        removed = backlink_remove(self_card_id, rm)
        tooltip(f"""{say("已删除反链")}：{rm.__str__()}""")
    QTimer.singleShot(200, lambda: common_tools.funcs.CardOperation.refresh())


def backlink_append(self_card_id, add):
    appended = False
    if type(self_card_id) != str:
        self_card_id = str(self_card_id)
    common_tools.funcs.Utils.print(f"need to add = {add.__str__()}")
    for card_id in add:
        data = linkdata_admin.read_card_link_info(card_id)
        common_tools.funcs.Utils.print(f"backlink of card of need to add ={data.backlink.__str__()}")
        if self_card_id not in data.backlink:
            data.backlink.append(self_card_id)  # 此处并不提供 卡片描述
            linkdata_admin.write_card_link_info(card_id, data.to_DB_record["data"])
            appended = True
    return appended


def backlink_remove(self_card_id, rm):
    removed = False
    if type(self_card_id) != str:
        self_card_id = str(self_card_id)
    for card_id in rm:
        data = linkdata_admin.read_card_link_info(card_id)
        if self_card_id in data.backlink:
            data.backlink.remove(self_card_id)
            linkdata_admin.write_card_link_info(card_id, data.to_DB_record["data"])
            removed = True
    return removed
