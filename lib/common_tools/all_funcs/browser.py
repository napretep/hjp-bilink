from .basic_funcs import *
class BrowserOperation:
    @staticmethod
    def search(s) -> "Optional[Browser]":
        """注意,如果你是自动搜索,需要自己激活窗口"""
        if ISLOCALDEBUG:
            return
        browser: "Browser" = BrowserOperation.get_browser()
        # if browser is not None:
        if not isinstance(browser, Browser):
            browser: "Browser" = dialogs.open("Browser", mw)

        browser.search_for(s)
        return browser

    @staticmethod
    def refresh():
        browser: "Browser" = BrowserOperation.get_browser()
        if isinstance(browser, Browser):
            # if dialogs._dialogs["Browser"][1] is not None:
            browser.sidebar.refresh()
            browser.model.reset()
            browser.editor.setNote(None)

    @staticmethod
    def get_browser(OPEN=False):
        browser: Browser = dialogs._dialogs["Browser"][1]
        if not isinstance(browser, Browser) and OPEN:
            browser = dialogs.open("Browser")
        # browser.forget_cards
        return browser

    @staticmethod
    def get_selected_card():
        browser = BrowserOperation.get_browser(OPEN=True)
        card_ids = browser.selected_cards()
        result = [G.objs.LinkDataPair(str(card_id), 导入.card.CardOperation.desc_extract(card_id)) for card_id in card_ids]
        return result