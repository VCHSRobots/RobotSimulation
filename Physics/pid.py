"""
pid.py: Pid loops
6/27/2019 Holiday Pettijohn
"""
from time import time

class PID:
  def __init__(self, p, i, d, k=1):
    self.p = p
    self.i = i
    self.d = d
    self.k = k
    self.last_time = time()
    self.last_error = None
    self.integral = 0

  def update(self, error):
    t = time()
    if self.last_time != None:
      delta_time = t-self.last_time
    else:
      delta_time = None
    delta_error = error-self.last_error
    p = self.getP(error)
    d = self.getD(delta_error, delta_time)
    i = self.getI(delta_error, delta_time, d/self.d)
    self.last_error = error
    self.last_time = t
    return (p+i+d)*self.k

  def getP(self, error):
    return self.p*error

  def getI(self, delta_error, delta_time, derivitive):
    triangle = (delta_time*delta_error)/2
    box = self.last_error*delta_time
    self.integral += triangle+box
    return self.i*self.integral

  def getD(self, delta_error, delta_time):
    if delta_error != None:
      d = self.d*(delta_error)/(delta_time)
      return d
    else:
      return 0

  def tune(self, p=None, i=None, d=None):
    if p != None:
      self.p = p
    if i != None:
      self.i = i
    if d != None:
      self.d = d

  def resetI(self):
    self.integral = 0
