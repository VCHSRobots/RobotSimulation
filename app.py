"""
app.py: The Panda3D app class which the robot simulator runs from
6/27/2019 Holiday Pettijohn
"""

from math import pi, sin, cos, atan2, sqrt

from direct.showbase.ShowBase import ShowBase
from direct.showbase.Loader import Loader
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, InputDevice, TextNode

import Input.joy as joy
import Physics.primitivePhysics as physics

class Simulator(ShowBase):
  def __init__(self):
    ShowBase.__init__(self)

    self.joys = self.devices.getDevices(InputDevice.DeviceClass.gamepad)
    #Attaches input devices to base
    for ind, joy in enumerate(self.joys):
      self.attachInputDevice(joy, prefix=str(ind))
    #Joystick reading variable
    self.joystick_readings = []

    #Add panda and background
    self.scene = self.loader.loadModel("models/environment")
    self.scene.reparentTo(self.render)
    self.scene.setScale(0.25, 0.25, 0.25)
    #Sets the scene position
    self.scene.setPos(-8, 48, 0)

    self.camera.setPos(-8, 48, -4)

    self.pandaActor = Actor("models/panda-model",
                            {"walk": "models/panda-walk4"})
    self.pandaActor.setScale(0.005, 0.005, 0.005)
    self.pandaActor.reparentTo(self.render)
    self.pandaLocation = [0, 0, 0]
    self.setPandaToLocation()
    #Text display objects
    textNodeNames = ["frvector_label",
                     "frvector_value"]
    self.textNodes = {}
    self.textNodePaths = {}
    for node in textNodeNames:
      self.textNodes[node] = TextNode(node)
      self.textNodePaths[node] = self.aspect2d.attachNewNode(self.textNodes[node])
    self.setupTextNodes()
    self.text_is_active = True
    #If the text toggle button has been up for more than one frame
    self.text_button_lifted = True
    #If changes that need to be made on text have taken place
    self.text_toggled = True
    #Loop the animation to the one loaded in the dictionary
    self.pandaActor.loop("walk")
    #Intantiates physics engine
    self.physics = physics.Swerve()
    self.taskMgr.add(self.updateJoysticks, "updateJoysticks")
    self.taskMgr.add(self.walkPandaToPhysics, "walkPandaToPhysics")
    self.taskMgr.add(self.update2dDisplay, "update2dDisplay")
    self.taskMgr.add(self.toggleText, "toggleText")

  def setupTextNodes(self):
    for node in self.textNodes:
      self.textNodePaths[node].setScale(0.07)
    self.textNodePaths["frvector_label"].setPos(.5, 0, .8)
    self.textNodePaths["frvector_value"].setPos(.5, 0, .7)
    self.textNodes["frvector_label"].setText("Front Right Wheel")

  def walkPanda(self, task):
    x = self.joystick_readings[0]["axes"]["left_x"]
    y = self.joystick_readings[0]["axes"]["left_y"]
    magnitude = sqrt(x**2+y**2)
    self.pandaLocation[0] += x/7
    self.pandaLocation[1] += y/7
    angle = atan2(y, x)*(180/pi)
    self.setPandaToLocation()
    self.pandaActor.setHpr(angle+90, 0, 0)
    if not self.pandaActor.getCurrentAnim() == "walk":
      self.pandaActor.loop("walk")
    else:
      self.pandaActor.setPlayRate(magnitude*2, "walk")
    return Task.cont

  def walkPandaToPhysics(self, task):
    """
    Makes panda walk based on inputs from physics enigne
    """
    x = self.joystick_readings[0]["axes"]["left_x"]
    y = self.joystick_readings[0]["axes"]["left_y"]
    z = self.joystick_readings[0]["axes"]["right_x"]
    self.physics.sendControls(x, y, z)
    self.physics.update()
    self.pandaLocation[0] = self.physics.position[0]
    self.pandaLocation[1] = self.physics.position[1]
    angle = self.physics.position[2]*(180/pi)
    self.setPandaToLocation()
    self.pandaActor.setHpr(angle+180, 0, 0)
    return Task.cont

  def setPandaToLocation(self):
    self.pandaActor.setPos(self.pandaLocation[0], self.pandaLocation[1], self.pandaLocation[2])

  def updateJoysticks(self, task):
    joystick_readings = []
    for joystick in self.joys:
      joystick_readings.append(joy.readJoystickValues(joystick))
    self.joystick_readings = joystick_readings
    return Task.cont

  def update2dDisplay(self, task):
    """
    Updates the 2d heads-up overlay
    """
    frvector = "Mag: {}\nDir: {}\nTheta_acc: {}\nVel_x: {}\nVel_y: {}\nVel_t: {}\nPos: {}, {}\nRot: {}".format(round(self.physics.vectors["frame"].magnitude, 4),
                                                  round(self.physics.vectors["frame"].direction, 4),
                                                  round(self.physics.z_acceleration, 4),
                                                  round(self.physics.velocities["frame"][0], 4),
                                                  round(self.physics.velocities["frame"][1], 4),
                                                  round(self.physics.z_velocity, 4),
                                                  round(self.physics.position[0], 4),
                                                  round(self.physics.position[1], 4),
                                                  round(self.physics.position[2], 4))
    self.textNodes["frvector_value"].setText(frvector)
    return Task.cont

  def toggleText(self, task):
    if self.joystick_readings[0]["axes"]["right_trigger"] >= .05 and self.text_button_lifted:
      self.text_is_active = not self.text_is_active
      self.text_toggled = False
      self.text_button_lifted = False
    elif not self.joystick_readings[0]["axes"]["right_trigger"] >= .05:
      self.text_button_lifted = True
    if not self.text_toggled:
      if self.text_is_active:
        for path in self.textNodePaths:
          self.textNodePaths[path].detachNode()
      else:
        for node in self.textNodes:
          self.textNodePaths[node] = self.aspect2d.attachNewNode(self.textNodes[node])
    return Task.cont

app = Simulator()
app.run()