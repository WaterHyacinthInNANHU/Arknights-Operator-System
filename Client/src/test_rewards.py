from arknights.operator import Operator
from util.logger import CmdLogger
op = Operator(CmdLogger('test'))
op.launch_and_connect_emulator()
op.receive_rewards()
