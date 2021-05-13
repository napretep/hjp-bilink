from functools import partial

def add(x,y):
    return x+y
inc = partial(add,x=1)

if __name__ == '__main__':
    print(inc(y=1))