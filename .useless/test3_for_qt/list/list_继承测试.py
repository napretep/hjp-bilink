class mydict(dict):

    def to_string(self):
        fun(**self)


def fun(**kwargs):
    print(kwargs)


if __name__ == "__main__":
    mydict().to_string()
