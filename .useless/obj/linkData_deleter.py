from aqt import mw
from bs4 import BeautifulSoup, element
import os
from .utils import Config,JSONFile_FOLDER
from .handle_DB import LinkDataDBmanager

class LinkDataDeleter(Config):
    def __init__(self, card_id):
        super().__init__()
        self.card_id = int(card_id)
        self.storageLocation = self.user_cfg["linkInfoStorageLocation"]
        self.fieldPostion = self.user_cfg["appendNoteFieldPosition"]
        self.consolerName = self.base_cfg["consoler_Name"]
        self.data_version = self.base_cfg["data_version"]
        self.method_dict = {
            0: self.DB_data_delete,
            1: self.Field_data_delete,
            2: self.JSON_data_delete
        }

    def delete(self):
        self.method_dict[self.storageLocation]()

    def DB_data_delete(self):
        DB = LinkDataDBmanager()
        DB.data_remove(self.card_id)

    def Field_data_delete(self):
        note = mw.col.getCard(self.card_id).note()
        field = note.fields[self.fieldPostion]
        HTML = BeautifulSoup(field, "html.parser")
        comment = HTML.find(text=lambda text: isinstance(text, element.Comment) and self.consolerName in text)
        if comment is not None:
            comment.extract()
        note.fields[self.fieldPostion] = HTML.__str__()
        note.flush()

    def JSON_data_delete(self):
        path = os.path.join(JSONFile_FOLDER,str(self.card_id)+".json")
        if os.path.exists(path):
            os.remove(path)
