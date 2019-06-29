"""
primitivePhysics.py: Simple version of swerve drive physics engine
6/27/2019 Holiday Pettijohn
"""

import json
from math import atan2, sqrt, sin, cos
from time import time

class Swerve:
  def __init__(self, start_position = (0, 0, 0)):
    #Position is x, y, direction
    self.position = list(start_position)
    #Swerve Wheel Target
    self.swerve_target = 0
    #Last update time - used for velocity motion calculations
    self.last_time = time()
    #Wheel encoders work in Panda grid units, which are assumed to be like meters
    #Swerve encoders work in radians
    self.encoders = {"frwheel": 0,
                     "brwheel": 0,
                     "flwheel": 0,
                     "blwheel": 0,
                     "frswerve": 0,
                     "brswerve": 0,
                     "flswerve": 0,
                     "blswerve": 0}
    #Vectors are stored as 2D [magnitude, radian] pairs
    self.vectors = {"frwheel": [0, 0],
                    "brwheel": [0, 0],
                    "flwheel": [0, 0],
                    "blwheel": [0, 0],
                    "frswerve": [0, 0],
                    "brswerve": [0, 0],
                    "flswerve": [0, 0],
                    "brswerve": [0, 0],
                    "frame": [0, 0]}
    self.motor_velocities = {"frwheel": 0,
                             "brwheel": 0,
                             "flwheel": 0,
                             "blwheel": 0,
                             "frswerve": 0,
                             "brswerve": 0,
                             "flswerve": 0,
                             "blswerve": 0}

  def update(self):
    """
    Calculates the effects of physics given the motor velocites and time passed
    """
    #TODO: Implement Friction
    t = time()
    delta_time = t-self.last_time
    self.last_time = t
    self.updateVectors()
    self.updatePositions(delta_time)

  def updateVectors(self):
    """
    Updates the vectors output by the motors
    """
    #Velocity (m/s) = amps*volts (watts) /robot_weight (newtons)
    #= newton*meter/second*newton = meter/second
    #TODO: Add equasions for swerve wheels
    #TODO: This equasion does not go through rpm, but simplifies the
    #motor's mechanics into an efficency power loss
    self.vectors["frwheel"] = [(params["voltage"]*params["max_current"]*self.motor_velocities["frwheel"])
                               *params["motor_efficency"]/params["robot_weight"],
                               self.encoders["frswerve"]]
    self.vectors["brwheel"] = [(params["voltage"]*params["max_current"]*self.motor_velocities["brwheel"])
                               *params["motor_efficency"]/params["robot_weight"],
                               self.encoders["brswerve"]]
    self.vectors["flwheel"] = [(params["voltage"]*params["max_current"]*self.motor_velocities["flwheel"])
                               *params["motor_efficency"]/params["robot_weight"],
                               self.encoders["flswerve"]]
    self.vectors["blwheel"] = [(params["voltage"]*params["max_current"]*self.motor_velocities["blwheel"])
                               *params["motor_efficency"]/params["robot_weight"],
                               self.encoders["blswerve"]]

  def updatePositions(self, delta_time):
    """
    Updates the wheel and robot positions based on vector data
    """
    #TODO: Account for each wheel rotating individually as opposed to
    #treating their forces as coming from robot's the center of gravity
    #Calculate robot position change
    #TODO: Account for robot rotation
    wheels = ["frwheel", "brwheel", "flwheel", "blwheel"]
    x = 0
    y = 0
    z = 0
    for wheel in wheels:
      x += delta_time*cos(self.vectors[wheel][1])*self.vectors[wheel][0]
      y += delta_time*sin(self.vectors[wheel][1])*self.vectors[wheel][0]
    self.position[0] += x
    self.position[1] += y

  def sendControls(self, x = 0, y = 0, z = 0):
    """
    Sets motor velocites based on the given controls
    """
    print("x = {} y = {} z = {}".format(x, y, z))
    magnitude = sqrt(x**2+y**2)
    direction = atan2(y, x)
    twist = z
    self.arcadeDrive(twist, magnitude)
    self.swerve_target = direction
    self.swerveWheels(direction)
  
  def arcadeDrive(self, x, y):
    self.motor_velocities["frwheel"] = y+x
    self.motor_velocities["brwheel"] = y+x
    self.motor_velocities["flwheel"] = y-x
    self.motor_velocities["blwheel"] = y-x

  def swerveWheels(self, direction):
    """
    Swerves wheels to a given direction
    """
    #TODO: This does not yet simulate the physics of turning the wheels
    self.encoders["frswerve"] = direction
    self.encoders["brswerve"] = direction
    self.encoders["flswerve"] = direction
    self.encoders["blswerve"] = direction

def loadParams():
  f = open("params.json")
  params = json.load(f)
  f.close()
  return params

params = loadParams()
