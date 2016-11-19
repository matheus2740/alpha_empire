from collections import namedtuple
from math import sqrt
import random

from direct.task import Task
from panda3d.core import BitMask32, CollisionTraverser, CollisionHandlerQueue, GraphicsEngine
from panda3d.core import CollisionNode, CollisionRay, Point3


class HexNode(object):

    def __init__(self, fname, pos, root, i):

        node = loader.loadModel(fname)
        node.setPos(pos.x, pos.y, pos.z)

        # TODO: DEBUG
        node.setColorScale(random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1), 1)

        node.reparentTo(root)

        # make it collideable
        node.find("**/Cylinder").node().setIntoCollideMask(BitMask32.bit(1))
        # Set a tag on the square's node so we can look up what square this is
        # later during the collision pass
        node.find("**/Cylinder").node().setTag('hexmesh_i', str(i))

        node.setTag('hexnode_i', str(i))

        self.node = node

    def animatez(self, z):
        pos = self.getPos()
        pos.z = z
        interval = self.node.posInterval(.5, pos, blendType='easeInOut')
        interval.start()
        pass

    def select(self):
        self.animatez(10)

    def deselect(self):
        self.animatez(0)

    def __getattr__(self, item):
        return getattr(self.node, item)


class HexGrid(object):

    def __init__(self, w, h, show):

        self.width = w
        self.height = h

        self.loader = show.loader

        self.root = show.render.attachNewNode("hexgrid_root")

        self.base_tile = 'hex'

        self.diameter = 20
        self.inscribed = self.diameter * sqrt(3) / 2

        self.nodes = None

        self.show = show

        # Since we are using collision detection to do picking, we set it up like
        # any other collision detection system with a traverser and a handler
        self.picker = CollisionTraverser()  # Make a traverser
        self.picker_queue = CollisionHandlerQueue()  # Make a handler
        # Make a collision node for our picker ray
        self.pickerNode = CollisionNode('mouseRay')
        # Attach that node to the camera since the ray will need to be positioned
        # relative to it
        self.pickerNP = show.camera.attachNewNode(self.pickerNode)
        # Everything to be picked will use bit 1. This way if we were doing other
        # collision we could seperate it
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()  # Make our ray
        # Add it to the collision node
        self.pickerNode.addSolid(self.pickerRay)
        # Register the ray as something that can cause collisions
        self.picker.addCollider(self.pickerNP, self.picker_queue)

        self.assemble()

        self.onclick_fn = None

        # self.mouseTask = self.taskMgr.add(self.mouseTask, 'mouseTask')
        # self.accept("mouse1", self.grabPiece)  # left-click grabs a piece
        show.accept("mouse1-up", self.mouse_up)  # releasing places it

    def mouse_up(self):
        # This task deals with the highlighting and dragging based on the mouse

        # Check to see if we can access the mouse. We need it to do anything
        # else
        if self.onclick_fn and self.show.mouseWatcherNode.hasMouse():
            # get the mouse position
            mpos = self.show.mouseWatcherNode.getMouse()

            # Set the position of the ray based on the mouse position
            self.pickerRay.setFromLens(self.show.camNode, mpos.getX(), mpos.getY())

            # Do the actual collision pass
            self.picker.traverse(self.root)
            if self.picker_queue.getNumEntries() > 0:
                # if we have hit something, sort the hits so that the closest
                # is first, and highlight that node
                self.picker_queue.sortEntries()
                i = int(self.picker_queue.getEntry(0).getIntoNode().getTag('hexmesh_i'))

                self.onclick_fn(self.nodes[i])

        return Task.cont

    def onclick(self, fn):

        self.onclick_fn = fn

    def index_of(self, x, y):

        return x + y * self.width

    def xyi_iter(self, fn):

        for x in range(self.height):
            for y in range(self.width):

                fn(x, y, self.index_of(x, y))

    def node_iter(self, fn):

        for node in self.nodes:
            fn(node)

    def assemble(self):

        random.seed(3141592)

        def make_node(x, y, i):

            row_offset = self.inscribed / 2. if y % 2 == 0 else 0

            pos = Point3(x * self.inscribed + row_offset, y * self.diameter * 0.75, 0)

            self.nodes[i] = HexNode(self.base_tile, pos, self.root, i)

        self.nodes = [None for _ in range(self.width * self.height)]

        self.xyi_iter(make_node)


