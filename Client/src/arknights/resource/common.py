from dataclasses import dataclass
from PIL import Image


@dataclass
class TemplateData:
    _path_: str
    location: tuple
    upper_left: tuple
    bottom_right: tuple
    resolution: tuple
    image: Image
    size: tuple
    path: str
    timestamp: str


@dataclass
class PositionData:
    _path_: str
    resolution: tuple
    position: tuple
    timestamp: str


@dataclass
class RectangleData:
    _path_: str
    resolution: tuple
    upper_left: tuple
    bottom_right: tuple
    center: tuple
    timestamp: str
