"""
joy.py: Interface for getting joystick data
6/27/2019 Holiday Pettijohn
"""
from panda3d.core import InputDevice

buttons = ["a", "b", "x", "y", "rstick", "lstick"]

def readJoystickValues(joystick):
  axes_values = readAxesValues(joystick)
  button_values = readButtonValues(joystick)
  return {"axes": axes_values, "buttons": button_values}

def readAxesValues(joystick):
  values = {}
  names = ("left_x", "left_y", 
           "right_x", "right_y",
           "left_trigger", "right_trigger")
  axis_names = (InputDevice.Axis.left_x,
                InputDevice.Axis.left_y,
                InputDevice.Axis.right_x,
                InputDevice.Axis.right_y,
                InputDevice.Axis.left_trigger,
                InputDevice.Axis.right_trigger)
  for ind in range(len(names)):
    values[names[ind]] = joystick.findAxis(axis_names[ind]).value
  return values

def readButtonValues(joystick):
  values = {}
  for button in buttons:
    values[button] = joystick.findButton(button).pressed
  return values