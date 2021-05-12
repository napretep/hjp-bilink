import re

from bs4 import BeautifulSoup


class FieldHTMLData:
    def __init__(self, html: str):
        super().__init__()
        self.html_str = html
        self.output_str = ""
        self.html_page = BeautifulSoup(self.html_str, "html.parser")

class InTextButtonMaker(FieldHTMLData):

    def build(self):
        buttonli = []
        baseindex = 0
        html_str = self.html_str
        result = self.markup_find(html_str,baseindex)
        while result is not None and baseindex<len(self.html_str):
            buttonli.append(result)
            baseindex = result["span"][1]
            result = self.markup_find(html_str,baseindex)
        if len(buttonli)>0:
            finalstring = self.html_str[0:buttonli[0]["span"][0]]
            for i in range(len(buttonli)-1):
                prevEnd,nextBegin  = buttonli[i]["span"][1],buttonli[i+1]["span"][0]
                finalstring += self.button_make(buttonli[i])+self.html_str[prevEnd:nextBegin]
            finalstring += self.button_make(buttonli[-1])+self.html_str[buttonli[-1]["span"][1]:]
        else:
            finalstring = self.html_str
        return finalstring

    def button_make(self,data):
        card_id = data["card_id"]
        desc = data["desc"]
        h = self.html_page
        b = h.new_tag("button", attrs={"card_id": card_id,"class":"hjp-bilink intext button",
                                       "onclick": f"""javascript:pycmd('hjp-bilink-cid:{card_id}');"""})
        b.string = desc
        return b.__str__()

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
        if card_id_span[1]==len(html_str) or html_str[card_id_span[1]] != "_": return None
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

teststring = """A
[[link:1620468288991_AfromJSON_]]




[[link:1620460468289832__]]"""
if __name__ == "__main__":
    I = InTextButtonMaker(teststring)
    s = I.build()
    print(s)