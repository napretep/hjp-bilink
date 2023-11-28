import copy
import re, zipfile
import shutil
import sys, os, json
from shutil import copy2

THIS_FOLDER = os.path.curdir
LOCAL_FOLDER = os.path.join("..","hjp_linkmaster")

metaJson = os.path.join(THIS_FOLDER,"meta.json")

localMetaJson = os.path.join(LOCAL_FOLDER,"meta.json")
# baseconfig = json.load(open("baseInfo.json", "r", encoding="utf-8"))
excludeFile = ["clipper2", "clipper3", "__pycache__"]
linux_addon_path = "/home/napretep/.local/share/Anki2/addons21/"
linux_addon_repository = "/home/napretep/addons"
windows_addon_repository = r"D:\hjp_linkmaster历代版本"
addon_name = json.load(open("manifest.json", "r", encoding="utf-8"))["name"]
is_win = sys.platform.startswith("win32")

class addon_version:
    def __init__(self, v_str):
        self.v = [int(i) for i in v_str.split(".")]

    def __lt__(self, other):
        if self.v[0] != other.v[0]:
            return self.v[0] < other.v[0]
        elif self.v[1] != other.v[1]:
            return self.v[1] < other.v[1]
        else:
            return self.v[2] < other.v[2]


def set_metaJson_disabled(json_path,bool_value):
    data = json.load(open(json_path,"r",encoding="utf-8"))
    data["disabled"]=bool_value
    json.dump(data,open(json_path,"w",encoding="utf-8"))


def cmpkey(path):
    filename = os.path.basename(path)
    v_str = re.search(r"\d+\.\d+\.\d", filename).group()
    return addon_version(v_str)


# def check_version():
#     base_version = baseconfig["VERSION"]
#     VERSION_FOLDER = baseconfig["versionsDir"]
#     path1 = os.path.join(THIS_FOLDER, VERSION_FOLDER)
#     liname = os.listdir(path1)
#     liname.sort(reverse=True, key=cmpkey)
#     update_version = re.search(r"\d+\.\d+\.\d", liname[0]).group()
#     if update_version != base_version:
#         raise ValueError("update_version!=base_version")


def check_is_debug():
    from lib.debugState import ISDEBUG
    if ISDEBUG:
        raise ValueError("ISDEBUG=True!")


def pycache_check():
    for root, dirs, files in os.walk(THIS_FOLDER, onerror=lambda x: print("wrong direction")):
        for i in dirs:
            if r".\lib" in root.__str__() and "__pycache__" in i:
                raise ValueError("__pycache__ exists in " + root.__str__())


def status_check():
    if is_win:
        check_is_debug()
    # pycache_check()


# def copy_to_linux_addon_dir():
#     linux_addon_path = "/home/napretep/.local/share/Anki2/addons21/"
#     addon_name = json.load(open("manifest.json", "r", encoding="utf-8"))["name"]
#     target_path = os.path.join(linux_addon_path, addon_name)
#     if os.path.exists(target_path):
#     #     os.
#         os.system(f"rm -rf {target_path}")
#     os.mkdir(target_path)
#     for root, dirs, files in os.walk(THIS_FOLDER, onerror=lambda x: print("wrong direction")):
#         if any([ex in root for ex in excludeFile]):
#             continue
#
#         if "./lib" in root.__str__():
#             for file in files:
#                 old_path = os.path.join(root, file)
#                 new_path = os.path.join(linux_addon_path, addon_name, root[2:])
#                 print(new_path)
#                 if not os.path.exists(new_path):
#                     os.system(f"mkdir {new_path}")
#                 # print(os.path.join(linux_addon_path,addon_name,root[2:],file))
#                 # shutil.copyfile(old_path,os.path.join(new_path,file))
#                 os.system(f"cp {old_path} {os.path.join(new_path,file)}")
#
#         if root == os.path.curdir:
#             for file in ["manifest.json", "__init__.py", "log.txt", "linkpool.json", "data_crash.txt"]:
#                 shutil.copyfile(os.path.join(root, file),os.path.join(linux_addon_path, addon_name, root[2:], file))
#
#
#     pass


