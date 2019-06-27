"""
app.py: The Panda3D app class which the robot simulator runs from
6/27/2019 Holiday Pettijohn
"""

from math import pi, sin, cos, atan2, sqrt

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3, InputDevice

import Input.joy as joy

class Simulator(ShowBase):
  def __init__(self):
    ShowBase.__init__(self)

    self.joys = self.devices.getDevices(InputDevice.DeviceClass.gamepad)
    #Attaches input devices to base
    for ind, joy in enumerate(self.joys):
      self.attachInputDevice(joy, prefix=str(ind))
    #Joystick reading variable
    self.readings = []

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
    #Loop the animation to the one loaded in the dictionary
    self.pandaActor.loop("walk")
    self.taskMgr.add(self.updateJoysticks, "updateJoysticks")
    self.taskMgr.add(self.walkPanda, "walkPanda")

  def walkPanda(self, task):
    x = self.readings[0]["axes"]["left_x"]
    y = self.readings[0]["axes"]["left_y"]
    magnitude = sqrt(x**2+y**2)
    self.pandaLocation[0] += x/7
    self.pandaLocation[1] += y/7
    angle = atan2(y, x)*(180/pi)
    self.setPandaToLocation()
    if magnitude >= .05:
      self.pandaActor.setHpr(angle+90, 0, 0)
      if not self.pandaActor.getCurrentAnim() == "walk":
        self.pandaActor.loop("walk")
      else:
        self.pandaActor.setPlayRate(magnitude*2, "walk")
    else:
      if self.pandaActor.getCurrentAnim() == "walk":
        self.pandaActor.stop("walk")
    return Task.cont

  def setPandaToLocation(self):
    self.pandaActor.setPos(self.pandaLocation[0], self.pandaLocation[1], self.pandaLocation[2])

  def updateJoysticks(self, task):
    readings = []
    for joystick in self.joys:
      readings.append(joy.readJoystickValues(joystick))
    self.readings = readings
    return Task.cont

app = Simulator()
app.run()