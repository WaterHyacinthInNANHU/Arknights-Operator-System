# from arknights.operator import ArknightsOperator
# from ruamel.yaml import YAML
# from arknights.engines.database import *

# # test config
# import config
# print(config.get('user/account'))

# yaml = YAML()
# with open("config/config-dev.yaml", 'r', encoding='utf-8') as f:
#     _ydoc = yaml.load(f)
# pass
# arkop = ArknightsOperator()
# screen = arkop.screenshot()

# # test grab_temp
# from dev import grab_temp
# grab_temp.grab()

# # test grab_temp
# from dev import grab_pos
# grab_pos.grab()

# # test Player._locate_template
# from arknights.player import Player
# player = Player()
# top_left, bottom_right = player.locate_template('launch/launch_icon')
# print(top_left, bottom_right)

# # test ocr
# from arknights.ocr import OCREngine
# from PIL import Image
# image = Image.open('test/imgs/target.png')
# engine = OCREngine('zh')
# res = engine.recognize(image)

# # test database
# from arknights.resource.database import load_template
# load_template('launch/launch_icon')

# # test path
# import os
# print(os.getcwd())

# # test game launching
# from arknights.player import Player
# player = Player()
# player.launch_game()

# # test emulator launching
# from arknights.player import Player
# player = Player()
# player.launch_emulator()

# # test list_pos
# from dev.list_pos import *
# ls()

# # test list_temp
# from dev.list_temp import *
# ls()

# test operator
from arknights.operator import Operator, ANNIHILATION_OPERATION
from util.logger import CmdLogger
import connector.ADBConnector
# connector.ADBConnector.logger = CmdLogger('adb')
op = Operator(CmdLogger('test'))
# op.player._get_device_pid()
# import config
# print(op.player.is_device_online())
op.launch_and_connect_emulator()
op.launch_game()
op.login()
# op.navigate_to_main_panel()
# op.navigate_to_default_annihilation()
# op._get_warning_message_by_ocr()
# for _ in range(5):
#     op.operate(ANNIHILATION_OPERATION)
# op.close_emulator()
# for _ in range(9):
#     op.operate()
# from time import sleep
# sleep(60*60)
# op.close_emulator()
# op.player.wait_until_screen_stable(10, 1, 0.01)


# test adb
# from connector.ADBConnector import ADBConnector
# print(ADBConnector.available_devices())

# # test move_temp
# from arknights.resource.dev import move_temp
# from arknights.resource import TEMPLATE_PATH
# move_temp.clear_file_tree(TEMPLATE_PATH)

# test psutil
# import psutil
# pp = None
# for p in psutil.process_iter():
#     if p.name() == 'NemuPlayer.exe':
#         pp = p
# print(pp.pid)

# kill progress
# import os
# import config
# from time import sleep
# process_name = config.get('device/emulator_launcher')
# print(process_name)
# os.system("tskill {}".format(process_name))
# import psutil
# p = psutil.Process(35292)
# p.terminate()


# # close_emulator & trigger_emulator_to_start
# from arknights.operator import Operator
# from util.logger import CmdLogger
# from time import sleep
# op = Operator(CmdLogger('test'))
# op.player.trigger_emulator_to_start()
# sleep(20)
# op.player.close_emulator()

# from arknights.player import Player
# from time import sleep
# player = Player()
# player.connect_device()
# # sleep(3)
# print('dragging')
# player.drag((0.5, 0.5), (0.5, 0), 2)


pass
