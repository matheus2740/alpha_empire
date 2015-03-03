from src.dgvm.instruction import Instruction

__author__ = 'salvia'


class Move(Instruction):
    # MOVE UNIT (X, Y) -> None
    opcode = 101
    mnemonic = 'MOVE'
    n_arg = 2

    @classmethod
    def execute(cls, vm, unit, x, y):
        unit.position = (x, y)