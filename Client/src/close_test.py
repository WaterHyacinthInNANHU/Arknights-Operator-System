from arknights.operator import Operator
from util.logger import CmdLogger
from time import sleep
op = Operator(CmdLogger('test'))
sleep(60*60)
op.close_emulator()

