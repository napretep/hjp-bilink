import json

from aqt.utils import showInfo
from .inputObj import Input
from .handle_DB import LinkInfoDBmanager
from .utils import BaseInfo, Pair, console, Config
from .HTML_converterObj import HTML_converter
from .linkData_reader import LinkData_reader


class ButtonMaker(Config):


def HTMLbutton_make(htmltext, card):
    result = htmltext
    data = LinkData_reader(str(card.id)).read()
    if len(data["link_list"]) > 0:

    # showInfo(linkdata.__str__())
    # htmltext1 = HTML_converter().feed(htmltext).HTMLButton_selfdata_make(linkdata).HTMLdata_save().HTML_get().HTML_text
    return htmltext
