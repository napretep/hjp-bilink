class A:
    def __init__(self, B):
        self.B = B

    def hi(self):
        print("hi")


class B:
    def __init__(self):
        self.C = 1
        self.A = A(B)
        self.hi = self.A.hi


import sys

if __name__ == '__main__':
    Y = B()
    print(sys.getrefcount(Y))
