#gamepad.py -- game pad implementation
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4
from panda3d.core import InputDevice
import math

class GamePad:
	def __init__(self):
		self.dummy = 0

	def setupGamePad(self, sb):
		self.haveGamePad = False
		pads = sb.devices.getDevices(InputDevice.DeviceClass.gamepad)
		if len(pads) <= 0:
			print("No suitable game-pad or controller found.")
			return
		pad = pads[0]
		sb.attachInputDevice(pad, prefix="gamepad")
		axis_x = pad.findAxis(InputDevice.Axis.x)
		axis_y = pad.findAxis(InputDevice.Axis.y)
		axis_z = pad.findAxis(InputDevice.Axis.z)
		axis_yaw = pad.findAxis(InputDevice.Axis.yaw)
		axis_pitch = pad.findAxis(InputDevice.Axis.pitch)
		axis_roll = pad.findAxis(InputDevice.Axis.roll)
		axis_left_x = pad.findAxis(InputDevice.Axis.left_x)
		axis_left_y = pad.findAxis(InputDevice.Axis.left_y)
		axis_right_x = pad.findAxis(InputDevice.Axis.right_x)
		axis_right_y = pad.findAxis(InputDevice.Axis.right_y)
		axis_list = []

		if axis_x:
			axis_list.append(axis_x)
		else:
			print("X Axis not found on controller.")
		if axis_y:
			axis_list.append(axis_y)
		else:
			print("Y Axis not found on controller.")
		if axis_z:
			axis_list.append(axis_z)
		else:
			print("Z Axis not found on controller.")
		if axis_yaw:
			axis_list.append(axis_yaw)
		else:
			print("Yaw Axis not found on controller.")
		if axis_pitch:
			axis_list.append(axis_pitch)
		else:
			print("Pitch Axis not found on controller.")
		if axis_roll:
			axis_list.append(axis_roll)
		else:
			print("Roll Axis not found on controller.")
		if axis_left_x:
			axis_list.append(axis_left_x)
		else:
			print("Left X Axis not found on controller.")
		if axis_left_y:
			axis_list.append(axis_left_y)
		else:
			print("Left Y Axis not found on controller.")
		if axis_right_x:
			axis_list.append(axis_right_x)
		else:
			print("Right X Axis not found on controller.")
		if axis_right_y:
			axis_list.append(axis_right_y)
		else:
			print("Right Y Axis not found on controller.")

		print("Number of axes found on controller: ", len(axis_list))
		self.axes = axis_list
		self.haveGamePad = True

	def getAxisValues(self):
		if not self.haveGamePad:
			return 0.0, 0.0, 0.0, 0.0
		v = []
		for i in range(4):
			if i < len(self.axes):
				v.append(self.axes[i].value)
			else:
				v.append(0.0)
		return v[0], v[1], v[2], v[3]

	def startReportLoop(self):
		taskMgr.add(self.reportTask, "GamePadReportTask")

	def reportTask(self, task):
		i = math.fmod(task.frame, 10)
		if i == 0:
			a, b, c, d = self.getAxisValues()
			print("Axis Values", a, b, c, d)
		return Task.cont