def ankiaddon_make(version):
    status_check()
    addon_repository_fold =windows_addon_repository  if  is_win else linux_addon_repository
    repository = os.path.join(addon_repository_fold , version[:-2])
    print(repository)
    if not os.path.exists(repository):
        os.mkdir(repository)
    zip_name = os.path.join(repository, "hjp_linkmaster.zip")
    f = zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED)
    # root 是 当前文件夹的路径, dirs 是当前文件夹的直接子文件夹, files是当前文件夹下的文件
    for root, dirs, files in os.walk(THIS_FOLDER, onerror=lambda x: print("wrong direction")):
        if any([ex in root for ex in excludeFile]):
            continue
        if re.search(r"\.[\\/]lib",root):
            for file in files:
                print(root, dirs, files)
                f.write(os.path.join(root, file))
        if root == os.path.curdir:
            for file in ["manifest.json", "__init__.py", "log.txt", "linkpool.json", "data_crash.txt"]:
                f.write(os.path.join(root, file))
    f.close()
    filename = os.path.join(repository, f"{version}.ankiaddon")
    if os.path.exists(filename):
        os.remove(filename)
    os.rename(zip_name, filename)
    print(f"{version}构建完成!")

    return filename
    pass


if __name__ == "__main__":

    if is_win:
        version = input("请输入版本号\n")
        if version:
    # if sys.platform.startswith("win32"):
            with open("./lib/debugState.py","r",encoding="utf-8") as f:
                text = f.read()
                text = re.sub(r"""(?<=ISDEBUG = )\w+""","False",text)
            with open("./lib/debugState.py","w",encoding="utf-8") as f:
                f.write(text)


            for webOrLocal in ["w", "l"]:
                with open("./__init__.py", "r", encoding="utf-8") as f:
                    pyFile = f.read()
                    pyFile = re.sub("""(?<=connectors.funcs.G.src.ADDON_VERSION=").*?\"""",
                                    version + "." + webOrLocal + '"', pyFile)  # w表示ankiweb,l表示local
                    print(pyFile)
                with open("./__init__.py", "w", encoding="utf-8") as f:
                    f.write(pyFile)
                filename = ankiaddon_make(version + "." + webOrLocal)
                if not is_win: break

            with open("./__init__.py", "r", encoding="utf-8") as f:
                pyFile = f.read()
                pyFile = re.sub("""(?<=connectors.funcs.G.src.ADDON_VERSION=").*?\"""",'dev"', pyFile)  # w表示ankiweb,l表示local
            with open("./__init__.py", "w", encoding="utf-8") as f:
                f.write(pyFile)
            with open("./lib/debugState.py","r",encoding="utf-8") as f:
                text = f.read()
                text = re.sub(r"""(?<=ISDEBUG = )\w+""","True",text)
            with open("./lib/debugState.py","w",encoding="utf-8") as f:
                f.write(text)
            # if is_win:
            #     os.startfile(repository)
            # else:
            #     # print(filename)
            #     programname = "anki"
            #     os.system(f"{programname} {filename}")
            if input("是否立即安装插件?输入任意字符表示打开,直接回车示不打开\n"):

                set_metaJson_disabled(metaJson,True)
                set_metaJson_disabled(localMetaJson, False)
                os.system(f'anki "{filename}" ')
            elif input("是否立即打开插件目录?输入任意字符表示打开,直接回车示不打开\n"):
                set_metaJson_disabled(metaJson,True)
                set_metaJson_disabled(localMetaJson,False)
                os.startfile(os.path.split(filename)[0])
    # else:
    #     print("linux 調試模式")
    #     version = input("请输入版本号\n")
        # copy_to_linux_addon_dir()
        # print("ok")