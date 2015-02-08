import random
import math

def calc_dmg(bat1, bat2):
    success_att = sum(1 if x < (bat1.att_prof+50-bat2.def_prof) else 0 for x in (random.randint(0, 100) for _ in xrange(bat1.n_units)))
    dmg = ((
        sum(random.randint(1, bat1.attack) for _ in xrange(success_att))
        - (bat2.armor * success_att)
    )/(0.4*bat1.n_units ** 0.5))*random.randint(1, 4)

    unit_loss = min(max(int(dmg / float(bat2.health + random.randint(1, 2))), 0),bat2.n_units)

    return dmg, unit_loss


class Battalion(object):

    def __init__(self, tag, n_units, attack, armor, health, att_prof, def_prof):
        self.tag = tag
        self.n_units = n_units
        self.attack = attack
        self.armor = armor
        self.health = health
        self.att_prof = att_prof
        self.def_prof = def_prof

    def fight(self, other):
        self_dmg, other_unit_loss = calc_dmg(self, other)
        other_dmg, self_unit_loss = calc_dmg(other, self)

        other.n_units -= other_unit_loss
        self.n_units -= self_unit_loss

        print 'stats:'
        print self.tag, 'n_units', self.n_units
        print other.tag, 'n_units', other.n_units
        print self.tag, 'inflicted', self_dmg, 'damage on', other.tag
        print other.tag, 'inflicted', other_dmg, 'damage on', self.tag
        print self.tag, 'killed', other_unit_loss, 'units of', other.tag
        print other.tag, 'killed', self_unit_loss, 'unit of', self.tag


a = Battalion(
    tag='A',
    n_units=100,
    attack=20,
    armor=2,
    health=10,
    att_prof=50,
    def_prof=50
)

b = Battalion(
    tag='B',
    n_units=70,
    attack=20,
    armor=2,
    health=10,
    att_prof=50,
    def_prof=50
)

a.fight(b)