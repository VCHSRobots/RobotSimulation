"""
graphs.py: Generates a graph image based off two related axes of data
6/27/2019 Holiday Pettijohn
"""

from PIL import Image, ImageDraw, ImageColor
from time import time
from collections import OrderedDict

class Graph:
  def __init__(self):
    """
    Super init for graph classes
    """
    
  def render(self):
    """
    Renders the graph's current geometry to self.image
    Returns points, strings, and locations required to draw the graph
    """

  def update(self, data):
    """
    Adds data to the graph
    """

class XYGraph(Graph):
  def __init__(self, name = "graph", location = (0, 0), graph_size = (.9, .9), x_range = (0, 10),
               y_range = (0, 10), x_axis_name = "Time", y_axis_name = "Value",
               buffer_size = .1, x_tick_space = 2, y_tick_space = 1, 
               line_color = (0, 0, 0, 255), edge_color = (0, 0, 0, 255), tick_color = (0, 0, 0, 255),
               label_color = (0, 0, 0, 255), background_color = (255, 255, 255, 100), tick_length = .1,
               number_spacing = .1, decimals = 1):
    #Reference name for use outside graph
    self.name = name
    #The location the graph will render on the screen
    self.location = location
    self.data = OrderedDict()
    self.size = graph_size
    #The number of x/y values to display on the graph
    self.x_range = x_range
    self.y_range = y_range
    #The displayed names of the axes
    self.x_axis_name = x_axis_name
    self.y_axis_name = y_axis_name
    #The size of the graph, without labels
    self.graph_size = graph_size
    #The size of the buffer which hangs to the left and bottom of the graph
    #This number is added to both dimensions in graph_size to create the actual resolution
    self.buffer_size = buffer_size
    self.resolution = graph_size[0]+buffer_size, graph_size[1]+buffer_size
    #Number of values between each tick on the graphs
    self.x_tick_space = x_tick_space
    self.y_tick_space = y_tick_space
    #Saves edge and tick locations since they are constant unless explicitly changed
    self.x_distance_per_value = 0
    self.y_distance_per_value = 0
    self.graph_origin = (self.location[0]+self.buffer_size, self.location[1]+self.buffer_size)
    self.edge_locations = self.calculateEdgeLocations()
    self.tick_locations = self.calculateTickLocations()
    #Colors in which the graph elements should be rendered
    self.line_color = line_color
    self.edge_color = edge_color
    self.tick_color = tick_color
    self.label_color = label_color
    self.background_color = background_color
    #Space between the graph and number labels in pixels
    self.number_spacing = number_spacing
    #Decimals to round numeric values to
    self.decimals = decimals
    #Start time
    self.start_time = time()
    #Length of each tick
    self.tick_length = tick_length
    #Each list within the points list is a line/polyline
    #Each tuple in the list is a point
    self.points = []
    #Strings are stored as (location, string) pairs
    self.strings = []

  def calculateEdgeLocations(self):
    """
    Calculates where the edge and ticks of the graph will be drawn
    """
    #Line locations for edges
    graph_origin = self.graph_origin
    edge_locations = [(graph_origin, (graph_origin[0], graph_origin[1]+self.graph_size[1])),
                      (graph_origin, (graph_origin[0]+self.graph_size[0], graph_origin[1]))]
    return edge_locations
  
  def calculateTickLocations(self):
    #TODO: Finish This
    #Starting points for x and y axis ticks, respectively
    tick_origin = self.graph_origin
    tick_locations = [[], []]
    #Finds how many x values are represented by the graph
    x_diff = self.x_range[1]-self.x_range[0]
    num_ticks = int(x_diff/self.x_tick_space)
    #Visual distance between graph unit
    self.x_distance_per_value = self.graph_size[0]/x_diff
    #Visual distance between each tick
    distance_per_tick = self.x_tick_space*self.x_distance_per_value
    print(num_ticks, self.x_tick_space, x_diff, self.x_distance_per_value, distance_per_tick)
    for num in range(1, num_ticks+1):
      tick_locations[0].append((tick_origin[0]+distance_per_tick*num, tick_origin[1]))
    #Finds how many x values are represented by the graph
    y_diff = self.y_range[1]-self.y_range[0]
    num_ticks = int(y_diff/self.y_tick_space)
    self.y_distance_per_value = self.graph_size[1]/y_diff
    #Visual distance between each tick
    distance_per_tick = self.y_tick_space*self.y_distance_per_value
    for num in range(1, num_ticks+1):
      tick_locations[1].append((tick_origin[0], tick_origin[1]+distance_per_tick*num))
    return tick_locations

  def render(self):
    """
    Renders the graph's current geometry to self.image
    Returns points, strings, and locations required to draw the graph
    """
    self.points = []
    self.strings = []
    current_time = time()
    self.clearImage()
    graph_start_time = self.findGraphStartTime(current_time)
    self.drawOutline(graph_start_time)
    self.plotData(graph_start_time)
    return self.points, self.strings

  def findGraphStartTime(self, current_time):
    best_time = current_time-(self.x_range[1]-self.x_range[0])
    if best_time-self.start_time < 0:
      best_time = self.start_time
    return best_time

  def peek(self, current_time):
    """
    Renders the graph's state at the given time
    """
    self.clearImage()
    graph_start_time = self.findGraphStartTime(current_time)
    self.drawOutline(graph_start_time)
    self.plotData(graph_start_time)

  def clearImage(self):
    """
    Returns the image to a blank state
    """
    self.points = []

  def drawOutline(self, graph_start_time):
    """
    Draws the graph's edges, ticks, and labels
    """
    self.drawEdges()
    self.drawTicks()
    self.drawLabels(graph_start_time)

  def drawEdges(self):
    """
    Draws the graph's edges
    """
    for line in self.edge_locations:
      self.points.append(line)

  def drawTicks(self):
    """
    Draws ticks on the graph
    """
    for x_tick in self.tick_locations[0]:
      self.points.append((x_tick, (x_tick[0], x_tick[1]-self.tick_length)))
    for y_tick in self.tick_locations[1]:
      self.points.append((y_tick, (y_tick[0]+self.tick_length, y_tick[1])))

  def drawLabels(self, graph_start_time):
    """
    Draws number labels and axis names on the graph
    """
    #TODO: Make a list of strings that need to be written to the graph in certain locations
    #Generates numeric labels for time and value
    #Adjusts the time values to make them more readable
    x_labels = frange(graph_start_time-self.start_time, graph_start_time+self.x_range[1]-self.start_time, self.x_tick_space)
    y_labels = frange(self.y_range[0], self.y_range[1], self.y_tick_space)
    for ind, x_tick_location in enumerate(self.tick_locations[0]):
      #TODO: Fix these formulas for draw location
      draw_location = x_tick_location[0], x_tick_location[1]-self.number_spacing
      self.strings.append((draw_location, str(round(x_labels[ind], self.decimals)+1)))
    for ind, y_tick_location in enumerate(self.tick_locations[1]):
      draw_location = y_tick_location[0]-self.number_spacing, y_tick_location[1]
      self.strings.append((draw_location, str(round(y_labels[ind], self.decimals)+1)))

  def plotData(self, graph_start_time):
    """
    Plots the graph's data
    """
    points = self.dataToPoints(graph_start_time)
    self.points.append(points)

  def dataToPoints(self, graph_start_time):
    """
    Converts data to Panda3D compatible points
    """
    points = []
    graph_shift = graph_start_time-self.start_time
    for x in self.data:
      if x < graph_start_time:
        continue
      y = self.data[x]
      #Transform x relative to time graph was created
      x -= self.start_time+graph_shift
      location = (x*self.x_distance_per_value+self.graph_origin[0],
                  y*self.y_distance_per_value+self.graph_origin[1])
      points.append(location)
    if len(points) == 1:
      new_point = self.propigateDataFromPoint(points, graph_start_time)
      x = new_point[0]-self.start_time-graph_shift
      y = new_point[1]
      points.insert(0, ((x*self.x_distance_per_value)+self.graph_origin[0], y*self.y_distance_per_value+self.graph_origin[1]))
    return points

  def propigateDataFromPoint(self, points, graph_start_time):
    """
    Finds the point which would intersect the line between given data point
    and last data point which is off the graph
    """
    data_time, data_point = points[0]
    if len(self.data.items()) >= 2:
      last_data_time, last_data_point = tuple(self.data.items())[-2]
    else:
      last_data_time, last_data_point = 0, 0
    delta_time = data_time-last_data_time
    slope = (data_point-last_data_point)/delta_time
    intersect = data_point-(slope*data_time)
    point_time = graph_start_time
    intersection_data_point = slope*point_time + intersect
    return (point_time, intersection_data_point)

  def update(self, y):
    """
    Creates a new datapoint at the current time with the given value
    """
    self.data[time()] = y 

class PolarGraph(Graph):
  def __init__(self):
    """
    Initiates a polar graph
    """

  def calculateCirclePoints(self):
    """
    Finds the location of the static lines used to draw the circle outline
    """

  def update(self, magnitude, direction):
    """
    Adds data to the graph
    """

def frange(x, y, jump = 1):
  """
  Floating point range function
  Returns a list as opposed to a generator
  """
  nums = []
  while x < y:
    nums.append(x)
    x += jump
  return nums
