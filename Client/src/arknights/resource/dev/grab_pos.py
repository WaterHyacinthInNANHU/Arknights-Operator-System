# used to grab template from screen
import sys
import signal
from arknights.player import Player
from arknights.resource import save_position
import cv2
from arknights.imgops import pil2cv
from .common import Bcolors


def log(s: str):
    print(Bcolors.OKGREEN + s + Bcolors.ENDC)


def signal_handler(sig):
    log('Caught ' + str(sig))
    log('Exit')
    del PLAYER
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


global display_img
global point
PLAYER = Player()
PLAYER.connect_device()
DISPLAY_WINDOW = 'screenshot'
EXTENSION = '.png'


def on_mouse(event, x, y, flags, param):
    global display_img, point
    img2 = display_img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        point = (x, y)
        cv2.circle(img2, point, 5, (0, 0, 255), 10)
        cv2.imshow(DISPLAY_WINDOW, img2)


def grab(save=True):
    global display_img, point
    img = PLAYER.screenshot()
    display_img = pil2cv(img)
    cv2.namedWindow(DISPLAY_WINDOW, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(DISPLAY_WINDOW, on_mouse)
    cv2.imshow(DISPLAY_WINDOW, display_img)
    cv2.waitKey(0)
    cv2.destroyWindow(DISPLAY_WINDOW)
    resolution = PLAYER.viewport
    log('position {}'.format(point))
    if save:
        while True:
            path = input('please input the path to save this position\n')
            try:
                save_path = save_position(point, resolution, path)
            except KeyError:
                log('position name has already exist, do you want to overwrite it?[y/n]')
                ans = None
                while ans not in ['y', 'n']:
                    ans = input()
                if ans == 'y':
                    save_path = save_position(point, resolution, path, force=True)
                    log('position successfully saved to ' + save_path)
                    break
                else:
                    break
            else:
                log('position successfully saved to ' + save_path)
                break
