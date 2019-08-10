# cones.py -- Loads and maintains visualization for cones on the field
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4

class Cones:
	def __init__(self):
		self.dummy = 0.0

	def loadModel(self):
		self.cone = loader.loadModel("cone_1.obj", noCache=True)
		self.cone.reparentTo(render)
		self.cone.setPos(0.0, 0.0, 0.0)

	def setPos(self, x, y):
		self.cone.setX(x)
		self.cone.setY(y)
