"""
physics.py: Physics calculator for swerve drive
6/27/2019 Holiday Pettijohn
"""

import json
from math import atan2, sqrt
from time import time

import pid

params = loadParams()

class Swerve:
  def __init__(self, start_position = (0, 0, 0)):
    #Position is x, y, direction
    self.position = list(start_position)
    #Swerve Wheel Target
    self.swerve_target = 0
    #Last update time - used for velocity motion calculations
    self.last_time = time()
    #Swerve Wheel PID
    self.swerve_pid = pid.PID(params["swerve_p"], params["swerve_i"], params["swerve_d"])
    #TODO: Velocity PID
    #Wheel encoders work in Panda grid units
    #Swerve encoders work in radians
    self.encoders = {"frwheel": 0,
                     "brwheel": 0,
                     "flwheel": 0,
                     "blwheel": 0,
                     "frswerve": 0,
                     "brswerve": 0,
                     "flswerve": 0,
                     "brswerve": 0}
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
                             "brswerve": 0}

  def update(self):
    """
    Calculates the effects of physics given the motor velocites and time passed
    """
    t = time()
    delta_time = t-self.last_time
    self.last_time = t
    wheel_power = params["voltage"]*params["max_current"]
    frswerve_motor_velocity = (wheel_power*self.motor_velocities["frswerve"])/params["robot_weight"]
    brswerve_motor_velocity = (wheel_power*self.motor_velocities["brswerve"])/params["robot_weight"]
    flswerve_motor_velocity = (wheel_power*self.motor_velocities["flswerve"])/params["robot_weight"]
    blswerve_motor_velocity = (wheel_power*self.motor_velocities["blswerve"])/params["robot_weight"]
    self.encoders["frswerve"] += frswerve_motor_velocity*delta_time
    self.encoders["brswerve"] += brswerve_motor_velocity*delta_time
    self.encoders["flswerve"] += flswerve_motor_velocity*delta_time
    self.encoders["blswerve"] += blswerve_motor_velocity*delta_time

  def sendControls(self, x, y, z):
    """
    Sets motor velocites based on the given controls
    """
    magnitude = sqrt(x**2+y**2)
    direction = atan2(y, x)
    twist = z
    self.arcadeDrive(twist, magnitude)
    self.swerve_target = direction
    self.swerveWheelsTo(direction)
  
  def arcadeDrive(self, x, y):
    right = x+y
    left = x-y
    self.motor_velocities["frwheel"] = right
    self.motor_velocities["brwheel"] = right
    self.motor_velocities["flwheel"] = left
    self.motor_velocities["blwheel"] = left

  def swerveWheelsTo(self, direction):
    """
    Uses a pid loop to swerve wheels to a certain position
    """
    motors = ["frswerve", "brswerve", "flswerve", "blswerve"]
    velocity = self.swerve_pid.update(error = self.swerve_target-self.encoders["frswerve"])
    for motor in motors:
      self.motor_velocities[motor] = velocity

def loadParams():
  f = open("params.json")
  params = json.load(f)
  f.close()
  return params
