def wrapper(func):
    def do(*args, **kwargs):
        print("hi-----")
        result = func(*args, **kwargs)
        return result

    return do


class dict2(dict):
    def __init__(self, data):
        super().__init__(data)

    def __getitem__(self, item):
        return super().__getitem__(item)


if __name__ == "__main__":
    a = dict2({1: 1})
    a.__getitem__ = wrapper(a.__getitem__)
    print(a[1])
