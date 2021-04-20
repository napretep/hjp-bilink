import json

from aqt.utils import showInfo
from .inputObj import Input
from .handle_DB import LinkInfoDBmanager
from .utils import BaseInfo, Pair, console
from .HTML_converterObj import HTML_converter
from .linkData_reader import LinkData_reader


def HTMLbutton_maker(htmltext, card):
    """
    Parameters
    ----------
    htmltext : str
    card : str

    Returns
    -------

    """
    linkdata = LinkData_reader().linkdata_read(str(card.id))
    htmltext1 = HTML_converter().feed(htmltext).HTMLButton_selfdata_make(linkdata).HTMLdata_save().HTML_get().HTML_text
    return htmltext1
