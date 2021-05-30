from arknights.resource import POSITION_PATH
from os import walk
from os.path import join, dirname, isfile, splitext, isdir, basename
from json import load, dump
import os
import shutil
from .common import Bcolors

JSON_NAME = 'pos.json'


def log(s: str):
    print(Bcolors.WARNING + s + Bcolors.ENDC)


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


def _create_info_if_not_exist(path: str):
    if not isfile(path):
        with open(path, 'w') as _f:
            _f.write('{}')


def move(_path_: str, new_path: str):
    target_path = _path_.replace('/', '\\')
    dst_path = new_path.replace('/', '\\')
    for json_path in find_all_json(POSITION_PATH):
        dir_name = remove_root(dirname(json_path), POSITION_PATH, '\\')
        with open(json_path, 'r+', encoding='utf-8') as f:
            _json = load(f)
        for key in _json.keys():
            if join(dir_name, key) == target_path:
                log('sure to move position {} to {}?[y/n]'.format(_path_, new_path))
                ans = None
                while ans not in ['y', 'n']:
                    ans = input()
                if ans == 'y':
                    info = _json[key]
                    # create destination dictionary
                    dst_dir = join(POSITION_PATH, dirname(dst_path))
                    new_json_path = join(dst_dir, JSON_NAME)
                    os.makedirs(dst_dir, exist_ok=True)  # create dictionary recursively
                    _create_info_if_not_exist(new_json_path)

                    # write info to new json
                    with open(new_json_path, 'r+', encoding='utf-8') as f:
                        _new_json = load(f)
                    new_key = basename(new_path)
                    if new_key in _new_json:
                        log('position {} already exists , do you want to overwrite it?[y/n]'
                            .format(new_path))
                        ans = None
                        while ans not in ['y', 'n']:
                            ans = input()
                        if ans == 'n':
                            return
                    _new_json[new_key] = info
                    with open(new_json_path, 'w+', encoding='utf-8') as f:
                        dump(_new_json, f, indent=4)

                    # delete info from original json
                    with open(json_path, 'r+', encoding='utf-8') as f:
                        _json = load(f)
                    _json.pop(key)
                    with open(json_path, 'w+', encoding='utf-8') as f:
                        dump(_json, f, indent=4)
                    log('successfully move position {} to {}'.format(_path_, new_path))
                    clear_file_tree(POSITION_PATH, json_name=JSON_NAME)
                    log('cleared file tree')
                    return
                else:
                    return
    else:
        log('Error: position {} not found'.format(_path_))
