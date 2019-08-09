"""
app.py: The Panda3D app class which the robot simulator runs from
6/27/2019 Holiday Pettijohn
"""

from math import atan2, cos, pi, sin, sqrt

from direct.actor.Actor import Actor
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import Sequence
from direct.showbase.Loader import Loader
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (Geom, GeomLinestrips, GeomNode, GeomVertexData,
                          GeomVertexFormat, GeomVertexWriter, InputDevice,
                          LineSegs, Point3, TextNode, TransparencyAttrib)

import Input.joy as joy
import Physics.primitivePhysics as physics
import VisualAssets.graphs as graphs


class Simulator(ShowBase):
  def __init__(self, textboxes = ({}), default_text_scale = .07, graph_objs = {}):
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
    #Lines to be rendered on the next frame
    self.lines = []
    self.lineNodes = []
    self.lineNodePaths = []
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
    #Geometry drawing node
    self.geom_node = GeomNode("drawer")
    self.aspect2d.attach_new_node(self.geom_node)
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
    #Creates a graph of y vectors
    self.graphs = graph_objs
    #Adds dummy value to graph to prevent crash
    self.graphs["y_graph"].update(0)
    self.graphs["vector_graph"].update(0, 0)

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
    self.graphs["y_graph"].update(self.physics.velocities["frame"][1])
    magnitude = sqrt(x**2+y**2)
    direction = atan2(y, x)
    self.graphs["vector_graph"].update(magnitude, direction)
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

  def manageGeometry(self):
    """
    Manages geometry generation
    """
    #(Re)Renders all the lines which are in self.lines
    for line in self.lines:
      self.addLine(line)

  def addLine(self, points):
    """
    Adds a line to class GeomNode from a pair of points
    """
    #Creates objects needed to draw a geometry on the HUD
    #The vertex data which will define the rendered geometry
    vertex_data = GeomVertexData("graph", GeomVertexFormat.getV3(), Geom.UHStatic)
    #The object that writes vertexes the vertex data
    writer = GeomVertexWriter(vertex_data, "vertex")
    for point in points:
      writer.add_data3f(point[0], 0, point[1])
    #Defines that this geometry represents a polyline
    primitive = GeomLinestrips(Geom.UHStatic)
    #Tells geometry how many verticies will be added(?)
    primitive.add_consecutive_vertices(0, 2)
    primitive.close_primitive()
    geometry = Geom(vertex_data)
    geometry.add_primitive(primitive)
    #Draws a graph on the HUD
    self.geom_node.add_geom(geometry)

  def manageTextNodes(self):
    deleted = []
    for name in self.textboxes:
      if name not in self.textNodes:
        #If the name has not been given a textNode object, set it up
        self.textNodes[name] = TextNode(name)
        self.textNodePaths[name] = self.aspect2d.attachNewNode(self.textNodes[name])
    #Checks if any textNodes no longer have their respective textbox object and should be deleted
    for name in self.textNodes:
      if name not in self.textboxes:
        deleted.append(name)
    for node in deleted:
      self.textNodePaths[node].removeNode()
      self.textNodePaths.pop(node)
      self.textNodes.pop(node)
    
  def renderText(self):
    for name in self.textboxes:
      if "location" in self.textboxes[name]:
        location = self.textboxes[name]["location"]
      else:
        location = (0, 0)
      if "scale" in self.textboxes[name]:
        scale = self.textboxes[name]["scale"]
      else:
        scale = self.default_text_scale
      if "text" in self.textboxes[name]:
        self.textNodes[name].setText(self.textboxes[name]["text"])
      self.textNodePaths[name].setScale(scale)
      self.textNodePaths[name].setPos(location[0], 0, location[1])

  def toggleText(self, task):
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
app = Simulator(textboxes={"frvector_label": {}, "frvector_value": {"location": (.4, .7)}}, graph_objs = graphs)
app.run()
