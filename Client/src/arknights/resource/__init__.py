from os.path import dirname, isdir, join, isfile, basename
from os import makedirs
from json import load, dump
import datetime
from .common import *
from config import root


def mkdir(path):
    if not isdir(path):
        makedirs(path)


# root: current work dictionary ......./Client/src/
TEMPLATE_PATH = join(dirname(root), "resources\\templates")
POSITION_PATH = join(dirname(root), "resources\\positions")
RECTANGLE_PATH = join(dirname(root), "resources\\rectangle")
mkdir(TEMPLATE_PATH)
mkdir(POSITION_PATH)
mkdir(RECTANGLE_PATH)


def _create_info_if_not_exist(path: str):
    if not isfile(path):
        with open(path, 'w') as _f:
            _f.write('{}')


def save_template(temp: Image, resolution: tuple, location: tuple, _path_: str, extension: str, force: bool = False) \
        -> str:
    path = join(TEMPLATE_PATH, _path_)
    name = basename(path)
    dictionary = dirname(join(TEMPLATE_PATH, path))
    if not isdir(dictionary):
        makedirs(dictionary)
    info_path = join(dictionary, 'info.json')
    _create_info_if_not_exist(info_path)
    with open(info_path, 'r+', encoding='utf-8') as f:
        _json = load(f)
    if name in _json:
        if not force:
            raise KeyError('template name ' + name + ' already exist！')
    # save template
    save_path = join(dictionary, name) + extension
    temp.save(save_path)
    # register template information
    _json[name] = {}
    _json[name]['location'] = location
    _json[name]['resolution'] = resolution
    _json[name]['path'] = _path_ + extension
    _json[name]['size'] = temp.size
    _json[name]['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    with open(info_path, 'w+', encoding='utf-8') as f:
        dump(_json, f, indent=4)
    return save_path


def load_template(_path_: str) -> TemplateData:
    path = join(TEMPLATE_PATH, _path_)
    name = basename(path)
    dictionary = dirname(path)
    info_path = join(dictionary, 'info.json')
    if not isfile(info_path):
        raise ValueError('template {} not found!'.format(_path_))
    with open(info_path, 'r+', encoding='utf-8') as f:
        _json = load(f)
    if name not in _json:
        raise ValueError('template {} not found!'.format(_path_))
    info_json = _json[name]
    image = Image.open(join(TEMPLATE_PATH, info_json['path']))
    template = TemplateData(
        location=tuple(info_json['location']),
        resolution=tuple(info_json['resolution']),
        upper_left=(int(info_json['location'][0] - info_json['size'][0] / 2),
                    int(info_json['location'][1] - info_json['size'][1] / 2)
                    ),
        bottom_right=(int(info_json['location'][0] + info_json['size'][0] / 2 + 0.5),
                      int(info_json['location'][1] + info_json['size'][1] / 2 + 0.5)
                      ),
        size=tuple(info_json['size']),
        path=str(info_json['path']),
        timestamp=str(info_json['timestamp']),
        _path_=str(_path_),
        image=image
    )
    return template


def is_template_exist(_path_):
    try:
        load_template(_path_)
    except ValueError:
        return False
    return True


def save_position(pos: tuple, resolution: tuple, _path_: str, force: bool = False) -> str:
    path = join(POSITION_PATH, _path_)
    name = basename(path)
    dictionary = dirname(join(POSITION_PATH, path))
    if not isdir(dictionary):
        makedirs(dictionary)
    info_path = join(dictionary, 'pos.json')
    _create_info_if_not_exist(info_path)
    with open(info_path, 'r+', encoding='utf-8') as f:
        _json = load(f)
    if name in _json:
        if not force:
            raise KeyError('position name ' + name + ' already exist！')
    # register position to json
    _json[name] = {}
    _json[name]['position'] = pos
    _json[name]['resolution'] = resolution
    _json[name]['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    with open(info_path, 'w+', encoding='utf-8') as f:
        dump(_json, f, indent=4)
    return info_path


def load_position(_path_: str) -> PositionData:
    path = join(POSITION_PATH, _path_)
    name = basename(path)
    dictionary = dirname(path)
    info_path = join(dictionary, 'pos.json')
    if not isfile(info_path):
        raise ValueError('position {} not found!'.format(_path_))
    with open(info_path, 'r+', encoding='utf-8') as f:
        _json = load(f)
    if name not in _json:
        raise ValueError('position {} not found!'.format(_path_))
    info_json = _json[name]
    position = PositionData(
        resolution=tuple(info_json['resolution']),
        timestamp=str(info_json['timestamp']),
        _path_=str(_path_),
        position=tuple(info_json['position'])
    )
    return position


def is_position_exist(_path_):
    try:
        load_position(_path_)
    except ValueError:
        return False
    return True


def save_rectangle(upper_left: tuple, bottom_right: tuple, resolution: tuple, _path_: str,
                   force: bool = False) -> str:
    path = join(RECTANGLE_PATH, _path_)
    name = basename(path)
    dictionary = dirname(join(RECTANGLE_PATH, path))
    if not isdir(dictionary):
        makedirs(dictionary)
    info_path = join(dictionary, 'rect.json')
    _create_info_if_not_exist(info_path)
    with open(info_path, 'r+', encoding='utf-8') as f:
        _json = load(f)
    if name in _json:
        if not force:
            raise KeyError('rectangle name ' + name + ' already exist！')
    # register position to json
    _json[name] = {}
    _json[name]['upper_left'] = upper_left
    _json[name]['bottom_right'] = bottom_right
    _json[name]['center'] = (int((upper_left[0] + bottom_right[0]) / 2), int((upper_left[1] + bottom_right[1]) / 2))
    _json[name]['resolution'] = resolution
    _json[name]['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
    with open(info_path, 'w+', encoding='utf-8') as f:
        dump(_json, f, indent=4)
    return info_path


def load_rectangle(_path_: str) -> RectangleData:
    path = join(RECTANGLE_PATH, _path_)
    name = basename(path)
    dictionary = dirname(path)
    info_path = join(dictionary, 'rect.json')
    if not isfile(info_path):
        raise ValueError('rectangle {} not found!'.format(_path_))
    with open(info_path, 'r+', encoding='utf-8') as f:
        _json = load(f)
    if name not in _json:
        raise ValueError('rectangle {} not found!'.format(_path_))
    info_json = _json[name]
    rectangle = RectangleData(
        resolution=tuple(info_json['resolution']),
        timestamp=str(info_json['timestamp']),
        _path_=str(_path_),
        upper_left=tuple(info_json['upper_left']),
        bottom_right=tuple(info_json['bottom_right']),
        center=tuple(info_json['center'])
    )
    return rectangle


def is_rectangle_exist(_path_):
    try:
        load_rectangle(_path_)
    except ValueError:
        return False
    return True
