from . import funcs


def signal_wrapper(signal=None, **signal_kwargs):
    def wrapper(func):
        def do(*args, **kwargs):
            result = func(*args, **kwargs)
            if signal is not None:
                signal.emit(signal_kwargs)
            return result

        return do

    return wrapper


def func_wrapper(before=None, after=None, **signal_kwargs):
    """
    Args:
        before: list[list[callable,kwargs]]
        funcli: list[callable,kwargs]
        **signal_kwargs:

    Returns:

    """

    def wrapper(func):
        def do(*args, **kwargs):
            if before is not None:
                for f, k in before:
                    if k is not None:
                        f(k)
                    else:
                        f()
            result = func(*args, **kwargs)
            if after is not None:
                for f, k in after:
                    if k is not None:
                        f(k)
                    else:
                        f()
            return result

        return do

    return wrapper


def Previewer_close_wrapper(func):
    def do(self, QCloseEvent):
        result = func(self, QCloseEvent)
        funcs.PDFprev_close(self.card().id, all=True)
        return result

    return do


def BrowserPreviewer_card_change_wrapper(func):
    def do(self):
        funcs.PDFprev_close(self.card().id, all=True)
        result = func(self)
        return result

    return do
