import random
from direct.actor.Actor import Actor
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile

from hex import HexGrid

loadPrcFile("./hexemp.prc")


class TheGreatTTF(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.hexgrid = HexGrid(10, 10, self)

        def node_click(node):
            node.setColorScale(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)

        self.hexgrid.onclick(node_click)




app = TheGreatTTF()
app.run()

