__author__ = 'salvia'

from src.dgvm.datamodel import Datamodel
from src.dgvm.datamodel_meta import constraint, IntegerVMAttribute, PairVMAttribute


class Board(Datamodel):
    """
    Preliminary board datamodel,
    used to test DGVM
    """
    width = IntegerVMAttribute()
    height = IntegerVMAttribute()