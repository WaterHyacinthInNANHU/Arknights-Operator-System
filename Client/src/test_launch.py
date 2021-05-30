from arknights.operator import Operator, ANNIHILATION_OPERATION
from util.logger import CmdLogger
op = Operator(CmdLogger('test'))
op.launch_and_connect_emulator()
op.launch_game()
# op.login()
op.login(force_re_login=True)
