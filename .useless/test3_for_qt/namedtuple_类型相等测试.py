from collections import namedtuple

if __name__ == "__main__":
    a = namedtuple("x", "uu vv")

    v = a(uu=2, vv=3)

    print(type(v) == a)
