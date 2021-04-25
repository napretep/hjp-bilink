import json

from .linkData_syncer import DataSyncer
from .utils import Config
from aqt import mw
from bs4 import BeautifulSoup, element


class LinkData_writer(Config):

    def __init__(self, card_id, data: dict):
        super().__init__()
        self.card_id = int(card_id)
        self.storageLocation = self.user_cfg["linkInfoStorageLocation"]
        self.fieldPostion = self.user_cfg["appendNoteFieldPosition"]
        self.consolerName = self.base_cfg["consoler_Name"]
        self.data_version = self.base_cfg["data_version"]
        self.data = data
        self.method_dict = {
            0: self.DB_data_write,
            1: self.Field_data_write,
            2: self.JSON_data_write
        }

    def write(self):
        self.data = DataSyncer(self.data).sync().remove_leaves().data
        self.method_dict[self.storageLocation]()
        pass

    def DB_data_write(self):
        pass

    def Field_data_write(self):
        note = mw.col.getCard(self.card_id).note()
        field = note.fields[self.fieldPostion]
        HTML = BeautifulSoup(field, "html.parser")
        comment = HTML.find(text=lambda text: isinstance(text, element.Comment) and self.consolerName in text)
        if comment is not None:
            comment.extract()
        script = HTML.new_tag("script", attrs={"id": f"{self.consolerName}info_v{self.data_version}"})
        script.string = f"{self.consolerName}info={json.dumps(self.data, ensure_ascii=False)}"
        HTML = HTML.__str__() + "<!--" + script.__str__() + "-->"
        note.fields[self.fieldPostion] = HTML
        note.flush()
        pass

    def JSON_data_write(self):
        pass
