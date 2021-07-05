import json
import os
import re
import time
from datetime import datetime
from functools import reduce
from math import ceil

from aqt.utils import showInfo

from .tools import events, fitz, objs
from anki import stdmodels, notes
from aqt import mw, browser

pngfileprefix = "hjp_clipper_"

def on_anki_create_card_handle1(model_id, deck_id):
    if model_id is None:
        if not "Basic" in mw.col.models.allNames():
            mw.col.models.add(stdmodels.addBasicModel(mw.col))
        model = mw.col.models.byName("Basic")
    else:
        if mw.col.models.have(model_id):
            model = mw.col.models.get(model_id)
        else:
            raise TypeError(f"modelId don't exist:{model_id}")
    note = notes.Note(mw.col, model=model)
    if deck_id is None:
        deck_id = mw.col.decks.current()["id"]
    mw.col.add_note(note, deck_id=deck_id)
    note.flush()
    return str(note.card_ids()[0])


def bookmark_to_tag(bookmark: "list[list[int,str,int]]"):
    tag_dict = {}
    level, content, pagenum = bookmark[0][0], bookmark[0][1], bookmark[0][2]
    tag_dict[pagenum] = re.sub(r"\s|\r|\n", "-", content)
    level_stack = []
    level_stack.append([level, content, pagenum])
    for item in bookmark[1:]:
        level, content, pagenum = item[0], re.sub(r"\s|\r|\n", "-", item[1]), item[2]
        if level == 1:
            tag_dict[pagenum] = content
        else:
            while len(level_stack) != 0 and level_stack[-1][0] >= level:
                level_stack.pop()
            content = f"{level_stack[-1][1]}::{content}"
            tag_dict[pagenum] = content
        level_stack.append([level, content, pagenum])
    return tag_dict


def on_anki_field_insert_handle1(self, clipboxlist: "list"):
    count = 0
    total = len(clipboxlist)
    bookdict = {}
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    for clipbox in clipboxlist:
        count += 1
        self.job_progress(self.state_insert_DB, 3, count / total)
        # self.on_job_progress.emit([self.state_insert_cardfield,ceil( 100*2/self.job_part+(count/total)*100/self.job_part )])
        card_id_li = clipbox["card_id"].split(",")
        for card_id in card_id_li:
            pdfname = os.path.basename(clipbox["pdfname"])
            pdfname_in_tag = re.sub(r"\s|\r|\n", "-", pdfname[0:-4])
            note = mw.col.getCard(int(card_id)).note()
            html = reduce(lambda x, y: x + "\n" + y, note.fields)
            if clipbox["uuid"] not in html:
                note.fields[clipbox["QA"]] += f"""<img src="{pngfileprefix}{clipbox["uuid"]}_.png">\n"""
            if clipbox["text_"] != "" and clipbox["uuid"] not in html:
                note.fields[clipbox["textQA"]] += f"""<p id="{clipbox["uuid"]}">{clipbox["text_"]}<p>\n"""

            note.addTag(f"""hjp-bilink::timestamp::{timestamp}""")
            note.addTag(f"""hjp-bilink::books::{pdfname_in_tag}::page::{clipbox["pagenum"]}""")
            # 下面都是为了得到PDF的书签
            path = objs.SrcAdmin.get
            jsonfilename = os.path.join(path.dir_root, path.dir_user_files, path.dir_bookmark, pdfname[0:-3] + "json")
            if os.path.exists(jsonfilename):
                bookdict = json.loads(open(jsonfilename, "r", encoding="utf-8").read())
            else:
                doc: "fitz.Document" = fitz.open(clipbox["pdfname"])
                toc = doc.get_toc()
                bookdict = bookmark_to_tag(toc)
                json.dump(bookdict, open(jsonfilename, "w", encoding="utf-8"), indent=4, ensure_ascii=False)
            pagelist = sorted(list(bookdict.keys()), key=lambda x: int(x))
            # showInfo(pagelist.__str__())
            atbookmark = -1
            for idx in range(len(pagelist)):
                if int(pagelist[idx]) > clipbox["pagenum"]:
                    if idx > 0:
                        atbookmark = pagelist[idx - 1]
                    break
            if atbookmark != -1:
                note.addTag(f"""hjp-bilink::books::{pdfname_in_tag}::bookmark::{bookdict[atbookmark]}""")
            note.flush()
    return timestamp


def anki_file_create_handle1(self, clipboxslist):
    count = 0
    total = len(clipboxslist)
    mediafolder = os.path.join(mw.pm.profileFolder(), "collection.media")
    for clipbox in clipboxslist:
        count += 1
        self.job_progress(self.state_create_png, 4, count / total)
        doc: "fitz.Document" = fitz.open(clipbox["pdfname"])
        # 0.144295302 0.567695962 0.5033557047 0.1187648456
        page = doc.load_page(clipbox["pagenum"])
        pagerect: "fitz.rect_like" = page.rect
        x0, y0 = clipbox["x"] * pagerect.width, clipbox["y"] * pagerect.height
        x1, y1 = x0 + clipbox["w"] * pagerect.width, y0 + clipbox["h"] * pagerect.height
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=fitz.Rect(x0, y0, x1, y1))
        pngdir = os.path.join(mediafolder, f"""{pngfileprefix}{clipbox["uuid"]}_.png""")
        if os.path.exists(pngdir):
            os.remove(pngdir)
        pixmap.save(pngdir)


e = events.AnkiCardCreateEvent
anki_create_card_handle = {
    e.ClipBoxType: on_anki_create_card_handle1
}

e = events.AnkiFieldInsertEvent
anki_field_insert_handle = {
    e.ClipBoxBeginType: on_anki_field_insert_handle1
}

e = events.AnkiFileCreateEvent
anki_file_create_handle = {
    e.ClipperCreatePNGType: anki_file_create_handle1
}
