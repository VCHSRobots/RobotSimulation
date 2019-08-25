# swervebot.py -- Loads and maintains visualization for the swerve bot
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4
import math

class SwerveBot:
	def __init__(self):
		self.frame_pos = (0, 0)
		self.frame_dir = 0.0
		self.wheel_dirs = (0.0, 0.0, 0.0, 0.0)
		self.autoDriving = False
		#taskMgr.add(self.autoDrive, "AutoDrive")

	def loadModel(self):
		self.frame = loader.loadModel("frame_1.obj", noCache=True)
		self.frame.reparentTo(render)
		self.frame.setPos(0.0, 0.0, 0.0)
		self.wheels = []  
		locs = [(-1.0, -1.0), (-1.0, 1.0), (1.0, 1.0), (1.0, -1.0)]
		wnames = ["Back-Right", "Back-Left", "Front-Left", "Front-Right"]
		for i in range(4):
			caster = loader.loadModel("caster_1.obj", noCache=True)
			x, y = locs[i]
			sx, sy = 1.7, 1.7
			name = wnames[i]
			caster.reparentTo(self.frame)
			caster.setX(x*sx)
			caster.setY(y*sy)
			caster.setZ(0.0)
			wheel = loader.loadModel("wheel_1.obj", noCache=True)
			wheel.reparentTo(caster)
			wheel.setPos(0.0, 0.0, 0.0)
			caster_angle = 0.0
			wheel_turns = 0.0
			self.wheels.append((caster, wheel, name))

	def setPos(self, x, y, angle):
		self.frame.setX(x)
		self.frame.setY(y)
		self.frame.setH(angle);

	def setCasterAngles(self, a1, a2, a3, a4):
		c1, w1, n1 = self.wheels[0]
		c1.setH(a1+90)
		c2, w2, n2 = self.wheels[1]
		c2.setH(a2+90)
		c3, w3, n3 = self.wheels[2]
		c3.setH(a3+90)
		c4, w4, n4 = self.wheels[3]
		c4.setH(a4+90)

	def setWheelTurns(self, t1, t2, t3, t4):
		a1 = math.fmod(t1, 1.0) * 360.0
		a2 = math.fmod(t2, 1.0) * 360.0
		a3 = math.fmod(t3, 1.0) * 360.0
		a4 = math.fmod(t4, 1.0) * 360.0
		c1, w1, n1 = self.wheels[0]
		w1.setR(a1)
		c2, w2, n2 = self.wheels[1]
		w2.setR(a2)
		c3, w3, n3 = self.wheels[2]
		w3.setR(a3)
		c4, w4, n4 = self.wheels[3]
		w4.setR(a4)

	def toggleAutoDrive(self):
		if self.autoDriving:
			self.turnOffAutoDrive()
		else:
			self.turnOnAutoDrive()

	def turnOnAutoDrive(self):
		if self.autoDriving:
			return
		print("Turning on Audo Drive")
		self.autoDriving = True
		self.startPos = self.frame.getX()
		taskMgr.add(self.autoDrive, "AutoDrive")

	def turnOffAutoDrive(self):
		if not self.autoDriving:
			return
		print("Turning off Auto Drive")
		self.autoDriving = False
		taskMgr.remove("AutoDrive")
		
	def autoDrive(self, task):
		x = math.fmod(task.time + self.startPos, 20.0)
		a = math.fmod(task.time * 10, 360.0)
		w = task.time * 0.5
		#print("DeltaX", x, task.id)
		if x > 10:
			x = 20 - x
		self.setPos(x, 0.0, a)
		self.setCasterAngles(a, a+10, a+30, a+60)
		self.setWheelTurns(w, w*1.25, w*-0.75, w*2.0)
		return Task.cont





