import re
from aqt import mw

class BackLinkReader():

    def __init__(self,card_id="",html_str=""):
        if card_id !="":
            note = mw.col.getCard(int(card_id)).note()
            if note is None:
                raise ValueError("note is None")
            html_str = " ".join(note.fields)
        self.html_str = html_str

    def backlink_get(self):
        """返回buttonli 其中每个元素装的是状态, 位置, 描述, 卡片id"""
        buttonli = []
        baseindex = 0
        html_str = self.html_str
        result = self.markup_find(html_str, baseindex)
        while result is not None and baseindex < len(self.html_str):
            buttonli.append(result)
            baseindex = result["span"][1]
            result = self.markup_find(html_str, baseindex)
        return buttonli

    def markup_find(self,html_str_origin,baseindex):
        """html_str要从上一个link结束后开始，baseindex是原始文本的绝对位置"""
        html_str = html_str_origin[baseindex:]
        index_of_head = re.search(r"\[\[link:",html_str)
        if index_of_head is None: return None #如果找不到，那就直接退出了，后面都不会有了
        beginindex = index_of_head.span()[0]
        headendindex = index_of_head.span()[1]
        html_str = html_str[headendindex:]
        r = re.search(r"\d+",html_str,)
        if r is None: return None
        card_id_span, card_id = r.span(), r.group()
        if card_id_span[0] != 0 : return None
        if card_id_span[1]==len(html_str): return None
        if html_str[card_id_span[1]] != "_": return None
        html_str = html_str[card_id_span[1]:]
        r2 = re.search(r"_]]", html_str)
        if r2 is None: return None
        tail_begin = r2.span()[0]
        tail_end = r2.span()[1]
        desc = html_str[1:tail_begin]
        endindex = headendindex+card_id_span[1]+tail_end
        return {
            "status": True,
            "span":(baseindex+beginindex,baseindex+endindex),
            "desc":desc,
            "card_id":card_id
        }