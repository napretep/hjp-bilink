import re

if __name__ == "__main__":
    v_str = re.search(r"(\d+)\.(\d+)\.(\d+)", "1.1.1").groups()
    print(v_str)
    pass
