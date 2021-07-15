from aqt.utils import tooltip

from .utils import wrapper_browser_refresh, wrapper_webview_refresh
from .languageObj import rosetta as say
from .linkData_reader import LinkDataReader
from .linkData_writer import LinkDataWriter


def backlink_append_remove(self_card_id, nowbacklink, originbacklink):
    add = nowbacklink - originbacklink
    rm = originbacklink - nowbacklink
    if len(add) > 0:
        appended = backlink_append(self_card_id, add)
        tooltip(f"""{say("已建立反链")}：{add.__str__()}""")
    if len(rm) > 0:
        removed = backlink_remove(self_card_id, rm)
        tooltip(f"""{say("已删除反链")}：{rm.__str__()}""")


def backlink_append(self_card_id, add):
    appended = False
    if type(self_card_id) != str:
        self_card_id = str(self_card_id)
    for card_id in add:
        data = LinkDataReader(card_id).read()
        if "backlink" not in data:
            data["backlink"] = []
        if self_card_id not in data["backlink"]:
            data["backlink"].append(self_card_id)  # 此处并不提供 卡片描述
            LinkDataWriter(card_id, data).write()
            appended = True
    return appended


def backlink_remove(self_card_id, rm):
    removed = False
    if type(self_card_id) != str:
        self_card_id = str(self_card_id)
    for card_id in rm:
        data = LinkDataReader(card_id).read()
        if "backlink" in data and self_card_id in data["backlink"]:
            data["backlink"].remove(self_card_id)
            LinkDataWriter(card_id, data).write()
            removed = True
    return removed
