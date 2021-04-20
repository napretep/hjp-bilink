import json

from aqt.utils import showInfo

from .handle_DB import LinkInfoDBmanager
from .languageObj import rosetta as say
from .HTML_converterObj import HTML_converter
from .cardInfo_obj import CardLinkInfo
from .inputObj import Input
from .utils import BaseInfo, Pair, console


class LinkData_reader:
    """
    用来统一读取链接数据的接口.
    """

    def __init__(self, config=None):
        self.config = config if config is not None else BaseInfo()
        self.storageLocation = self.config.userinfo["linkInfoStorageLocation"]

    def linkdata_read(self, card_id: str):
        """用来读取链接信息为下一步的按钮渲染做准备, 并且作兼容处理, """
        if self.storageLocation == 0:
            return self.linkData_DB_read(card_id)
        elif self.storageLocation == 1:
            return self.linkData_field_read(card_id)
        else:
            return None

    def linkData_DB_read(self, card_id: str):
        DB = LinkInfoDBmanager()
        link_card_info = DB.cardinfo_get(Pair(card_id=card_id, desc=""))
        card_dict = link_card_info.card_dict
        link_card_info.card_linked_pairLi = list(map(lambda x: Pair(**card_dict[x]), link_card_info.link_list))
        for pair in link_card_info.card_linked_pairLi:
            link_card_info.cardinfo_dict[pair.card_id] = pair
        for item in link_card_info.link_tree:
            newitem = {}
            if "card_id" in item:
                newitem["type"] = "cardinfo"
                newitem["card_id"] = item["card_id"]
            elif "groupname" in item:
                newitem["type"] = "groupinfo"
                newitem["groupname"] = item["groupname"]
            link_card_info.card_selfdata_dict["menuli"].append(newitem)

        return link_card_info

    def linkData_field_read(self, card_id):
        dict_cardinfo = CardLinkInfo(card_id)
        p = Input()
        field = p.note_id_load(Pair(card_id=card_id, desc="")).fields[p.insertPosi]
        try:
            fielddata = HTML_converter().feed(field).HTMLdata_load()
            dict_cardinfo.card_linked_pairLi = fielddata.card_linked_pairLi
            dict_cardinfo.card_selfdata_dict = fielddata.card_selfdata_dict
            dict_cardinfo.cardinfo_dict = fielddata.cardinfo_dict
        except json.JSONDecodeError as e:
            console(f"""{say("链接列表渲染失败")},{say("错误信息")}:{repr(e)}""", func=showInfo).talk.end()
        return dict_cardinfo
