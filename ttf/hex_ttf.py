import random
from direct.actor.Actor import Actor
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile
import sys
from hex import HexGrid

sys.path.insert(0, "../render_pipeline")
# Import the main render pipeline class
from rpcore import RenderPipeline
from rpcore.util.movement_controller import MovementController

loadPrcFile("./hexemp.prc")


class TheGreatTTF(ShowBase):

    def __init__(self):


        # Construct and create the pipeline
        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)
        self.render_pipeline.daytime_mgr.time = "19:17"
        # ShowBase.__init__(self)

        self.hexgrid = HexGrid(2, 2, self)

        ps = [None]

        def node_click(node):
            if ps[0] is not None:
                ps[0].deselect()
            node.select()
            ps[0] = node

        self.hexgrid.onclick(node_click)

        # self.controller = MovementController(self)
        # self.controller.setup()


app = TheGreatTTF()
app.run()

