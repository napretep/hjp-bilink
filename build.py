import re,zipfile
import sys,os,json
THIS_FOLDER = os.path.curdir
baseconfig = json.load(open("baseInfo.json","r",encoding="utf-8"))

class addon_version:
    def __init__(self,v_str):
        self.v = [int(i) for i in v_str.split(".")]

    def __lt__(self, other):
        if self.v[0]!=other.v[0]:
            return self.v[0]< other.v[0]
        elif self.v[1]!=other.v[1]:
            return self.v[1]< other.v[1]
        else:
            return self.v[2]< other.v[2]

def cmpkey(path):
    filename = os.path.basename(path)
    v_str = re.search(r"\d+\.\d+\.\d",filename).group()
    return addon_version(v_str)

def check_version():

    base_version = baseconfig["VERSION"]
    VERSION_FOLDER = baseconfig["versionsDir"]
    path1 = os.path.join(THIS_FOLDER, VERSION_FOLDER)
    liname = os.listdir(path1)
    liname.sort(reverse=True, key=cmpkey)
    update_version = re.search(r"\d+\.\d+\.\d",liname[0]).group()
    if update_version!=base_version:
        raise ValueError("update_version!=base_version")

def check_is_debug():
    ISDEBUG = baseconfig["ISDEBUG"]==1
    if ISDEBUG:
        raise ValueError("ISDEBUG=True!")
def pycache_check():
    for root,dirs,files in os.walk(THIS_FOLDER,onerror=lambda x:print("wrong direction")):
        for i in dirs:
            if r".\lib" in root.__str__() and i == "__pycache__":
                raise ValueError("__pycache__ exists in "+root.__str__())

def status_check():
    check_is_debug()
    check_version()
    pycache_check()

def ankiaddon_make():
    f = zipfile.ZipFile("hjp_bilink.zip", "w", zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(THIS_FOLDER, onerror=lambda x: print("wrong direction")):
        if r".\lib" in root.__str__():
            for file in files:
                f.write(os.path.join(root, file))
        if root == os.path.curdir:
            for file in ["meta.json", "baseInfo.json", "__init__.py", "log.txt", "input.json"]:
                f.write(os.path.join(root, file))
    f.close()
    if os.path.exists("hjp-bilink.ankiaddon"):
        os.remove("hjp-bilink.ankiaddon")
    os.rename("hjp_bilink.zip", "hjp-bilink.ankiaddon")
    pass



if __name__ == "__main__":
    status_check()
    print("no problem, then do zipfile")
    ankiaddon_make()
    print("done!")