#gamepad_logitech.py -- game pad implementation -- For Logiteck Big Stick
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4
from panda3d.core import InputDevice
import pygame
import math

class GamePad_Logitech:
	def __init__(self):
		self.dummy = 0
		pygame.init()
		pygame.joystick.init()

	def setupGamePad(self, sb):
		self.haveGamePad = False
		if pygame.joystick.get_count() <= 0:
			print("No suitable game-pad or controller found.")
			return
		taskMgr.add(self.joystickPumper, "JoystickPumper")
		self.joystick = pygame.joystick.Joystick(0)
		self.joystick.init()
		self.haveGamePad = True 
		print("Logitech joystick initialized.")

	def getAxisValues(self):
		if not self.haveGamePad:
			return 0.0, 0.0, 0.0, 0.0
		v = []
		n = self.joystick.get_numaxes()
		for i in range(4):
			if i < n:
				v.append(self.joystick.get_axis(i))
			else:
				v.append(0.0)
		return v[0], v[1], v[2], v[3]

	def getButtons(self):
		buttons = [False, False, False, False, False, False, False, False, 
				   False, False, False, False]
		if not self.haveGamePad:
			return buttons
		n = self.joystick.get_numbuttons()
		for i in range(12):
			if i < n:
				buttons[i] = self.joystick.get_button(i)
		return buttons

	def startReportLoop(self):
		taskMgr.add(self.reportTask, "GamePadReportTask")

	def reportTask(self, task):
		i = math.fmod(task.frame, 10)
		if i == 0:
			a, b, c, d = self.getAxisValues()
			print("Axis Values", a, b, c, d)
		#print("Buttons: ", self.getButtons())
		return Task.cont

	def joystickPumper(self, task):
		pygame.event.pump()
		return Task.cont
