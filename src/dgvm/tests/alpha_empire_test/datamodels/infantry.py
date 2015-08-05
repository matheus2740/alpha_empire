__author__ = 'salvia'

from src.dgvm.datamodel import Datamodel
from src.dgvm.datamodel_meta import constraint, IntegerVMAttribute, PairVMAttribute, ForeignModelVMAttribute
from board import Board
from src.dgvm.instruction import instruction
import math


class Infantry(Datamodel):
    """
    Preliminary infantry datamodel,
    used to test DGVM
    """
    n_units = IntegerVMAttribute()
    attack_dmg = IntegerVMAttribute()
    armor = IntegerVMAttribute()
    health = IntegerVMAttribute()
    action = IntegerVMAttribute()
    position = PairVMAttribute(int)
    board = ForeignModelVMAttribute(Board)

    @instruction(opcode=101, mnemonic='MOVE', args=(Datamodel, int, int), onself=True)
    def move(inst, infantry, x, y):
        dx = (x - infantry.position[0]) ** 2
        dy = (y - infantry.position[1]) ** 2
        d = dx + dy
        root = math.sqrt(d)
        infantry.action -= math.ceil(root)
        infantry.position = (x, y)

    @constraint.on_change(action)
    def action_limit(cons, old, new, related):
        if new < 0:
            return False
        return True

    @constraint.on_change(position, related=(board,))
    def board_bounds(cons, old, new, related):

        if new.x < 0 or new.y < 0:
            return False

        board = related['board']
        if new.x >= board.width or new.y >= board.height:
            return False

        return True
