import sys


class U:
    def __init__(self, C, B):
        self.C = C
        self.B = B

        def say(X):
            # print(sys.)
            print(sys._getframe(0))
            print(sys._getframe(1).f_code.co_name == f.__name__)
            print(f"hello {self.__dict__[X]}")

        self.say = say
        print(self.say)


def f():
    u = U("1", "2")
    u.say("C")


if __name__ == "__main__":
    f()
