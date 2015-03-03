__author__ = 'salvia'

from src.dgvm.datamodel import Datamodel
from src.dgvm.datamodel_meta import business_rule, IntegerVMAttribute, PairVMAttribute


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
    position = PairVMAttribute()

    @business_rule(on_change=(action,))
    def action_limit(self, *args, **kwargs):
        if self.action < 0:
            return False
        return True