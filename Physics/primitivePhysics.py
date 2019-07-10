"""
primitivePhysics.py: Simple version of swerve drive physics engine
6/27/2019 Holiday Pettijohn
"""

import json
from math import atan2, sqrt, sin, cos, pi
from time import time

from Physics.vectors import Vector

class Swerve:
  def __init__(self, start_position = (0, 0, 0)):
    #Position is x, y, direction
    self.position = list(start_position)
    #Swerve Wheel Target
    self.swerve_target = 0
    #Last update time - used for velocity motion calculations
    self.last_time = time()
    #Wheel positions work in Panda grid units, which are assumed to be like meters
    #Swerve positions work in radians
    self.positions = {"frwheel": 0,
                     "brwheel": 0,
                     "flwheel": 0,
                     "blwheel": 0,
                     "frswerve": 0,
                     "brswerve": 0,
                     "flswerve": 0,
                     "blswerve": 0}
    #Vectors produced by motors or other robot-influenced forces
    #Vectors are stored in vector objects
    self.vectors = {"frwheel": Vector(0, 0),
                    "brwheel": Vector(0, 0),
                    "flwheel": Vector(0, 0),
                    "blwheel": Vector(0, 0),
                    "frswerve": Vector(0, 0),
                    "brswerve": Vector(0, 0),
                    "flswerve": Vector(0, 0),
                    "brswerve": Vector(0, 0),
                    "frame": Vector(0, 0)}
    #Resistance vectors which will not accelerate the robot in the opposite direction
    self.resistance_vectors = {"frwheel": Vector(0, 0),
                               "brwheel": Vector(0, 0),
                               "flwheel": Vector(0, 0),
                               "blwheel": Vector(0, 0),
                               "frswerve": Vector(0, 0),
                               "brswerve": Vector(0, 0),
                               "flswerve": Vector(0, 0),
                               "brswerve": Vector(0, 0),
                               "frame": Vector(0, 0)}
    self.wheel_vectors = {"frwheel": Vector(0, 0),
                          "brwheel": Vector(0, 0),
                          "flwheel": Vector(0, 0),
                          "blwheel": Vector(0, 0)}
    self.motor_velocities = {"frwheel": 0,
                             "brwheel": 0,
                             "flwheel": 0,
                             "blwheel": 0,
                             "frswerve": 0,
                             "brswerve": 0,
                             "flswerve": 0,
                             "blswerve": 0}
    self.z_acceleration = 0
    self.z_friction = 0
    self.z_friction = params["rolling_friction"]
    self.z_velocity = 0
    #Diagnostic variable for z acceleration
    self.delta_z_accel = {}
    self.velocities = {"frwheel": [0, 0],
                       "brwheel": [0, 0],
                       "flwheel": [0, 0],
                       "blwheel": [0, 0],
                       "frswerve": [0, 0],
                       "brswerve": [0, 0],
                       "flswerve": [0, 0],
                       "blswerve": [0, 0],
                       "frame": [0, 0]}

  def update(self):
    """
    Calculates the effects of physics given the motor velocites and time passed
    """
    #The frame's location is the only one tracked in the position variable
    #However, it is directly affected by the other components
    #TODO: Implement Friction
    t = time()
    delta_time = t-self.last_time
    self.last_time = t
    #Updates force vectors taking place on different parts of the robot
    self.updateVectors()
    #Updates the velocities at which the robot/parts should be traveling
    self.updateVelocities(delta_time)
    #Updates the positions of the robot
    self.updatePositions(delta_time)

  def updateVectors(self):
    """
    Updates the vectors output by the motors
    """
    #TODO: Account for swerve wheels
    #Functions are called in the order in which they transitively affect each other
    self.updateWheelVectors()
    self.updateWheelFrictionVectors()
    self.updateFrameVectors()
    self.updateFrameFrictionVectors()
    #self.vectorsUnitTest()

  def updateWheelVectors(self):
    """
    Updates vectors related to the wheel's drive forces
    """
    wheels = ["frwheel", "brwheel", "flwheel", "blwheel"]
    swerves = ["frswerve", "brswerve", "flswerve", "blswerve"]
    #TODO: This equasion does not go through rpm, but simplifies the
    #motor's mechanics into an efficency power loss
    #Velocity (m/s) = amps*volts (watts) /robot_weight (newtons)
    #= newton*meter/second*newton = meter/second
    for ind, wheel in enumerate(wheels):
      if self.motor_velocities[wheel] <= .05:
        self.vectors[wheel].setMagnitude(0)
        self.vectors[wheel].setDirection(0)
        continue
      self.vectors[wheel].setMagnitude(params["voltage"]*params["max_current"]*self.motor_velocities[wheel]
                                      *params["motor_efficency"]/params["robot_weight"])
      self.vectors[wheel].setDirection(self.positions[swerves[ind]])

  def updateWheelFrictionVectors(self):
    """
    Calculates rolling friction on wheels
    """
    coef = params["rolling_friction"]
    for component in self.vectors:
      self.resistance_vectors[component].setMagnitude(params["robot_weight"]/4*coef)
      self.resistance_vectors[component].setDirection(self.vectors[component].direction+pi)

  def updateFrameVectors(self):
    """
    Finds the total force being applied to the frame, sans friction
    """
    wheels = ["frwheel", "brwheel", "flwheel", "blwheel"]
    xy_force = Vector(0, 0)
    self.z_acceleration = 0
    #Calculates the effects of vectors in the x, y, and z direction
    for wheel in wheels:
      total_vector = self.vectors[wheel]#+self.resistance_vectors[wheel]
      delta_z_acceleration = total_vector.magnitude*sin(total_vector.direction-angles[wheel])*torques[wheel]
      self.delta_z_accel[wheel] = delta_z_acceleration
      self.z_acceleration += delta_z_acceleration
      wheel_vector = Vector(total_vector.magnitude*cos(total_vector.direction-angles[wheel]), angles[wheel])
      self.wheel_vectors[wheel] = wheel_vector
      xy_force += wheel_vector
    self.vectors["frame"] = xy_force

  def updateFrameFrictionVectors(self):
    """
    Finds the total friction the robot faces, based off its current velocity
    """
    swerves = ["frswerve", "brswerve", "flswerve", "blswerve"]
    #Calculate the total force being applied to the frame
    friction = Vector(0, 0)
    direction = atan2(self.velocities["frame"][1], self.velocities["frame"][0])-pi
    for swerve in swerves:
      coef = findFrictionCoef(self.positions[swerve]-self.vectors["frame"].direction)
      magnitude = coef*params["gravity"]*params["robot_weight"]/4
      friction += Vector(magnitude, direction)
    self.resistance_vectors["frame"] = friction
    #Calculate z axis friction
    if self.z_velocity > 0:
      self.z_friction = -params["gravity"]*params["robot_weight"]*params["rolling_friction"]/2
    elif self.z_velocity < 0:
      self.z_friction = params["gravity"]*params["robot_weight"]*params["rolling_friction"]/2
    else:
      self.z_friction = 0

  def vectorsUnitTest(self):
    """
    Unit test for wheel vector behavior
    """
    passing = "Failing"
    if self.delta_z_accel["frwheel"]+self.delta_z_accel["flwheel"]+self.delta_z_accel["brwheel"]+self.delta_z_accel["blwheel"] == 0:
      passing = "Passing"
    print("Unit Test {}".format(passing))
    print("frwheel: {} flwheel: {} brwheel: {} blwheel: {}".format(self.delta_z_accel["frwheel"], self.delta_z_accel["flwheel"], self.delta_z_accel["brwheel"], self.delta_z_accel["blwheel"]))
    print("Total Delta Z: {}".format(self.delta_z_accel["frwheel"]+self.delta_z_accel["flwheel"]+self.delta_z_accel["brwheel"]+self.delta_z_accel["blwheel"]))

  def updateVelocities(self, delta_time):
    self.updateWheelVelocities(delta_time)
    self.updateFrameVelocity(delta_time)
    self.velocityUnitTest(delta_time)

  def updateWheelVelocities(self, delta_time):
    wheels = ["frwheel", "brwheel", "flwheel", "blwheel"]
    for wheel in wheels:
      vector = self.vectors[wheel]+self.resistance_vectors[wheel]
      delta_x = vector.magnitude*delta_time*cos(self.vectors[wheel].direction)
      delta_y = vector.magnitude*delta_time*sin(self.vectors[wheel].direction)
      self.velocities[wheel][0] += delta_x
      self.velocities[wheel][1] += delta_y
      if self.vectors[wheel].magnitude < self.resistance_vectors[wheel].magnitude:
        if ((delta_x > 0 and self.velocities[wheel][0] > 0)
           or (delta_x < 0 and self.velocities[wheel][0] < 0)):
          self.velocities[wheel][0] = 0
        if ((delta_y > 0 and self.velocities[wheel][1] > 0)
           or (delta_y < 0 and self.velocities[wheel][1] < 0)):
          self.velocities[wheel][1] = 0

  def updateFrameVelocity(self, delta_time):
    total_vector = self.vectors["frame"]+self.resistance_vectors["frame"]
    delta_x = total_vector.magnitude*cos(total_vector.direction)*delta_time
    delta_y = total_vector.magnitude*sin(total_vector.direction)*delta_time
    #TODO: Update this to be based off accurate friction measurements
    delta_z = (self.z_acceleration+self.z_friction)*delta_time
    self.velocities["frame"][0] += delta_x
    self.velocities["frame"][1] += delta_y
    self.z_velocity += delta_z
    if self.vectors["frame"].magnitude < self.resistance_vectors["frame"].magnitude:
      #If the resistance vectors have taken over
      #only allow them to pull velocity towards zero
      if ((delta_x > 0 and self.velocities["frame"][0] > 0) or (delta_x < 0 and self.velocities["frame"][0] < 0)):
        self.velocities["frame"][0] = 0
      if ((delta_y > 0 and self.velocities["frame"][1] > 0) or (delta_y < 0 and self.velocities["frame"][1] < 0)):
        self.velocities["frame"][1] = 0
    if abs(self.z_acceleration) < abs(self.z_friction):
      if (self.z_friction > 0 and self.z_velocity > 0) or (self.z_friction < 0 and self.z_velocity < 0):
        self.z_velocity = 0
    #print("z_velocity: {}\nz_acceleration: {}\nz_friction: {}\ndelta_z: {}".format(self.z_velocity, self.z_acceleration, self.z_friction, delta_z))

  def velocityUnitTest(self, delta_time):
    """
    Checks if velocity calculations are working
    Current unused
    """

  def updatePositions(self, delta_time):
    """
    Updates the wheel and robot positions based on vector data
    """
    #TODO: Account for each wheel rotating individually as opposed to
    #treating their forces as coming from robot's the center of gravity
    #Calculate robot position change
    self.position[0] += self.velocities["frame"][0]*delta_time
    self.position[1] += self.velocities["frame"][1]*delta_time
    self.position[2] += self.z_velocity*delta_time

  def sendControls(self, x = 0, y = 0, z = 0, rnd = 2):
    """
    Sets motor velocites based on the given controls
    Rounds controls to the (rnd) decimal to prevent noise problems
    """
    x = round(x, rnd)
    y = round(y, rnd)
    z = round(z, rnd)
    #print("x = {} y = {} z = {}".format(x, y, z))
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
    self.positions["frswerve"] = direction
    self.positions["brswerve"] = direction
    self.positions["flswerve"] = direction
    self.positions["blswerve"] = direction

