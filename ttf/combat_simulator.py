import random


def calc_dmg(bat1, bat2):
    dmg = (
        sum(random.randint(1, bat1.attack) for _ in xrange(bat1.n_units))
        - (bat2.armor * bat2.n_units)
    )
    unit_loss = int(dmg / float(
        bat2.health
        + random.randint(1, 2)
    ))

    return dmg, unit_loss


class Battalion(object):

    def __init__(self, tag, n_units, attack, armor, health):
        self.tag = tag
        self.n_units = n_units
        self.attack = attack
        self.armor = armor
        self.health = health

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
    n_units=10,
    attack=20,
    armor=2,
    health=20
)

b = Battalion(
    tag='B',
    n_units=20,
    attack=10,
    armor=2,
    health=20
)

a.fight(b)