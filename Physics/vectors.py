"""
vectors.py: Vector class for physics engine
7/1/2019 Holiday Pettijohn
"""

from math import sin, cos, sqrt, atan2

class Vector:
  def __init__(self, magnitude = None, direction = None, component = None):
    if component != None:
      #component should be a 2-tuple with X, Y component
      self.component = component
      self.magnitude = sqrt(component[0]**2 + component[1]**2)
      self.direction = atan2(component[1], component[0])
    elif magnitude != None and direction != None:
      self.magnitude = magnitude
      self.direction = direction
      self.component = magnitude*cos(direction), magnitude*sin(direction)
    else:
      raise TypeError("Insufficent Arguments Provided")

  def setMagnitude(self, magnitude):
    self.magnitude = magnitude
    self.updateComponent()

  def setDirection(self, direction):
    self.direction = direction
    self.updateComponent()

  def updateComponent(self):
    self.component = self.magnitude*cos(self.direction), self.magnitude*sin(self.direction)

  def __add__(self, vector):
    component = (self.component[0]+vector.component[0],
                 self.component[1]+vector.component[1])
    return Vector(component=component)

  def __sub__(self, vector):
    component = (self.component[0]-vector.component[0],
                 self.component[1]-vector.component[1])
    return Vector(component=component)
