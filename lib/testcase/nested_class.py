class A:
    class B:
        class C:
            def say(self):
                print('hello' + self.__class__.__name__)

        class D:
            def say(self):
                print('hello' + self.__class__.__name__)

    def __init__(self):
        self.c = self.B.C()
        self.d = self.B.D()
        self.sayc = self.c.say
        self.sayd = self.d.say


if __name__ == "__main__":
    a = A()
    a.sayc()
    a.sayd()
