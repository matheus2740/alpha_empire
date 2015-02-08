from panda3d.core import Vec3, TextNode
from direct.gui.DirectGui import *
import traceback

class Console(object):

    def __init__(self, base):
        self.log = DirectLabel(
            text='>>> # debug console',
            text_wordwrap=50,
            text_fg=(0, 0, 1, 1),
            text_bg=(0, 0, 0, 0.7),
            relief=None,
            text_mayChange=True,
            text_align=TextNode.ALeft,
            suppressKeys=0
        )
        self.log.setScale(0.05, 0.05, 0.05)
        self.log.setPos(0, 0, (self.log.getHeight()*0.05)-1)

        self.log.reparentTo(base.a2dTopLeft)

        self.input = DirectEntry(
            pos=Vec3(0, 0, -0.05),
            text_wordwrap=50,
            command=self.command,
            text_bg=(0, 0, 0, 0.5),
            relief='sunken',
            text_mayChange=True,
            width=50,
            suppressKeys=0
        )
        self.input.setScale(0.05, 0.05, 0.05)
        self.input.reparentTo(base.a2dLeftCenter)

        base.accept('shift-control-a', self.toggle_visibility)

        self.hide()

    def command(self, text):
        self.input.enterText('')
        if text.strip().lower() == 'hide':
            self.hide()
            return
        self.log['text'] += '\n>>> ' + text
        try:
            res = str(eval(text))
        except:
            res = traceback.format_exc()
        self.log['text'] += '\n%s\n\n' % (res,)
        self.log.resetFrameSize()
        self.log.setPos(0, 0, (self.log.getHeight()*0.05)-1)
        print self.log.getHeight()

    def hide(self):
        self.log.hide()
        self.input.hide()

    def show(self):
        self.log.show()
        self.input.show()

    def toggle_visibility(self):
        if self.log.is_hidden():
            self.show()
        else:
            self.hide()
