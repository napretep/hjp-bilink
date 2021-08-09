import re

html_doc = """
<html><head><title>The Dormouse's story</title></head>

<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>
<img class="hjp_clipper_clipbox" src="hjp_clipper_e36c391d_.png">
&nbsp;<img src="hjp_clipper_71d4f06a_.png">&nbsp;
<p class="story">...</p>
"""

from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, "html.parser")

if __name__ == "__main__":
    result = soup.find_all(name="img", src=re.compile("hjp_clipper_\w{8}_.png"))
    print(result)
