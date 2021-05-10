from json.decoder import JSONDecodeError
from aqt.utils import showInfo

from .languageObj import rosetta as say
from .HTML_converterObj import HTML_converter
from .inputObj import Input
from .utils import Pair, console


def makelinklist_over_context(htmltext, card):
    """制作外部的链接列表"""
    p = Input()
    field = p.note_id_load(Pair(card_id=str(card.id))).fields[p.insertPosi]
    try:
        fielddata = HTML_converter().feed(field).HTMLdata_load()
    except JSONDecodeError as e:
        console(f"""{say("链接列表渲染失败")},{say("错误信息")}:{repr(e)}""", func=showInfo).talk.end()
    except:
        console(f"""{say("链家列表渲染失败")}:{say("未知错误")}""", func=showInfo).talk.end()
    return htmltext

