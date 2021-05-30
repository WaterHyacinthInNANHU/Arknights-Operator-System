# interact with emulator ( do dirty works for operator :)
# from typing import List
from connector.ADBConnector import ADBConnector, ensure_adb_alive
from random import gauss, uniform
import os
import time
import logging
import coloredlogs
import cv2
import numpy as np
from arknights.resource import load_template, load_position, load_rectangle, RectangleData
from arknights.imgops import pil2cv, compare_mse, scale_pos_to_local_resolution, grayscale
from win32api import ShellExecute
import psutil
from arknights.ocr import *
from arknights.common import singleton, NothingMatched, ClickNoEffect
from util.flags import *
from arknights.ocr.stage_ocr import recognize_all_screen_stage_tags


@singleton
class Player:
    def __init__(self):
        self.adb = None
        self.viewport = None
        self.logger = logging.getLogger('Player')
        coloredlogs.install(
            fmt=' Ξ %(message)s',
            # fmt=' %(asctime)s ! %(funcName)s @ %(filename)s:%(lineno)d ! %(levelname)s # %(message)s',
            datefmt='%H:%M:%S',
            level_styles={'info': {'color': 'green'}, 'error': {'color': 'red'}},
            level='INFO')
        # self.connect_device()
        # self.print_info()

    def _print_info(self):
        self.logger.info('system info:')
        self.logger.info('resolution:\t%dx%d', *self.viewport)
        # logger.info('OCR engine:\t%s', ocr.engine.info)
        self.logger.info('screenshot saving path:\t%s', config.SCREEN_SHOOT_SAVE_PATH)

        if config.enable_baidu_api:
            self.logger.info('%s',
                             """baidu API configurations:
        APP_ID\t{app_id}
        API_KEY\t{api_key}
        SECRET_KEY\t{secret_key}
                        """.format(
                                 app_id=config.APP_ID, api_key=config.API_KEY, secret_key=config.SECRET_KEY
                             )
                             )

    # def __del__(self):
    #     # self.adb.run_device_cmd("am force-stop {}".format(config.ArkNights_PACKAGE_NAME))
    #     pass

    @staticmethod
    def _mkdir(path: str):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            print('mkdir: ' + path)

    @staticmethod
    def _wait(n: float = 10,  # 等待时间中值
              manlike: bool = True):  # 是否在此基础上设偏移量
        if manlike:
            m = uniform(0, 0.3)
            n = uniform(n - m * 0.5 * n, n + m * n)
        time.sleep(n)

    def connect_device(self):
        # # select from multiple devices
        # ensure_adb_alive()
        # try:
        #     self.adb = ADBConnector.auto_connect()
        # except IndexError:
        #     print("detected multiple devices")
        #     devices = ADBConnector.available_devices()
        #     for i, (serial, status) in enumerate(devices):
        #         print("%2d. %s\t[%s]" % (i, serial, status))
        #     while True:
        #         try:
        #             num = int(input("please input number of the device you select: "))
        #             if not 0 <= num < len(devices):
        #                 raise ValueError()
        #             break
        #         except ValueError:
        #             print("invalid input, please try again")
        #     device_name = devices[num][0]
        #     self.adb = ADBConnector(device_name)
        ensure_adb_alive()
        try:
            self.adb = ADBConnector.auto_connect()
        except (IndexError, RuntimeError, EOFError):
            return False
        self.adb.ensure_alive()
        self.viewport = self.adb.screen_size
        self._print_info()
        return True

    def type(self, s: str):
        self.logger.debug("typing string with adb...")
        self.adb.run_device_cmd("input text {}".format(s))

    @staticmethod
    def _is_device_online() -> bool:
        """
        if the main process is running, returns True, otherwise returns False
        the main process is defined at the first entry of device/emulator_progress_names
        :return: bool
        """
        main_process_name = config.get('device/emulator_progress_names')[0]
        for p in psutil.process_iter():
            if p.name() == main_process_name:
                return True
        else:
            return False

    @staticmethod
    def _get_device_pids() -> list:
        """
        return pids of every sub-process define in config-dev.yaml
        :return: a set contains pids
        """
        name_list = config.get('device/emulator_progress_names')
        pids = set()
        for p in psutil.process_iter():
            # print(p.name())
            if p.name() in name_list:
                pids.add(p.pid)
        return list(pids)

    @staticmethod
    def _terminate_by_pids(pids: int or list):
        if not isinstance(pids, list):
            pids = [pids]
        for pid in pids:
            p = psutil.Process(pid)
            p.terminate()

    def _kill_all_device_processes(self):
        pids = self._get_device_pids()
        self._terminate_by_pids(pids)

    def ensure_device_launched(self):
        self.logger.debug("triggering emulator to start...")
        if self._is_device_online():
            self.logger.debug("emulator has already been launched")
        else:
            self._kill_all_device_processes()
            self._wait(2)
            ShellExecute(0, 'open', config.get('device/emulator_launcher'), '', '', 1)
            for _ in range(30):
                if self._is_device_online():
                    break
                self._wait(1, manlike=False)
            else:
                raise TimeoutError('time out launching emulator')
            self.logger.debug("emulator has launched")

    def ensure_device_closed(self):
        self.logger.debug("closing emulator...")
        if not self._is_device_online():
            self.logger.debug("emulator is not running")
        else:
            self._kill_all_device_processes()
            for _ in range(30):
                if not self._is_device_online():
                    break
                self._wait(1, manlike=False)
            else:
                raise TimeoutError('time out closing emulator')
            self.logger.debug("emulator is closed")

    def ensure_game_launched(self):
        self.logger.debug('launching game...')
        package_name = config.get('device/package_name')
        activity_name = config.get('device/activity_name')
        if self._is_game_running():
            self.logger.debug('game has already launched')
            return
        else:
            self.adb.run_device_cmd(
                "am start -n {}/{}".format(package_name, activity_name))
            for _ in range(30):
                if not self._is_game_running():
                    self._wait(1, manlike=False)
                else:
                    break
            else:
                raise TimeoutError('time out launching game')

    def _is_game_running(self):
        current = self.adb.run_device_cmd('dumpsys window windows | grep mCurrentFocus').decode(errors='ignore')
        self.logger.debug(current)
        package_name = config.get('device/package_name')
        if package_name in current:
            return True
        else:
            return False

    def screenshot(self, rect: RectangleData = None) -> Image:
        if rect is None:
            screenshot = self.adb.screenshot()
        else:
            screenshot = self.adb.screenshot().crop(*rect.upper_left, *rect.bottom_right)
        return screenshot

    def click_rect(self, ul_x: int, ul_y: int, dr_x: int, dr_y: int):
        hwidth = (dr_x - ul_x) / 2
        hheight = (dr_y - ul_y) / 2
        midx = ul_x + hwidth
        midy = ul_y + hheight
        xdiff = max(-1, min(1, gauss(0, 0.2)))
        ydiff = max(-1, min(1, gauss(0, 0.2)))
        tapx = int(midx + xdiff * hwidth)
        tapy = int(midy + ydiff * hheight)
        self.adb.touch_tap((tapx, tapy))
        self._wait(TINY_WAIT, manlike=True)

    def click_pos(self, tapx: int, tapy: int):
        self.adb.touch_tap((tapx, tapy))
        self._wait(TINY_WAIT, manlike=True)

    def _scale_pos_to_local_resolution(self, target_resolution: tuple, pos: tuple or list):
        return scale_pos_to_local_resolution(self.viewport, target_resolution, pos)

    def click_position(self, _path_: str):
        position = load_position(_path_)
        scaled_pos = self._scale_pos_to_local_resolution(position.resolution, position.position)
        self.click_pos(*scaled_pos)

    @staticmethod
    def _match_template(template: Image, target: Image, threshold) -> tuple:
        w, h = template.size
        template = pil2cv(template)
        target = pil2cv(target)
        # match
        method = getattr(cv2, config.get('resource/matching/method', 'TM_CCOEFF_NORMED'))
        res = cv2.matchTemplate(target, template, method)
        loc = np.where(res >= threshold)
        # raise if no template is matched
        if len(loc[0]) == 0:
            raise NothingMatched('length of loc is 0, nothing matched')
        # get location if successfully matched
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            upper_left = min_loc
        else:
            upper_left = max_loc
        bottom_right = (upper_left[0] + w, upper_left[1] + h)
        # debug
        # display = target.copy()
        # cv2.namedWindow('temp', cv2.WINDOW_NORMAL)
        # cv2.rectangle(display, upper_left, bottom_right, (0, 0, 255), 5)
        # cv2.imshow('temp', display)
        # cv2.waitKey(0)
        return upper_left, bottom_right

    def locate_template(self, _path_: str) -> tuple:
        # load template
        template = load_template(_path_)
        # screenshot and resize it
        screenshot = self.screenshot()
        resized_screenshot = screenshot.resize(template.resolution)
        # match
        threshold = config.get('resource/matching/threshold', 0.8)
        upper_left, bottom_right = self._match_template(template.image, resized_screenshot, threshold)
        # transform upper_left, bottom_right back to original resolution
        upper_left = self._scale_pos_to_local_resolution(template.resolution, upper_left)
        bottom_right = self._scale_pos_to_local_resolution(template.resolution, bottom_right)
        # # debug
        # display = pil2cv(screenshot.copy())
        # cv2.namedWindow('temp', cv2.WINDOW_AUTOSIZE)
        # cv2.rectangle(display, upper_left, bottom_right, (0, 0, 255), 5)
        # cv2.imshow('temp', display)
        # cv2.waitKey(0)
        return upper_left, bottom_right

    def click_template(self, _path_: str, check_diff: bool = False):
        location = self.locate_template(_path_)
        self.click_rect(*location[0], *location[1])
        if check_diff:
            self._wait(2, manlike=False)
            template = load_template(_path_)
            upper_left = self._scale_pos_to_local_resolution(template.resolution, template.upper_left)
            bottom_right = self._scale_pos_to_local_resolution(template.resolution, template.bottom_right)
            cropped_screen = self.screenshot().crop((*upper_left, *bottom_right))
            diff = compare_mse(template.image, cropped_screen)
            if diff < 255 ** 2 * 0.8:
                raise ClickNoEffect

    def ocr_screenshot_by_rect(self, _path_: str, lang: str = 'zh') -> OcrResult:
        screenshot = self.screenshot()
        rectangle = load_rectangle(_path_)
        if rectangle is not None:
            upper_left = self._scale_pos_to_local_resolution(rectangle.resolution, rectangle.upper_left)
            bottom_right = self._scale_pos_to_local_resolution(rectangle.resolution, rectangle.bottom_right)
            screenshot = screenshot.crop((*upper_left, *bottom_right))
        ocr_engine = OCREngine(lang)
        res = ocr_engine.recognize(screenshot)
        if res.text == '':
            raise NothingRecognized
        del ocr_engine
        return res

    def wait_until_screen_stable(self, max_check: int, check_interval: float, threshold: float, rect: str = None):
        """
        wait until screen in the rect is stable
        :return:
        """
        def _get_screenshot():
            if rect is None:
                screen = self.screenshot()
            else:
                rectangle = load_rectangle(rect)
                screen = self.screenshot(rectangle)
            return grayscale(screen)

        screen_pre = _get_screenshot()
        self._wait(check_interval, manlike=False)
        for _ in range(max_check - 1):
            screen_now = _get_screenshot()
            diff = compare_mse(screen_now, screen_pre)
            # print(diff)
            if diff < 255 ** 2 * threshold:
                break
            screen_pre = screen_now.copy()
            self._wait(check_interval, manlike=False)
        else:
            raise TimeoutError('time out waiting for screen to be stable')

    def drag(self, origin: tuple, movement: tuple, duration_s: float = None):
        """
        drag
        :param origin:(x, y) normalized start position
        :param movement:(x, y): normalize drag distance in x, y direction
        :param duration_s: duration in s
        :return:
        """
        origin = (origin[0]*self.viewport[0], origin[1]*self.viewport[1])
        movement = (movement[0]*self.viewport[0], movement[1]*self.viewport[1])
        duration_ms = (duration_s * 1000)
        self.adb.touch_swipe2(origin, movement, duration_ms)

    def stage_ocr(self):
        screenshot = self.screenshot()
        res = recognize_all_screen_stage_tags(screenshot)
        return res

