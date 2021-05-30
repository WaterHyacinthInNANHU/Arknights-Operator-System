# used to grab template from screen
import sys
import signal
from arknights.player import Player
from arknights.resource import save_template
from arknights.imgops import pil2cv
import cv2
from .common import Bcolors


def log(s: str):
    print(Bcolors.OKGREEN + s + Bcolors.ENDC)


def signal_handler(sig):
    log('Caught ' + str(sig))
    global PLAYER
    log('Exit')
    del PLAYER
    sys.exit(0)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


global display_img
global point1, point2
PLAYER = Player()
PLAYER.connect_device()
DISPLAY_WINDOW = 'screenshot'
EXTENSION = '.png'


def on_mouse(event, x, y, flags, param):
    global display_img, point1, point2
    img2 = display_img.copy()
    if event == cv2.EVENT_LBUTTONDOWN:
        point1 = (x, y)
        cv2.circle(img2, point1, 5, (0, 0, 255), 10)
        cv2.imshow(DISPLAY_WINDOW, img2)
    elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):
        cv2.rectangle(img2, point1, (x, y), (0, 0, 255), 2)
        cv2.imshow(DISPLAY_WINDOW, img2)
    elif event == cv2.EVENT_LBUTTONUP:
        point2 = (x, y)
        cv2.rectangle(img2, point1, point2, (0, 0, 255), 2)
        cv2.imshow(DISPLAY_WINDOW, img2)
        # min_x = min(point1[0], point2[0])
        # min_y = min(point1[1], point2[1])
        # width = abs(point1[0] - point2[0])
        # height = abs(point1[1] -point2[1])
        # cut_img = img[min_y:min_y+height, min_x:min_x+width]
        # cv2.imwrite('lena3.jpg', cut_img)
        # log("请按任意键结束截图")


def grab(save=True):
    global display_img
    img = PLAYER.screenshot()
    display_img = pil2cv(img)
    cv2.namedWindow(DISPLAY_WINDOW, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(DISPLAY_WINDOW, on_mouse)
    cv2.imshow(DISPLAY_WINDOW, display_img)
    cv2.waitKey(0)
    cv2.destroyWindow(DISPLAY_WINDOW)
    # log(point1, point2)
    # get center of the template
    location = ((point1[0] + point2[0])/2, (point1[1] + point2[1])/2)
    # save template
    resolution = PLAYER.viewport
    crop_rectangle = (*point1, *point2)
    cropped_img = img.crop(crop_rectangle)
    log('upper_left {} \nbottom_right {}'.format(point1, point2))
    if save:
        while True:
            path = input('please input the path to save this template\n')
            try:
                save_path = save_template(cropped_img, resolution, location, path, EXTENSION)
            except KeyError:
                log('template name has already exist, do you want to overwrite it?[y/n]')
                ans = None
                while ans not in ['y', 'n']:
                    ans = input()
                if ans == 'y':
                    save_path = save_template(cropped_img, resolution, location, path, EXTENSION, force=True)
                    log('template successfully saved to ' + save_path)
                    break
                else:
                    break
            else:
                log('template successfully saved to ' + save_path)
                break
