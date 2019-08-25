# robotsim.py -- Main app for robot swerver simulation
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
from math import pi, sin, cos, sqrt, atan2
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4
from panda3d.core import Mat4
from panda3d.core import (Geom, GeomLinestrips, GeomNode, GeomVertexData,
                          GeomVertexFormat, GeomVertexWriter, InputDevice,
                          LineSegs, Point3, TextNode, TransparencyAttrib)
from code.swervebot import SwerveBot
from code.cones import Cones

import VisualAssets.graphs as graphs
import Physics.primitivePhysics as physics

import Input.joy as joy

class RobotSim (ShowBase) :
	def __init__(self, textboxes = ({}), graph_objs = {}, default_text_scale = .07):
		ShowBase.__init__(self)
		self.scene = self.loader.loadModel("field_1.obj", noCache=True)
		# Reparent the model to render.
		self.scene.reparentTo(self.render)
		self.scene.setPos(0, 0, 0)
		self.insertLight("MainLight", 0, 0, 75)
		self.insertLight("ExtraLight1", -50, 0, 75)
		self.resetSim()

		self.robot = SwerveBot()
		self.robot.loadModel()

		self.setupCones()
		#Joystick setup
		self.joys = self.devices.getDevices(InputDevice.DeviceClass.gamepad)
    #Attaches input devices to base
		for ind, joy in enumerate(self.joys):
			self.attachInputDevice(joy, prefix=str(ind))
		#Joystick reading variable
		self.joystick_readings = []
		#Text boxes which will be rendered every frame
    #Key is a node name, value is a dict with
    #arguments such as text, location, and scale
    #Hack to keep default argument immutable and prevent bugs
		if type(textboxes) == tuple:
			self.textboxes = textboxes[0]
		else:
			self.textboxes = textboxes
		self.textNodes = {}
		self.textNodePaths = {}
		self.default_text_scale = default_text_scale
		self.text_is_active = False
    #If the text toggle button has been up for more than one frame
		self.text_button_lifted = True
    #If changes that need to be made on text have taken place
		self.text_toggled = True
		#Graph drawing data
		#Lines to be rendered on the next frame
		self.lines = []
		self.lineNodes = []
		self.lineNodePaths = []
		self.graphs = graph_objs
		for graph in self.graphs:
			self.graphs[graph].dummyUpdate()
		#Init physics engine
		self.physics = physics.Swerve()
		#Geometry drawing node
		self.geom_node = GeomNode("drawer")
		self.aspect2d.attach_new_node(self.geom_node)
		#Tasks
		self.taskMgr.add(self.updateJoysticks, "updateJoysticks")
		self.taskMgr.add(self.driveRobot, "driveRobot")
		self.taskMgr.add(self.updateHud, "updateHud")
		self.taskMgr.add(self.toggleHud, "toggleHud")
		self.accept('r', self.reportStatus)
		self.accept('i', self.resetSim)
		self.accept('a', self.robot.toggleAutoDrive)


	def driveRobot(self, task):
		"""
		Task to drive the robot
		"""
		x = self.joystick_readings[0]["axes"]["left_x"]
		y = self.joystick_readings[0]["axes"]["left_y"]
		z = self.joystick_readings[0]["axes"]["right_x"]
		self.physics.sendControls(x, y, z)
		self.physics.update()
		self.setRobotToLocation()
		return Task.cont

	def setRobotToLocation(self):
		x = self.physics.position[0]
		y = self.physics.position[1]
		angle = self.physics.position[2]*(2*pi)
		self.robot.setPos(x, y, angle)
		caster_angle_1 = self.physics.positions["brswerve"]*(180/pi)+90
		caster_angle_2 = self.physics.positions["blswerve"]*(180/pi)+90
		caster_angle_3 = self.physics.positions["flswerve"]*(180/pi)+90
		caster_angle_4 = self.physics.positions["frswerve"]*(180/pi)+90
		self.robot.setCasterAngles(caster_angle_1, caster_angle_2, caster_angle_3, caster_angle_4)
		wheel_angle_1 = self.physics.positions["brwheel"]/(2*pi)
		wheel_angle_2 = self.physics.positions["blwheel"]/(2*pi)
		wheel_angle_3 = self.physics.positions["flwheel"]/(2*pi)
		wheel_angle_4 = self.physics.positions["frwheel"]/(2*pi)
		self.robot.setWheelTurns(wheel_angle_1, wheel_angle_2, wheel_angle_3, wheel_angle_4)

	def updateJoysticks(self, task):
		joystick_readings = []
		for joystick in self.joys:
			joystick_readings.append(joy.readJoystickValues(joystick))
		self.joystick_readings = joystick_readings
		return Task.cont

	def updateHud(self, task):
		#Removes all lines from the geometry node
		self.geom_node.removeAllGeoms()
		if self.text_is_active:
			frvector = "Mag: {}\nDir: {}\nTheta_acc: {}\nVel_x: {}\nVel_y: {}\nVel_t: {}\nPos: {}, {}\nRot: {}".format(round(self.physics.vectors["frame"].magnitude, 4),
															round(self.physics.vectors["frame"].direction, 4),
															round(self.physics.z_acceleration, 4),
															round(self.physics.velocities["frame"][0], 4),
															round(self.physics.velocities["frame"][1], 4),
															round(self.physics.z_velocity, 4),
															round(self.physics.position[0], 4),
															round(self.physics.position[1], 4),
															round(self.physics.position[2], 4))
			self.textboxes["frvector_value"]["text"] = frvector
			self.lines = []
			for graph_name in self.graphs:
				lines, strings = self.graphs[graph_name].render()
        #Splits the lines into pairs of points and assigns them to self.lines
				for line in lines:
					self.lines += pairPoints(line)
        #Clears all graph generated strings from textboxes
				deleted = []
				for key in self.textboxes:
					if graph_name in key:
						deleted.append(key)
				for key in deleted:
					self.textboxes.pop(key)
        #Processes strings into textboxes
				for ind, val in enumerate(strings):
					location, string = val
					self.textboxes["{}_{}".format(graph_name, str(ind))] = {"location": location, "text": string}
			self.manageTextNodes()
			self.renderText()
			self.manageGeometry()
		return Task.cont

	def toggleHud(self, task):
		if self.joystick_readings[0]["axes"]["right_trigger"] >= .05 and self.text_button_lifted:
			self.text_is_active = not self.text_is_active
			self.text_toggled = False
			self.text_button_lifted = False
		elif not self.joystick_readings[0]["axes"]["right_trigger"] >= .05:
			self.text_button_lifted = True
		if not self.text_toggled:
			if not self.text_is_active:
				for path in self.textNodePaths:
					self.textNodePaths[path].detachNode()
				for path in self.lineNodePaths:
					path.detachNode()
			else:
				for node in self.textNodes:
					self.textNodePaths[node] = self.aspect2d.attachNewNode(self.textNodes[node])
				for node in self.lineNodes:
					self.aspect2d.attachNewNode(node)
		return Task.cont
		
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

def pairPoints(points, closed=False):
	"""
	Seperates a series of points into a series of lines connecting the points
	"""
	pairs = []
	for ind, point in enumerate(points):
		if ind == len(points)-1:
			#If on the last point of the set
			#break the loop or link back to the start
			#depending on arguments
			if closed:
				pairs.append((point, points[0]))
			else:
				break
		else:
			#If not on the last point, add the next line as a pair of points
			pairs.append((point, points[ind+1]))
	return pairs


graphs = {"y_graph": graphs.XYGraph(location=(-.4,-.4)), "vector_graph": graphs.PolarGraph(location=(-.8, -.5))}
textboxes = {"frvector_label": {}, "frvector_value": {"location": (.4, .7)}}
app = RobotSim(textboxes, graphs)

app.run()

