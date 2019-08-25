# robotsim.py -- Main app for robot swerver simulation
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4
from panda3d.core import Mat4
from swervebot import SwerveBot
from cones import Cones
from skid import SkidTrack
from overlay import Overlay
from gamepad_logitech import GamePad_Logitech
import sys

class RobotSim (ShowBase) :
	def __init__(self):
		ShowBase.__init__(self)
		self.scene = self.loader.loadModel("field_1.obj", noCache=True)
		# Reparent the model to render.
		self.scene.reparentTo(self.render)
		self.scene.setPos(0, 0, 0)
		self.insertLight("MainLight", 25, 0, 75)
		self.insertLight("ExtraLight1", -25, 0, 75)
		self.resetSim()

		self.robot = SwerveBot()
		self.robot.loadModel()

		self.setupCones()

		self.overlay = Overlay()

		self.gamepad = GamePad_Logitech()
		self.gamepad.setupGamePad(self)
		#self.gamepad.startReportLoop()

		self.skidtrack = SkidTrack(nrects=100, wheel_width=1, zpos=4)
		self.skid_pos = (-5, -5)

		self.counter = 0
		self.accept('r', self.reportStatus)
		self.accept('i', self.resetSim)
		self.accept('a', self.robot.toggleAutoDrive)
		self.accept('c', self.count)
		self.accept('s', self.skidtrackAdd)
		self.accept('escape', sys.exit)

	def resetSim(self):
		base.disableMouse()
		self.resetCamPosition()
		self.allowMovement()

	def allowMovement(self):
		mat=Mat4(camera.getMat())
		mat.invertInPlace()
		base.mouseInterfaceNode.setMat(mat)
		base.enableMouse()
		#self.resetCamPosition()

	def insertLight(self, name, x, y, z):
		lightball = self.loader.loadModel("lightball_1.obj", noCache=True)
		lightball.reparentTo(self.render)
		lightball.setPos(x, y, z)
		plight = PointLight(name)
		plight.setColor(VBase4(1.0, 1.0, 1.0, 1))
		plnp = self.render.attachNewNode(plight)
		plnp.setPos(x, y, z)
		self.render.setLight(plnp)

	def setupCones(self):
		self.cones = []
		conepos = [(20, 20), (18, 0)]
		for cp in conepos:
			c = Cones()
			c.loadModel()
			x, y = cp
			c.setPos(x, y)
			self.cones.append(c)

	def reportStatus(self):
		x=base.camera.getX()
		y=base.camera.getY()
		z=base.camera.getZ()
		print("Camera Position", x, y, z)
		h=base.camera.getH()
		p=base.camera.getP()
		r=base.camera.getR()
		print("Camera Angle", h, p, r)

	def resetCamPosition(self):
		self.camPos = (-28, -23, 17)
		self.camAngle = (-51, -17, -12)
		x,y,z = self.camPos
		h,p,r = self.camAngle
		base.camera.setPos(x, y, z)
		base.camera.setHpr(h, p, r)

	def count(self):
		self.counter += 1
		txt = "%d" % self.counter 
		self.overlay.setText(1, txt)

	def skidtrackAdd(self):
		x, y = self.skid_pos
		x += 1
		self.skid_pos = (x, y)
		self.skidtrack.addPoint(x, y, 0.0, 1.0)

app = RobotSim()
app.run()

