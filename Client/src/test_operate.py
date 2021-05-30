from arknights.operator import Operator
from util.logger import CmdLogger
op = Operator(CmdLogger('test'))
op.launch_and_connect_emulator()
for _ in range(100):
    op.operate()
op.navigate_to_main_panel()
try:
    op.receive_rewards()
except Exception as e:
    print(e)
op.close_emulator()