def loadParams():
  f = open("Physics\params.json")
  params = json.load(f)
  f.close()
  return params

def findFrictionCoef(angle):
  """
  Finds the coefficent of friction the robot's wheels will encounter based on the angle at which they are being dragged
  """
  #TODO: Find correct model for this measurement
  #angle is the angle between the dragging force and wheel direction
  #pi/2 radians = straight
  #How far the angle is from being straight
  # offset = abs((pi/2)-(angle%pi))/(pi/2)
  # #Difference between the rolling and skiding wheel coefficents
  # diff_of_coef = params["wheel_skid_friction"]-params["rolling_friction"]
  # coef = params["rolling_friction"]+(diff_of_coef*offset)
  return params["rolling_friction"]


params = loadParams()
#Wheel distances from robot center of gravity
#Used for calculating robot spin
#TODO: Fix these distance formulas
torques = {"frwheel": (sqrt((params["wheel_offset_x"]/2-params["cgoffset_x"])**2
                       + (params["wheel_offset_y"]/2-params["cgoffset_y"])**2)),
           "brwheel": (sqrt((params["wheel_offset_x"]/2-params["cgoffset_x"])**2
                       + (params["wheel_offset_y"]/2+params["cgoffset_y"])**2)),
           "flwheel": (-sqrt((params["wheel_offset_x"]/2+params["cgoffset_x"])**2
                       + (params["wheel_offset_y"]/2-params["cgoffset_y"])**2)),
           "blwheel": (-sqrt((params["wheel_offset_x"]/2+params["cgoffset_x"])**2
                       + (params["wheel_offset_y"]/2+params["cgoffset_y"])**2))}
#Cartesian distances from center of gravity
frdist = (params["wheel_offset_x"]/2-params["cgoffset_x"],
          params["wheel_offset_y"]/2-params["cgoffset_y"])
brdist = (params["wheel_offset_x"]/2-params["cgoffset_x"],
          -(params["wheel_offset_y"]/2+params["cgoffset_y"]))
fldist = (-(params["wheel_offset_x"]/2+params["cgoffset_x"]),
          params["wheel_offset_y"]/2-params["cgoffset_y"])
bldist = (-(params["wheel_offset_x"]/2+params["cgoffset_x"]),
          -(params["wheel_offset_y"]/2+params["cgoffset_y"]))
#Angles of the lines propigated between the center of gravity and wheel locations
#Angles should be the same between diagonally aligned wheels
#since their forces both should be transposed on the same vectors
angles = {"frwheel": atan2(frdist[1], frdist[0]),
          "brwheel": atan2(fldist[1], fldist[0]),
          "flwheel": atan2(fldist[1], fldist[0]),
          "blwheel": atan2(frdist[1], frdist[0])}
