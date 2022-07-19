# import json
# import os
# import re
# from functools import reduce
#
# from aqt import mw
# from aqt.utils import showInfo
# from bs4 import BeautifulSoup
#
# from ..G import src
#
#
# def version_cmpkey(path):
#     from . import objs
#     filename = os.path.basename(path)
#     v_tuple = re.search(r"(\d+)\.(\d+)\.(\d+)", filename).groups()
#     return objs.AddonVersion(v_tuple)
#
#
# # def config_check_update():
# #     """
# #     更新配置文件
# #
# #     Returns:
# #
# #     """
# #     need_update = False
# #     config = src.config
# #     user_config_dir = src.path.userconfig
# #     template = config.template.get_config
# #     if os.path.isfile(user_config_dir) and os.path.exists(user_config_dir):
# #         user = config.user.get_config
# #     else:
# #         user = {}
# #
# #     if "VERSION" not in user or config.base.VERSION != user["VERSION"]:
# #         need_update = True
# #         user["VERSION"] = config.base.VERSION
# #         template["VERSION"] = config.base.VERSION
# #         for key, value in template.items():
# #             if key not in user:
# #                 user[key] = value
# #         usercopy = user.copy()
# #         for key, value in usercopy.items():
# #             if key not in template:
# #                 user.__deleteitem__(key)
# #     if need_update:
# #         json.dump(user, open(user_config_dir, "w", encoding="utf-8"), indent=4,
# #                   ensure_ascii=False)
# #     return need_update
#
#
# def note_get(card_id):
#     from . import objs
#     if isinstance(card_id, objs.LinkDataPair):
#         cid = card_id.int_card_id
#     elif isinstance(card_id, str):
#         cid = int(card_id)
#     elif type(card_id) == int:
#         cid = card_id
#     else:
#         raise TypeError("参数类型不支持:" + card_id.__str__())
#     if cardExistsInDB(cid):
#         note = mw.col.getCard(cid).note()
#     else:
#         showInfo(f"{cid} 卡片不存在/card don't exist")
#         return
#     return note
#
#
# # def desc_extract(card_id=None, fromField=False):
# #     """读取卡片的描述,需要卡片id"""
# #     from . import objs
# #     from . import linkdata_admin
# #
# #     if isinstance(card_id, objs.LinkDataPair):  # 有可能把pair传进来的
# #         cid = card_id.int_card_id
# #     elif isinstance(card_id, str):
# #         cid = int(card_id)
# #     elif type(card_id) == int:
# #         cid = card_id
# #     else:
# #         raise TypeError("参数类型不支持:" + card_id.__str__())
# #     cfg = src.config.user
# #     note = note_get(cid)
# #
# #     if fromField:  # 分成这两段, 是因为一个循环引用.
# #         content = reduce(lambda x, y: x + y, note.fields)
# #         desc = HTML_txtContent_read(content)
# #         desc = re.sub(r"\n+", "", desc)
# #         desc = desc[0:cfg.descMaxLength if len(desc) > cfg.descMaxLength != 0 else len(desc)]
# #     else:
# #         desc = linkdata_admin.read_card_link_info(str(cid)).self_data.desc
# #         if desc == "":
# #             content = reduce(lambda x, y: x + y, note.fields)
# #             desc = HTML_txtContent_read(content)
# #             desc = re.sub(r"\n+", "", desc)
# #             desc = desc[0:cfg.descMaxLength if len(desc) > cfg.descMaxLength != 0 else len(desc)]
# #
# #     return desc
#
#
# def cardExistsInDB(card_id):
#     from . import objs
#     if isinstance(card_id, objs.LinkDataPair):
#         cid = card_id.int_card_id
#     elif isinstance(card_id, str):
#         cid = int(card_id)
#     elif type(card_id) == int:
#         cid = card_id
#     else:
#         raise TypeError("参数类型不支持:" + card_id.__str__())
#     txt = f"cid:{cid}"
#     card_ids = mw.col.find_cards(txt)
#     if len(card_ids) == 1:
#         return True
#     else:
#         return False
#
#
# # def HTML_txtContent_read(html):
# #     """HTML文本内容的读取,如果没有就尝试找img的src文本"""
# #
# #     from .backlink_reader import BackLinkReader
# #     cfg = src.config.user
# #     root = BeautifulSoup(html, "html.parser")
# #     text = root.getText()
# #     if cfg.delete_intext_link_when_extract_desc == 1:
# #         newtext = text
# #         replace_str = ""
# #         intextlinks = BackLinkReader(html_str=text).backlink_get()
# #         for link in intextlinks:
# #             span = link["span"]
# #             replace_str += re.sub("(\])|(\[)", lambda x: "\]" if x.group(0) == "]" else "\[",
# #                                   text[span[0]:span[1]]) + "|"
# #         replace_str = replace_str[0:-1]
# #         text = re.sub(replace_str, "", newtext)
# #     if not re.search("\S", text):
# #         a = root.find("img")
# #         if a is not None:
# #             text = a.attrs["src"]
# #
# #     return text
