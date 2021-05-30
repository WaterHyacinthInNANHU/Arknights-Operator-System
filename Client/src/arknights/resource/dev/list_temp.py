from arknights.resource import TEMPLATE_PATH
from os import walk
from os.path import join, dirname, splitext
from json import load
from .common import Bcolors


def log(s: str):
    print(Bcolors.OKCYAN + s + Bcolors.ENDC)


def find_all_json(base: str):
    for root, ds, fs in walk(base):
        for f in fs:
            _, file_extension = splitext(f)
            if file_extension != '.json':
                continue
            fullname = join(root, f)
            yield fullname


def remove_root(path: str, root: str, delimiter: str = '\\') -> str:
    sub_path = path.split(delimiter)
    sub_root = root.split(delimiter)
    for item in sub_root:
        sub_path.remove(item)
    res = delimiter.join(str(x) for x in sub_path)
    return res


def ls():
    # # debug
    # for json_path in find_all_file(POSITION_PATH):
    #     log(remove_root(dirname(json_path), POSITION_PATH, '\\'))
    log(' = list of all templates = ')
    for json_path in find_all_json(TEMPLATE_PATH):
        dir_name = remove_root(dirname(json_path), TEMPLATE_PATH, '\\')
        with open(json_path, 'r+', encoding='utf-8') as f:
            _json = load(f)
        for key in _json.keys():
            log(join(dir_name, key).replace('\\', '/'))
