# overlay.py -- Draws overlay info, such as heads up stuff
# DLB 08-09-2019
#

from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode

class Overlay:
	"""
    Overlay class manages visual overlays on the simulation.  Overlays work like Heads-Up Displays,
    as they are always on the same place on the screen, while the actual simulation is shown behind
    the overlays.

    Note, this class can be constructed anywhere, but it behaves as a singeton.  
    """
	instance = None
	class __Overlay:
		def __init__(self):
			print("Initing __Overlay")
			x, y, dy = 1.3, -0.85, 0.06
			self.text = []
			self.textobjs = []
			for i in range(6):
				obj = OnscreenText(text = "", pos = (x, y), 
					scale = 0.06,  fg=(0, 0, 0, 1), align=TextNode.ARight, mayChange=1)
				self.text.append("")
				self.textobjs.append(obj)
				y += dy

		def setText(self, slot, msg):
			if slot > len(self.textobjs):
				return
			self.text[slot] = msg 
			self.textobjs[slot].setText(msg)

		def getText(self, slot):
			if slot > len(self.textobjs):
				return ""
			return self.text[slot]

	def __init__(self):
		if not Overlay.instance:
			Overlay.instance = self.__Overlay()

	def setText(self, slot, msg):
		Overlay.instance.setText(slot, msg)

	def getText(self, slot):
		return Overlay.instance.getText(slot)



