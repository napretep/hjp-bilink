import copy
import re,zipfile
import sys,os,json
from shutil import copy2

THIS_FOLDER = os.path.curdir
baseconfig = json.load(open("baseInfo.json","r",encoding="utf-8"))
excludeFile = ["clipper2","clipper3","__pycache__"]
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
    from lib.debugState import ISDEBUG
    if ISDEBUG:
        raise ValueError("ISDEBUG=True!")
def pycache_check():
    for root,dirs,files in os.walk(THIS_FOLDER,onerror=lambda x:print("wrong direction")):
        for i in dirs:
            if r".\lib" in root.__str__() and "__pycache__" in i:

                raise ValueError("__pycache__ exists in "+root.__str__())

def status_check():
    check_is_debug()
    # pycache_check()

def ankiaddon_make(version):
    status_check()
    repository = os.path.join(r"D:\备份盘\个人创作成果\代码\hjp-bilink历代版本",version[:-2])
    if not os.path.exists(repository):
        os.mkdir(repository)
    zip_name = os.path.join(repository,"hjp_bilink.zip")
    f = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    # root 是 当前文件夹的路径, dirs 是当前文件夹的直接子文件夹, files是当前文件夹下的文件
    for root, dirs, files in os.walk(THIS_FOLDER, onerror=lambda x: print("wrong direction")):
        if any([ex in root for ex in excludeFile ]):
            continue
        if r".\lib" in root.__str__():
            for file in files:
                f.write(os.path.join(root, file))
        if root == os.path.curdir:
            for file in ["manifest.json", "__init__.py", "log.txt", "linkpool.json","data_crash.txt"]:
                f.write(os.path.join(root, file))
    f.close()
    filename =os.path.join(repository, f"{version}.ankiaddon")
    if os.path.exists(filename):
        os.remove(filename)
    os.rename(zip_name, filename)
    print(f"{version}构建完成!")
    pass



if __name__ == "__main__":
    version=input("请输入版本号\n")
    if not re.search("\d+\.\d+\.\d+",version):
        print("请输入符合格式的版本号!")
    for webOrLocal in ["w","l"]:
        with open("./__init__.py","r",encoding="utf-8") as f:
            pyFile = f.read()
            pyFile = re.sub("""(?<=connectors.funcs.G.src.ADDON_VERSION=")\d+\.\d+\.\d+\.[wl]""",version+"."+webOrLocal, pyFile) # w表示ankiweb,l表示local
            print(pyFile)
        with open("./__init__.py","w",encoding="utf-8") as f:
            f.write(pyFile)
        ankiaddon_make(version+"."+webOrLocal)