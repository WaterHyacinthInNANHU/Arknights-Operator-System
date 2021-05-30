from arknights.resource import RECTANGLE_PATH
from os import walk
from os.path import join, dirname, splitext, isdir
from json import load, dump
import shutil
import os
from .common import Bcolors

JSON_NAME = 'rect.json'


def log(s: str):
    print(Bcolors.RED + s + Bcolors.ENDC)


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


def clear_file_tree(target_dir: str, json_name: str):
    items = os.listdir(target_dir)
    # clear sub-dictionaries first
    for item in items:
        item_path = join(target_dir, item)
        if isdir(item_path):
            clear_file_tree(item_path, json_name)
    # find info.json, delete it if json is empty
    if json_name in items:
        json_path = join(target_dir, json_name)
        with open(json_path, 'r+', encoding='utf-8') as f:
            _json = load(f)
        if len(_json.keys()) == 0:
            os.remove(json_path)
    # delete target dictionary if dictionary is empty
    if len(os.listdir(target_dir)) == 0:
        shutil.rmtree(target_dir)


def delete(_path_: str):
    target_path = _path_.replace('/', '\\')
    for json_path in find_all_json(RECTANGLE_PATH):
        dir_name = remove_root(dirname(json_path), RECTANGLE_PATH, '\\')
        with open(json_path, 'r+', encoding='utf-8') as f:
            _json = load(f)
        for key in _json.keys():
            if join(dir_name, key) == target_path:
                log('sure to delete rectangle {}?[y/n]'.format(_path_))
                ans = None
                while ans not in ['y', 'n']:
                    ans = input()
                if ans == 'y':
                    # delete from json
                    _json.pop(key)
                    with open(json_path, 'w+', encoding='utf-8') as f:
                        dump(_json, f, indent=4)
                    log('successfully deleted rectangle {}'.format(_path_))
                    clear_file_tree(RECTANGLE_PATH, json_name=JSON_NAME)
                    log('cleared file tree')
                    return
                else:
                    return
    else:
        log('Error: position {} not found'.format(_path_))
