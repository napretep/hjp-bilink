from dataclasses import dataclass


@dataclass
class A:
    b: "int" = 0
    c: "int" = 1


@dataclass
class B(A):
    e: "int" = 2
    f: "int" = 3

    def __post_init__(self):
        self.e: "str" = "x"

    def say(self, s):
        print(s + self.e)


if __name__ == "__main__":
    b = B()

    b.say("hi ")
