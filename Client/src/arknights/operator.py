from typing import List
import config
from .player import Player
from arknights.common import NothingMatched, UnknownInterface, InvalidInitialInterface, NoSufficientSanity
from arknights.ocr.common import OcrResult, NothingRecognized
from arknights.resource import is_template_exist
import logging
import time

NORMAL_OPERATION = 0
ANNIHILATION_OPERATION = 1


def _collect_warning_info(expectation):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            try:
                result = function(self, *args, **kwargs)
            except expectation as e:
                self.logger.debug('trying to collecting error information...'.format(e))
                try:
                    warning_info = self._get_warning_message_by_ocr()
                except NothingRecognized:
                    self.logger.debug('ocr failed, unknown error'.format(e))
                    self.logger.error('unknown error')
                else:
                    self.logger.error('warning info: {}'.format(warning_info))
                raise
            return result

        return wrapper

    return decorator


class Operator(object):
    def __init__(self, logger=None):
        self.player = Player()
        if logger is None:
            self.logger = logging.getLogger('Operator')
        else:
            self.logger = logger

    def _wait(self, secs: float, mute=False):
        if not mute:
            self.logger.debug('waiting for {} seconds...'.format(secs))
        time.sleep(secs)

    def _type(self, s: str):
        self.logger.debug('typing {}'.format(s))
        self.player.type(s)

    def _wait_for_template(self, _path_: List[str] or str, max_retry: int, retry_interval: float):
        self.logger.debug('waiting for template {}...'.format(_path_))
        assert max_retry >= 0
        assert retry_interval >= 0
        if isinstance(_path_, str):
            _path_ = [_path_]
        for _ in range(max_retry):
            for p in _path_:
                try:
                    self.player.locate_template(p)
                except NothingMatched:
                    pass
                else:
                    return p
            self._wait(retry_interval, mute=True)
        else:
            raise TimeoutError('time out waiting for template {}'.format(_path_))

    def _wait_until_template_disappears(self, _path_: str, max_retry: int, retry_interval: float):
        self.logger.debug('waiting for template {} to disappear...'.format(_path_))
        assert max_retry >= 0
        assert retry_interval >= 0
        for _ in range(max_retry):
            try:
                self.player.locate_template(_path_)
            except NothingMatched:
                return
            else:
                self._wait(retry_interval, mute=True)
                continue
        else:
            raise TimeoutError('time out waiting for template {} to disappear'.format(_path_))

    def _wait_until_screen_stable(self, max_check: int, check_interval: float,
                                  threshold: float = 0.01, rect: str = None):
        self.logger.debug('waiting for screen to be stable')
        self.player.wait_until_screen_stable(max_check, check_interval, threshold, rect)

    def _wait_on_networking(self, max_retry: int, retry_interval: float):
        self.logger.debug('waiting for networking...')
        assert max_retry >= 0
        assert retry_interval >= 0
        for _ in range(max_retry):
            try:
                ocr_result = self.player.ocr_screenshot_by_rect('common/networking_message', lang='zh')
            except NothingRecognized:
                return
            else:
                self.logger.debug('networking ocr detected: {}...'.format(ocr_result.text))
                if ('正在' in ocr_result.text) or \
                        ('反馈' in ocr_result.text) or \
                        ('神经' in ocr_result.text):
                    self._wait(retry_interval, mute=True)
                else:
                    return
        else:
            raise TimeoutError('time out waiting on networking')

    def _is_template_on_screen(self, _path_: str) -> bool:
        self.logger.debug('checking existence of template {}'.format(_path_))
        try:
            self.player.locate_template(_path_)
        except NothingMatched:
            return False
        else:
            return True

    def _drag(self, origin: tuple, movement: tuple, duration_s: float = None):
        assert duration_s > 0
        self.player.drag(origin, movement, duration_s)

    def _drag_until_template_appears(self, _path_: str, origin: tuple, movement: tuple, duration_s: float,
                                     max_retry: int, retry_interval: float):
        assert max_retry >= 0
        assert retry_interval >= 0
        for _ in range(max_retry):
            if self._is_template_on_screen(_path_):
                self._wait_until_screen_stable(5, 1)
                return
            else:
                self._drag(origin, movement, duration_s)
                self._wait(retry_interval, mute=True)
                continue
        else:
            raise TimeoutError('time out dragging for template'.format(_path_))

    def _click_template(self, _path_: str):
        self.logger.debug('clicking template {}'.format(_path_))
        self.player.click_template(_path_)

    def _wait_and_click_template(self, _path_: str, max_retry: int, retry_interval: float):
        self._wait_for_template(_path_, max_retry, retry_interval)
        self._click_template(_path_)

    def _click_template_until_target_appears(self, _path_temp: str, _path_target: str,
                                             max_retry: int, retry_interval: float):
        assert max_retry >= 0
        assert retry_interval >= 0
        # location = self.player.locate_template(_path_temp)
        for _ in range(max_retry):
            if self._is_template_on_screen(_path_target):
                return
            else:
                # self.player.click_rect(*location[0], *location[1])
                self._click_template(_path_temp)
                self._wait(retry_interval, mute=True)
                continue
        else:
            raise TimeoutError('time out waiting for template'.format(_path_target))

    def _click_pos(self, *args):
        if len(args) == 1:
            _path_ = args[0]
            self.logger.debug('clicking pos {}'.format(_path_))
            self.player.click_position(_path_)
        elif len(args) == 2:
            self.player.click_pos(args[0], args[1])
        else:
            raise ValueError('Invalid parameter number')

    def _get_warning_message_by_ocr(self) -> OcrResult:
        self.logger.debug('getting message from warning dialog...')
        res = self.player.ocr_screenshot_by_rect('common/warning_info', lang='zh')
        self.logger.debug('ocr result: {}'.format(res.text))
        return res

    def _wait_and_connect_emulator(self, max_retry: int, retry_interval: float):
        self.logger.debug('waiting for emulator to be ready...')
        assert max_retry >= 0
        assert retry_interval >= 0
        for _ in range(max_retry):
            if self.player.connect_device():
                self.logger.debug('emulator is ready')
                return
            else:
                self._wait(retry_interval, mute=True)
                continue
        else:
            raise TimeoutError('time out waiting for emulator to be ready')

    def launch_and_connect_emulator(self):
        self.logger.debug('launching emulator...')
        self.player.ensure_device_launched()
        self._wait_and_connect_emulator(max_retry=30, retry_interval=10)
        self.logger.debug('connected to emulator')

    @_collect_warning_info(TimeoutError)
    def launch_game(self):
        self.logger.debug('launching game...')
        self.player.ensure_game_launched()
        # TODO: handle game update
        self._wait_for_template('login/start', max_retry=20, retry_interval=3)
        self.logger.debug('game launched')

    def close_emulator(self):
        self.logger.debug('closing emulator...')
        self.player.ensure_device_closed()

    @_collect_warning_info(TimeoutError)
    def login(self, force_re_login: bool = False):  # 初始界面为：start icon
        def _re_login():
            self.logger.debug('start to re-login')
            if not self._is_template_on_screen('login/账号登陆'):
                raise InvalidInitialInterface
            else:
                self._wait_and_click_template('login/账号登陆', max_retry=10, retry_interval=1)
                self._wait_for_template('login/登录按钮', max_retry=10, retry_interval=1)
                self._click_pos('login/账号')
                self._wait(1.5)
                self._type(str(config.get('user/account')))
                self._click_pos('login/确认输入')
                self._wait(1.5)
                self._click_pos('login/密码')
                self._wait(1.5)
                self._type(str(config.get('user/password')))
                self._wait(1.5)
                self._click_pos('login/确认输入')
                self._wait(1.5)
                self._click_template('login/登录按钮')

        def _wait_for_main_panel(max_retry: int, retry_interval: float):
            self.logger.debug('waiting for main panel')
            for _ in range(max_retry):
                if self._is_template_on_screen('login/main_panel'):
                    self._wait(5)
                    if self._is_template_on_screen('login/main_panel'):
                        break
                if self._is_template_on_screen('login/close_announcement'):
                    self.logger.debug('close announcement')
                    self._click_template('login/close_announcement')
                if self._is_template_on_screen('login/今日配给'):
                    self.logger.debug('confirm 今日配给')
                    self._click_pos('login/confirm_今日配给')
                self._wait(retry_interval, mute=True)
            else:
                raise TimeoutError('timeout waiting for main_panel')

        # workflow
        self.logger.debug('start logging in...')
        """"""
        if not self._is_template_on_screen('login/start'):
            raise InvalidInitialInterface
        else:
            self._click_template('login/start')
            self._wait_for_template('login/登录界面', max_retry=30, retry_interval=2)
            self._wait(2)
            self._wait_on_networking(max_retry=30, retry_interval=2)

            if not force_re_login:
                if not self._is_template_on_screen('login/开始唤醒'):
                    if not self._is_template_on_screen('login/账号登陆'):
                        raise UnknownInterface
                    else:
                        _re_login()
                else:
                    self._click_template('login/开始唤醒')
                    self._wait(2)
                    self._wait_on_networking(15, 2)
                    self._wait(2)
                    if self._is_template_on_screen('login/记忆已经模糊'):
                        self._click_template('login/warning')
                        self._wait(2)
                        _re_login()
            else:
                if self._is_template_on_screen('login/账号管理'):
                    self._click_template('login/账号管理')
                    self._wait_until_screen_stable(max_check=5, check_interval=1)
                _re_login()

            self.logger.debug('waiting until main panel is loaded')
            _wait_for_main_panel(max_retry=90, retry_interval=2)
            """"""
            self.logger.debug('successfully logged in')

    def _get_checkpoints(self):
        res = self.player.stage_ocr()
        return res

    @_collect_warning_info(TimeoutError)
    def navigate_to_main_panel(self):
        self.logger.debug('returning to main panel...')
        if not self._is_template_on_screen('navigate/main_panel/main_panel_loaded_flag'):
            if not self._is_template_on_screen('navigate/main_panel/back_to_main_button'):
                raise InvalidInitialInterface
            self._wait_and_click_template('navigate/main_panel/back_to_main_button', max_retry=10, retry_interval=1)
            self._wait_and_click_template('navigate/main_panel/back_to_main_button_首页', max_retry=10, retry_interval=1)
            self._wait_for_template('navigate/main_panel/main_panel_loaded_flag', max_retry=10, retry_interval=1)
        self._wait(2)
        self._wait_on_networking(max_retry=20, retry_interval=3)
        self.logger.debug('navigated to main panel')

    @_collect_warning_info(TimeoutError)
    def navigate_to_control_panel(self):
        self.logger.debug('navigating to control panel...')
        if not self._is_template_on_screen('navigate/control_panel/终端'):
            raise InvalidInitialInterface
        else:
            self._click_template('navigate/control_panel/终端')
            self._wait_for_template('navigate/control_panel/control_panel_loaded_flag', max_retry=10, retry_interval=1)
            self._wait_until_screen_stable(max_check=5, check_interval=1)
        self.logger.debug('navigated to control panel')

    @_collect_warning_info(TimeoutError)
    def navigate_to_default_annihilation(self):
        self.logger.debug('navigating to annihilation operation panel...')
        if not self._is_template_on_screen('navigate/common/main_panel_loaded_flag'):
            raise InvalidInitialInterface
        else:
            self.navigate_to_control_panel()
            self._click_pos('navigate/annihilation/每周部署')
            self._wait_for_template('navigate/annihilation/annihilation_panel_loaded_flag',
                                    max_retry=10, retry_interval=1)
            self._click_pos('navigate/annihilation/default_annihilation')
            self._wait_for_template('navigate/annihilation/annihilation_operation_loaded_flag', max_retry=10,
                                    retry_interval=1)
            self.logger.debug('navigated to default_annihilation')

    @_collect_warning_info(TimeoutError)
    def navigate_to_resources(self, resource: str, checkpoint: str):
        self.logger.debug('navigating to {}:{}...'.format(resource, checkpoint))
        resource_path = 'navigate/resources/{}'.format(resource)
        if not is_template_exist(resource_path):
            raise ValueError('invalid resource type')
        if not self._is_template_on_screen('navigate/common/main_panel_loaded_flag'):
            raise InvalidInitialInterface
        else:
            self.navigate_to_control_panel()
            self._click_pos('navigate/resources/资源收集')
            try:
                self._drag_until_template_appears(resource_path, (0.5, 0.5), (-0.2, 0), 1,
                                                  max_retry=5, retry_interval=1)
            except TimeoutError:
                try:
                    self._drag_until_template_appears(resource_path, (0.5, 0.5), (0.2, 0), 1,
                                                      max_retry=5, retry_interval=1)
                except TimeoutError:
                    self.logger.debug('resource is not currently available')
                    return
            self._click_template(resource_path)
            self._wait_until_screen_stable(max_check=5, check_interval=1)
            # find click checkpoint
            res = self._get_checkpoints()
            if len(res) == 0:
                self.logger.debug('failed to recognize any checkpoint')
            if checkpoint not in res:
                self.logger.debug('checkpoint not found')
                return
            else:
                location = res[checkpoint]
                self._click_pos(*location)
                self._wait_until_screen_stable(max_check=5, check_interval=1)
            self.logger.debug('navigated to {}:{}'.format(resource, checkpoint))

    @_collect_warning_info(TimeoutError)
    def navigate_to_storyline(self):
        pass

    @_collect_warning_info(TimeoutError)
    def operate(self, mode: int = NORMAL_OPERATION, auto_refill: bool = False):
        def _start_operation():
            if not self._is_template_on_screen('operation/common/开始行动'):
                raise InvalidInitialInterface
            else:
                self.logger.debug('start operation...')
                if self._is_template_on_screen('operation/common/代理指挥_off'):
                    self._click_template('operation/common/代理指挥_off')
                    self._wait_for_template('operation/common/代理指挥_on', max_retry=5, retry_interval=1)
                self._click_template('operation/common/开始行动')
                self._wait(1)
                self._wait_on_networking(max_retry=30, retry_interval=2)
                self._wait_until_screen_stable(max_check=5, check_interval=2)
                if self._is_template_on_screen('operation/common/sanity_not_sufficient_flag'):
                    self.logger.debug('sanity is not sufficient!')
                    if auto_refill:
                        self.logger.debug('refilling sanity...')
                        raise NotImplemented    # TODO
                        # self.logger.debug('sanity is refilled')
                    else:
                        if self._is_template_on_screen('operation/common/restore_sanity_cancel'):
                            self._click_template('operation/common/restore_sanity_cancel')
                            self._wait_until_screen_stable(max_check=5, check_interval=1)
                            raise NoSufficientSanity
                        else:
                            raise UnknownInterface
                self._wait_and_click_template('operation/common/_开始行动', max_retry=10, retry_interval=1)
                self._wait(1)
                self._wait_on_networking(max_retry=20, retry_interval=3)

        def _handle_warning_info():
            if self._is_template_on_screen('operation/common/error_flag'):
                self.logger.debug('error occurred, trying to collecting error information...')
                try:
                    warning_info = self._get_warning_message_by_ocr()
                except NothingRecognized:
                    self.logger.debug('ocr failed, unknown error')
                    self.logger.error('unknown error')
                else:
                    if '是否重试' in warning_info.text:
                        self._click_template('operation/common/error_confirm')
                        self._wait_on_networking(max_retry=20, retry_interval=3)
                    else:
                        self.logger.error('warning info: {}'.format(warning_info))
                        raise RuntimeError('unhandled error during operation: {}'.format(warning_info))

        def _on_normal_operation(max_retry: int, retry_interval: float):
            self.logger.debug('on operation...')
            assert max_retry >= 0
            assert retry_interval >= 0
            for _ in range(max_retry):
                _handle_warning_info()
                if self._is_template_on_screen('operation/common/operation_finished_flag'):
                    self._wait(1)
                    self._wait_until_screen_stable(max_check=15, check_interval=1)
                    self._click_template('operation/common/operation_finished_flag')
                    self._wait_for_template('operation/common/开始行动', max_retry=10, retry_interval=1)
                    self._wait_until_screen_stable(max_check=15, check_interval=1)
                    self.logger.debug('operation finished')
                    return
                else:
                    self._wait(retry_interval, mute=True)
                    continue
            else:
                raise TimeoutError('time out on operation')

        def _on_annihilation(max_retry: int, retry_interval: float):
            self.logger.debug('on annihilation...')
            assert max_retry >= 0
            assert retry_interval >= 0
            for _ in range(max_retry):
                _handle_warning_info()
                if self._is_template_on_screen('operation/annihilation/作战简报'):
                    self._click_template('operation/annihilation/作战简报')
                    self._wait_for_template('operation/annihilation/operation_finished_flag', max_retry=5,
                                            retry_interval=1)
                if self._is_template_on_screen('operation/annihilation/operation_finished_flag'):
                    self._wait(1)
                    self._wait_until_screen_stable(max_check=15, check_interval=1)
                    self._click_template('operation/annihilation/operation_finished_flag')
                    self._wait_for_template('operation/annihilation/开始行动', max_retry=10, retry_interval=1)
                    self._wait_until_screen_stable(max_check=15, check_interval=1)
                    self.logger.debug('operation finished')
                    self.logger.debug('annihilation finished')
                    return
                else:
                    self._wait(retry_interval, mute=True)
                    continue
            else:
                raise TimeoutError('time out on annihilation')

        # workflow
        self.logger.debug('on operation...')
        try:
            _start_operation()
        except NoSufficientSanity:
            self.logger.debug('no sufficient sanity, return')
            return
        if mode is ANNIHILATION_OPERATION:
            _on_annihilation(max_retry=180, retry_interval=10)
        elif mode is NORMAL_OPERATION:
            _on_normal_operation(max_retry=240, retry_interval=5)
        self.logger.debug('operation finished')

    @_collect_warning_info(TimeoutError)
    def receive_rewards(self, max_try=50):
        def _receive_rewards():
            for _ in range(max_try):
                self._wait_until_screen_stable(max_check=10, check_interval=1)
                if self._is_template_on_screen('reward/报酬已领取'):
                    break
                if self._is_template_on_screen('reward/点击领取'):
                    self._click_template('reward/点击领取')
                    self._wait_on_networking(max_retry=10, retry_interval=1)
                    continue
                else:
                    if self._is_template_on_screen('reward/reward_panel_loaded_flag'):
                        break
                if self._is_template_on_screen('reward/获得物资'):
                    self._click_template('reward/获得物资')
                    continue
            else:
                raise TimeoutError('time out receiving awards')

        self.logger.debug('receiving rewards...')
        if not self._is_template_on_screen('navigate/main_panel/main_panel_loaded_flag'):
            raise InvalidInitialInterface
        self._click_template('reward/任务')
        self._wait_until_screen_stable(max_check=5, check_interval=1)
        # 日常任务
        self._click_pos('reward/日常任务')
        self._wait_until_screen_stable(max_check=5, check_interval=1)
        _receive_rewards()
        self.logger.debug('received 日常任务')
        # 周常任务
        self._click_pos('reward/周常任务')
        self._wait_until_screen_stable(max_check=5, check_interval=1)
        _receive_rewards()
        self.logger.debug('received 周常任务')
        self.logger.debug('rewards received')

    # def get_icon(self, name, confidence=0.9):
    #     path = None
    #     for d in self.imgdirs:
    #         if os.path.exists(d + name + '.jpg'):
    #             path = d + name + '.jpg'
    #             break
    #     if path is None:
    #         raise ArknightsException('can not find resource: ' + name)
    #     else:
    #         return auto.locateCenterOnScreen(path, grayscale=False, confidence=confidence)
    #
    # def click(self, pos):
    #     auto.click(pos.x, pos.y)
    #     self.delay(1.5)
    #
    # @staticmethod
    # def type_string(s):
    #     for char in s:
    #         auto.keyDown(char)
    #         auto.keyUp(char)
    #
    # @staticmethod
    # def type(key):
    #     auto.keyDown(key)
    #     auto.keyUp(key)
    #
    # @staticmethod
    # def screen_shot():
    #     loc = r"output\\screenshot\\screenshot.jpg"
    #     auto.screenshot().save(loc)
    #
    # def drag(self, xstart=1020, ystart=160, xdistance=0, ydistance=0, speed=250):
    #     auto.moveTo(xstart, ystart)  # move mouse to the start position
    #     auto.dragTo(xstart + xdistance, ystart + ydistance, button='left',
    #                 duration=pow(pow(xdistance, 2) + pow(ydistance, 2), 0.5) / speed)  # drag
    #     auto.click(xstart + xdistance, ystart + ydistance)
    #     self.delay(0.5)
    #
    # def click_icon(self, icon, target=None, timeout_for_icon=10, timeout_for_target=10, is_raise_error=True):
    #     self.logger.info("name:" + str(icon) + " target_name:" + str(target) + '\n')
    #     cnt = 0
    #     while True:
    #         cnt += 1
    #         self.focus()
    #         pos = self.get_icon(icon)
    #         if pos is not None:
    #             break
    #         self.delay(1)
    #         if cnt >= timeout_for_icon:
    #             self.logger.info("can't find : " + icon)
    #             if is_raise_error:
    #                 raise ArknightsException("can't find tag:" + icon)
    #             return
    #     cnt = 0
    #     while True:
    #         cnt += 1
    #         self.focus()
    #         self.click(pos)
    #         self.delay(1)
    #         if target is None:
    #             break
    #         elif target == icon:
    #             if self.get_icon(icon) is None:
    #                 break
    #         else:
    #             if self.get_icon(target) is not None:
    #                 break
    #         if cnt >= timeout_for_target:
    #             self.logger.info("no reaction by pressing : " + icon)
    #             if is_raise_error:
    #                 raise ArknightsException("can't find tag:" + target)
    #             return
    #     return
    #
    # def back_to_menu(self):
    #     self.focus()
    #     if self.get_icon("maximizemumu") is not None:
    #         self.click_icon("maximizemumu", "maximizemumu")
    #     if self.get_icon("zuozhan") is None:
    #         self.click_icon("navigator", "navigator_shouye")
    #         self.click_icon("navigator_shouye", "navigator_shouye")
    #
    # def find_icon(self, level, max_drag=20, start_from='left'):
    #     cnt = 0
    #     while True:
    #         if cnt >= max_drag:
    #             break
    #         cnt += 1
    #         if self.get_icon(level) is None:
    #             if start_from == 'left':
    #                 self.drag(xdistance=-500, speed=500)
    #             else:
    #                 self.drag(xdistance=500, speed=500)
    #         else:
    #             break
    #     if cnt >= max_drag:
    #         cnt = 0
    #         while True:
    #             if cnt >= max_drag:
    #                 return
    #             cnt += 1
    #             if self.get_icon(level) is None:
    #                 if start_from == 'left':
    #                     self.drag(xdistance=500, speed=500)
    #                 else:
    #                     self.drag(xdistance=-500, speed=500)
    #             else:
    #                 break
    #
    # def wait_for_mission(self, scan_interval):
    #     self.logger.info("running", end='')
    #     while True:
    #         self.logger.info(".", end=' ')
    #         self.delay(scan_interval)
    #         self.focus(throw_exception=True)
    #         if self.get_icon("xingdongjieshu") is not None:
    #             self.click_icon("xingdongjieshu", "xingdongjieshu")
    #             return True
    #         if self.get_icon("dengjitisheng") is not None:
    #             self.click_icon("dengjitisheng", "dengjitisheng")
    #             self.click_icon("xingdongjieshu", "xingdongjieshu")
    #             return True
    #         if self.get_icon("zuozhanjianbao") is not None:
    #             self.click_icon("zoophobia", "zuozhanjianbao")
    #             self.click_icon("meizhoubaochoujindu", "meizhoubaochoujindu")
    #             return True
    #         if self.get_icon("fangqixingdong") is not None:
    #             self.click_icon("fangqixingdong", "fangqixingdong")
    #             self.click_icon("renwushibai", "renwushibai")
    #             return False
    #         if self.get_icon("reconnect") is not None:
    #             self.click_icon("reconnect")
    #             return False
    #
    # def set_as_foreground(self, hwnd):
    #     self.shell.SendKeys('%')
    #     win32gui.SetForegroundWindow(hwnd)
    #
    # def focus(self, throw_exception=False):
    #     hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    #     if hwnd == 0:
    #         hwnd = win32gui.FindWindow(None, "MuMu模拟器")
    #     if hwnd == 0:
    #         if throw_exception:
    #             raise ArknightsException("Mumu has crashed")
    #         return False
    #     self.set_as_foreground(hwnd)
    #     return True
    #
    # def exit_mumu(self):
    #     try:
    #         self.focus()
    #         cnt = 0
    #         self.back_to_menu()
    #         self.click_icon("renwu", "renwu")
    #         while cnt < 20:
    #             self.delay(0.5)
    #             if self.get_icon('baochouyilingqu') is not None:
    #                 break
    #             if self.get_icon('dianjilingqu') is not None:
    #                 self.click_icon('dianjilingqu', 'dianjilingqu')
    #                 self.click_icon('confirm', 'confirm', timeout_for_icon=10, is_raise_error=False)
    #                 cnt = 0
    #             else:
    #                 cnt += 1
    #     except Exception:
    #         self.logger.info(traceback.format_exc())
    #     hwnd = win32gui.FindWindow(None, "明日方舟 - MuMu模拟器")
    #     if hwnd == 0:
    #         hwnd = win32gui.FindWindow(None, "MuMu模拟器")
    #     if hwnd == 0:
    #         self.logger.info("can't find Mumu window")
    #         return
    #     else:
    #         win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    #         self.click_icon("exitmumu_confirm", "exitmumu_confirm")
    #
    # def init_mumu(self):
    #     errormsg = "error happened while starting Mumu"
    #     if win32gui.FindWindow(None, "MuMu模拟器") == 0:
    #         win32api.ShellExecute(0, 'open', self.path, '', '', 1)
    #         while self.focus() is False:
    #             self.delay(1)
    #         self.logger.info("waiting for mumu being ready", end="")
    #     cnt = 0
    #     while True:
    #         if cnt >= 120:
    #             self.logger.info(errormsg)
    #             raise ArknightsException(errormsg)
    #         cnt += 1
    #         self.logger.info(".", end="")
    #         if self.get_icon("maximizemumu") is not None:
    #             self.click_icon("maximizemumu", "maximizemumu", timeout_for_target=120)
    #             break
    #         if self.get_icon("minimizemumu") is not None:
    #             break
    #     self.logger.info("start operating")
    #     cnt = 0
    #     while True:
    #         if cnt >= 120:
    #             self.logger.info(errormsg)
    #             raise ArknightsException(errormsg)
    #         cnt += 1
    #         if self.get_icon("close_advertisement"):
    #             self.click_icon("close_advertisement", "close_advertisement")
    #         if self.get_icon("arknight_launcher"):
    #             self.click_icon("arknight_launcher", "arknight_launcher")
    #             break
    #     self.click_icon("login_start", "login_start", timeout_for_icon=120)
    #     cnt = 0
    #     while True:
    #         if cnt >= 120:
    #             self.logger.info(errormsg)
    #             raise ArknightsException(errormsg)
    #         cnt += 1
    #         if self.get_icon("zhanghaoguanli") is not None:
    #             self.click_icon('zhanghaoguanli', 'zhanghaoguanli')
    #         if self.get_icon("login_zhanghaodenglu") is not None:
    #             self.click_icon("login_zhanghaodenglu", "login_zhanghaodenglu")
    #             auto.click(1043, 602)  # click account bar
    #             self.delay(2)
    #             self.type('backspace')  # clear account
    #             self.type_string(self.account)
    #             self.type('enter')  # confirm
    #             self.click_icon("login_focuspassword")
    #             self.delay(2)
    #             self.type_string(self.password)
    #             self.type('enter')  # confirm
    #             self.click_icon("login_denglu", "login_denglu", timeout_for_target=60)
    #             break
    #     cnt = 0
    #     while True:
    #         if cnt >= 180:
    #             self.logger.info(errormsg)
    #             raise ArknightsException(errormsg)
    #         cnt += 1
    #         if self.get_icon("zuozhan") is not None:
    #             self.delay(3)
    #             if self.get_icon("zuozhan") is not None:
    #                 break
    #         if self.get_icon("close_message") is not None:
    #             self.click_icon("close_message", is_raise_error=False)
    #         if self.get_icon("confirm") is not None:
    #             self.click_icon("confirm", is_raise_error=False)
    #     self.logger.info("login successfully")
    #
    # def zhuxian(self, part, level, times):
    #     self.focus()
    #     self.back_to_menu()
    #     self.click_icon("zuozhan", "zhuxian")
    #     self.click_icon("zhuxian")
    #     self.find_icon(part, start_from='right')
    #     self.click_icon(part)
    #     self.find_icon(level)
    #     cnt = 0
    #     while True:
    #         cnt += 1
    #         self.click_icon(level, "kaishixingdong")
    #         if self.get_icon("dailizhihui_ON") is None:
    #             self.click_icon("dailizhihui_OFF", "dailizhihui_ON")
    #         self.click_icon("kaishixingdong")
    #         if self.get_icon("lizhihaojin") is not None:
    #             self.click_icon("lizhihaojin", "lizhihaojin")
    #             self.logger.info("run out of itellect")
    #             return
    #         self.click_icon("kaishixingdong_1", "kaishixingdong_1")
    #         self.logger.info("round " + str(cnt) + " begins")
    #         if self.wait_for_mission(5) is True:
    #             self.logger.info("round " + str(cnt) + " finished")
    #         else:
    #             self.logger.info("mission failed, try again")
    #             cnt -= 1
    #         if cnt >= times:
    #             self.logger.info("mission complete")
    #             return
    #         else:
    #             self.click_icon("back")
    #
    # def wuzichoubei(self, part, level, times):
    #     self.focus()
    #     cnt = 0
    #     self.back_to_menu()
    #     self.click_icon("zuozhan", "wuzichoubei")
    #     self.click_icon("wuzichoubei")
    #     self.delay(2)
    #     while self.get_icon(part) is None:
    #         if cnt > 5:
    #             self.logger.info("the part is not open today")
    #             return
    #         self.drag(xdistance=-500, speed=500)
    #         cnt += 1
    #     cnt = 0
    #     self.click_icon(part, level)
    #     while True:
    #         cnt += 1
    #         self.click_icon(level, "kaishixingdong")
    #         if self.get_icon("dailizhihui_ON") is None:
    #             self.click_icon("dailizhihui_OFF", "dailizhihui_ON")
    #         self.click_icon("kaishixingdong")
    #         if self.get_icon("lizhihaojin") is not None:
    #             self.click_icon("lizhihaojin", "lizhihaojin")
    #             self.logger.info("run out of itellect")
    #             return
    #         self.click_icon("kaishixingdong_1", "kaishixingdong_1")
    #         self.logger.info("round " + str(cnt) + " begins")
    #         if self.wait_for_mission(5):
    #             self.logger.info("round " + str(cnt) + " finished")
    #         else:
    #             self.logger.info("mission failed, try again")
    #             cnt -= 1
    #         if cnt >= times:
    #             self.logger.info("mission complete")
    #             return
    #         else:
    #             self.click_icon("back")
    #
    # def xinpiansousuo(self, part, level, times):
    #     self.focus()
    #     cnt = 0
    #     self.back_to_menu()
    #     self.click_icon("zuozhan", "xinpiansousuo")
    #     self.click_icon("xinpiansousuo", part)
    #     self.click_icon(part, level)
    #     while True:
    #         cnt += 1
    #         self.click_icon(level, "kaishixingdong")
    #         if self.get_icon("dailizhihui_ON") is None:
    #             self.click_icon("dailizhihui_OFF", "dailizhihui_ON")
    #         self.click_icon("kaishixingdong")
    #         if self.get_icon("lizhihaojin") is not None:
    #             self.click_icon("lizhihaojin", "lizhihaojin")
    #             self.logger.info("run out of itellect")
    #             # sys.exit()
    #             return
    #         self.click_icon("kaishixingdong_1", "kaishixingdong_1")
    #         self.logger.info("round " + str(cnt) + " begins")
    #         if self.wait_for_mission(5) is True:
    #             self.logger.info("round " + str(cnt) + " finished")
    #         else:
    #             self.logger.info("mission failed, try again")
    #             cnt -= 1
    #         if cnt >= times:
    #             self.logger.info("mission complete")
    #             return
    #         else:
    #             self.click_icon("back")
    #
    # def jiaomiemoshi(self, part, times):
    #     self.focus()
    #     self.back_to_menu()
    #     self.click_icon("zuozhan", "jiaomiezuozhan")
    #     self.click_icon("jiaomiezuozhan")
    #     self.find_icon('yanguolongmen')
    #     self.click_icon('yanguolongmen')
    #     cnt = 0
    #     while True:
    #         cnt += 1
    #         self.click_icon(part, "kaishixingdong")
    #         if self.get_icon("dailizhihui_ON") is None:
    #             self.click_icon("dailizhihui_OFF", "dailizhihui_ON")
    #         self.click_icon("kaishixingdong")
    #         if self.get_icon("lizhihaojin") is not None:
    #             self.click_icon("lizhihaojin", "lizhihaojin")
    #             self.logger.info("run out of itellect")
    #             # sys.exit()
    #             return
    #         self.click_icon("kaishixingdong_1", "kaishixingdong_1")
    #         self.logger.info("round " + str(cnt) + " begins")
    #         if self.wait_for_mission(5):
    #             self.logger.info("round " + str(cnt) + " finished")
    #         else:
    #             self.logger.info("mission failed, try again")
    #             cnt -= 1
    #         if cnt >= times:
    #             self.logger.info("mission complete")
    #             return
    #         else:
    #             self.click_icon("back")
    #
    # def activity_checkpoint(self, activityname, part, level, times):  # 活动关卡
    #     self.focus()
    #     cnt = 0
    #     self.back_to_menu()
    #     self.click_icon("zuozhan", activityname)
    #     self.click_icon(activityname, activityname)
    #     self.delay(2)
    #     while self.get_icon(part) is None:
    #         if cnt > 5:
    #             self.logger.info("the part is not open today")
    #             return
    #         self.drag(xdistance=-500, speed=500)
    #         cnt += 1
    #     self.click_icon(part, part)
    #     self.get_icon(level)
    #     cnt = 0
    #     while True:
    #         cnt += 1
    #         self.click_icon(level)
    #         if self.get_icon("dailizhihui_ON") is None:
    #             self.click_icon("dailizhihui_OFF", "dailizhihui_ON")
    #         try:
    #             self.click_icon("kaishixingdong")
    #         except Exception:
    #             self.click_icon("kaishixingdong_activity")
    #         if self.get_icon("lizhihaojin") is not None:
    #             self.click_icon("lizhihaojin", "lizhihaojin")
    #             self.logger.info("run out of itellect")
    #             return
    #         self.click_icon("kaishixingdong_1", "kaishixingdong_1")
    #         self.logger.info("round " + str(cnt) + " begins")
    #         if self.wait_for_mission(5) is True:
    #             self.logger.info("round " + str(cnt) + " finished")
    #         else:
    #             self.logger.info("mission failed, try again")
    #             cnt -= 1
    #         if cnt >= times:
    #             self.logger.info("mission complete")
    #             return
    #         else:
    #             self.click_icon("back")
    #
    # def generate_material_list(self):
    #     self.focus()
    #     loc1 = r"output\\wordsImgs\\MaterialName.jpg"
    #     loc2 = r"output\\wordsImgs\\MatrerialNumber.jpg"
    #     outputloc = r"output\\MaterialList.txt"
    #     file = open(outputloc, "w+", encoding="utf-8")
    #     list_ = []
    #
    #     def back():
    #         auto.click(1498, 164)
    #
    #     def drag():
    #         self.drag(xstart=1706, ystart=403, speed=250, xdistance=-240, ydistance=0)
    #
    #     def get_info(x_, y_):
    #         auto.click(x_, y_)
    #         self.delay(1)
    #         auto.screenshot(region=(424, 262, 672 - 424, 307 - 262)).save(loc1)
    #         auto.screenshot(region=(1352, 262, 1499 - 1352, 307 - 262)).save(loc2)
    #         try:
    #             name = baidu_ocr(loc1, self.APP_ID, self.API_KEY, self.SECRECT_KEY)
    #         except Exception:
    #             print("can't parse material's name")
    #             back()
    #             return True
    #         if name.find("技巧概要") != -1 or name.find("芯片助剂") != -1 or name.find("芯片") != -1 or name.find("信物") != -1:
    #             print("finding completes")
    #             back()
    #             return False
    #         if name.find("作战记录") != -1:
    #             back()
    #             return True
    #         try:
    #             number = baidu_ocr(loc2, self.APP_ID, self.API_KEY, self.SECRECT_KEY)
    #         except Exception:
    #             print("can't parse material's number")
    #             back()
    #             return True
    #         list_.append({"name": name, "need": 0, "have": int(number)})
    #         back()
    #         return True
    #
    #     def write_to_table(s):
    #         file.write(s)
    #         file.close()
    #
    #     def convert_list(lst):
    #         s = str(lst)
    #         s = s.replace("'", "\"")
    #         s = s.replace(" ", "")
    #         return s
    #
    #     x = 1712
    #     y = 283
    #     self.back_to_menu()
    #     self.click_icon("cangku", "cangku")
    #     self.click_icon("yangchengcailiao")
    #     self.delay(1)
    #     for i in range(0, 8):
    #         for j in range(0, 3):
    #             get_info(x - i * 200, y + j * 250)
    #             self.delay(0.5)
    #     while True:
    #         drag()
    #         self.delay(1)
    #         for j in range(0, 3):
    #             if get_info(x, y + j * 250) is False:
    #                 res = convert_list(list_)
    #                 write_to_table(res)
    #                 return res
    #             self.delay(0.5)
    #
    # def get_intellect(self):
    #     self.focus()
    #     self.back_to_menu()
    #     loc = r"output\\wordsImgs\\Intellect.jpg"
    #     auto.screenshot(region=(1118, 210, 1278 - 1118, 310 - 210)).save(loc)
    #     interllect = baidu_ocr(loc, self.APP_ID, self.API_KEY, self.SECRECT_KEY)
    #     print(interllect)
    #     return interllect


class ArknightsException(Exception):
    pass
