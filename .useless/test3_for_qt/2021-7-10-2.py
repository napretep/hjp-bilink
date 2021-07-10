from bs4 import BeautifulSoup, element
import re


def HTML_has_clipboxUuid(html, card_id=None):
    root = BeautifulSoup(html, "html.parser")
    imgli = root.find("img", attrs={"class": "hjp_clipper_clipbo"})
    clipbox_uuid_li = [re.sub("hjp_clipper_(\w+)_.png", lambda x: x.group(1), img.attrs["src"]) for img in imgli]
    print(re.sub("hjp_clipper_(\w+)_.png", lambda x: x.group(1), imgli.attrs["src"]))


if __name__ == "__main__":
    html = """
    [clip:1b96451a]
[clip:]
<img class="hjp_clipper_clipbox" src="hjp_clipper_034bd39d_.png">
<img class="hjp_clipper_clipbox" src="hjp_clipper_ac0bfe01_.png">
    """
    HTML_has_clipboxUuid(html)
