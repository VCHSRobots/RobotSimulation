"""
graphs.py: Generates a graph image based off two related axes of data
6/27/2019 Holiday Pettijohn
"""

from collections import OrderedDict
from math import ceil, cos, floor, log, pi, sin, sqrt
from time import time

from PIL import Image, ImageColor, ImageDraw


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

  def dummyUpdate(self):
    """
    Dummy update to prevent crash due to no data
    """

class XYGraph(Graph):
  def __init__(self, name = "graph", location = (0, 0), graph_size = (.9, .9),
               x_tick_space = 2, ideal_num_ticks = 8, ideal_tick_buffer = .1,
               x_range = 10, x_axis_name = "Time", y_axis_name = "Value",
               buffer_size = .1, tick_length = .1, number_spacing = .1,
               decimals = 1, data_edge_buffer = .1):
    #Reference name for use outside graph
    self.name = name
    #The location the graph will render on the screen
    self.location = location
    self.data = OrderedDict()
    self.size = graph_size
    #The number of x/y values to display on the graph
    self.x_range = x_range
    #The displayed names of the axes
    self.x_axis_name = x_axis_name
    self.y_axis_name = y_axis_name
    #The size of the graph, without labels
    self.graph_size = graph_size
    #The size of the buffer which hangs to the left and bottom of the graph
    #This number is added to both dimensions in graph_size to create the actual resolution
    self.buffer_size = buffer_size
    self.resolution = graph_size[0]+buffer_size, graph_size[1]+buffer_size
    #Number of values between each tick on the x axis
    self.x_tick_space = x_tick_space
    #The ideal tick number on the y axis, since it is dynamic
    self.ideal_num_ticks = ideal_num_ticks
    #The ideal buffer from the bottom and top of the screen
    #A percentage of the max/min data values which change based on input
    self.ideal_tick_buffer = ideal_tick_buffer
    #Saves visual distance between each graph unit
    self.x_distance_per_value = self.graph_size[0]/self.x_range
    #This will be defined by the dynamic tick creator
    self.y_distance_per_value = 0
    #Distance kept between the edge of the graph and the data, as a percentange of the data's value
    self.data_edge_buffer = data_edge_buffer
    self.graph_origin = (self.location[0]+self.buffer_size, self.location[1]+self.buffer_size)
    self.edge_locations = self.calculateEdgeLocations()
    self.x_tick_locations = self.calculateXTickLocations()
    #Space between the graph and number labels in pixels
    self.number_spacing = number_spacing
    #Decimals to round numeric values to
    self.decimals = decimals
    #Start time
    self.start_time = time()
    #Length of each tick
    self.tick_length = tick_length
    #Each list within the points list is a line/polyline
    #Each tuple in the nested list is a point
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
  
  def calculateXTickLocations(self):
    """
    Finds where each x tick is located
    These values are static, and this function only called once
    """
    tick_origin = self.graph_origin
    tick_locations = []
    #X ticks move at a linear rate
    #Finds how many x values are represented by the graph
    num_ticks = int(self.x_range/self.x_tick_space)
    #Visual distance between each tick
    distance_per_tick = self.x_tick_space*self.x_distance_per_value
    #Adds tick locations to list
    for num in range(1, num_ticks+1):
      tick_locations.append((tick_origin[0]+distance_per_tick*num, tick_origin[1]))
    return tick_locations

  def placeYTicks(self, data_values):
    """
    Calculates the y tick locations and values
    """
    tick_origin = self.graph_origin
    tick_locations = []
    #Finds how many y values are represented by the graph
    rough_y_max, rough_y_min = max(data_values), min(data_values)
    #Finds tick numbers and intervals which are intuitive and closest to the desired number of ticks
    y_max, y_min, tick_interval, num_ticks, scale = self.getTickInterval(rough_y_max, rough_y_min)
    y_range = y_max-y_min
    if y_range == 0:
      y_range = .00001
    #Visual distance per grid value
    self.y_distance_per_value = self.graph_size[1]/y_range
    #Visual distance between each tick
    distance_per_tick = tick_interval*self.y_distance_per_value
    #Calculates tick locations
    for num in range(num_ticks):
      tick_locations.append((tick_origin[0], tick_origin[1]+distance_per_tick*num))
    tick_values = frange(y_min, y_max+tick_interval, tick_interval)
    return tick_locations, tick_values, y_range, scale

  def getTickInterval(self, rough_max, rough_min):
    """
    Finds a good distance between each graph tick
    """
    rough_range = abs(rough_max-rough_min)
    #Finds about how large/small the scale of the graph should be
    if -.001 <= rough_range <= .001:
      rough_range = 1
    #print("rough_range: {} rough_max: {} rough_min: {}".format(rough_range, rough_max, rough_min))
    scale = log(rough_range, 10)
    #Determines if scale is indecicive enough to check it rounded both up and down
    #This feature may be removed for efficency
    if .2 < scale%1 < .8:
      choices = []
      for scale in (floor(scale), ceil(scale)):
        choices.append(self.getTickIntervalAtScale(rough_max, rough_min, scale))
      if choices[0][4] < choices[1][4]:
        real_max, real_min, best_interval, num_ticks, _, scale = choices[0]
      else:
        real_max, real_min, best_interval, num_ticks, _, scale = choices[1]
    else:
      real_max, real_min, best_interval, num_ticks, _, scale = self.getTickIntervalAtScale(rough_max, rough_min, round(scale))
    return real_max, real_min, best_interval, floor(num_ticks), scale

  def getTickIntervalAtScale(self, rough_max, rough_min, scale):
    """
    Finds the best interval to use with the given scale
    """
    intervals = (1*10**scale, 2*10**scale, 5*10**scale)
    choices = []
    deltas = []
    for interval in intervals:
      interval_max, interval_min = (rough_max//interval+1)*interval, (rough_min//interval-1)*interval
      interval_range = interval_max-interval_min
      num_ticks = (interval_range/interval)+1
      #Difference betweeen ideal number of ticks and number proposed by interval
      #TODO: Adjust these equasions to adjust the weight of delta buffer and tick num
      delta_tick_num_weight = 7
      delta_buffer_weight = .4
      delta_tick_num = abs(self.ideal_num_ticks-num_ticks)
      delta_buffer = (abs((interval_max-rough_max)-(rough_max*(1+self.ideal_tick_buffer))
                     +abs((rough_min-interval_min)-(rough_min*(1-self.ideal_tick_buffer)))))
      choices.append((interval_max, interval_min, interval, num_ticks))
      deltas.append(delta_tick_num*delta_tick_num_weight+delta_buffer*delta_buffer_weight)
    choice_ind = deltas.index(min(deltas))
    real_max, real_min, interval, num_ticks = choices[choice_ind]
    return real_max, real_min, interval, num_ticks, min(deltas), scale

  def render(self):
    """
    Renders the graph's current geometry to self.image
    Returns points, strings, and locations required to draw the graph
    """
    current_time = time()
    self.clearImage()
    graph_start_time = self.findGraphStartTime(current_time)
    #Draws the static parts of the graph, i.e. names, edges
    self.drawOutline(graph_start_time)
    data = self.getReleventData(graph_start_time)
    data_values = self.getReleventData(graph_start_time).values()
    y_tick_locations, y_tick_values, y_tick_range, scale = self.placeYTicks(data_values)
    self.drawStaticLabels()
    self.drawTicks(graph_start_time, y_tick_locations, y_tick_values, scale)
    self.plotData(data, graph_start_time, y_tick_range, tick_min=min(y_tick_values))
    return self.points, self.strings
  
  def peek(self, current_time):
    """
    Renders the graph's state at the given time
    """
    self.clearImage()
    graph_start_time = self.findGraphStartTime(current_time)
    #Draws the static parts of the graph, i.e. names, edges
    self.drawOutline(graph_start_time)
    data = self.getReleventData(graph_start_time)
    data_values = self.getReleventData(graph_start_time).values()
    y_tick_locations, y_tick_values, y_tick_range, scale = self.placeYTicks(data_values)
    self.drawStaticLabels()
    self.drawTicks(graph_start_time, y_tick_locations, y_tick_values, scale)
    self.plotData(data, graph_start_time, y_tick_range, tick_min=min(y_tick_values))
    return self.points, self.strings

  def findGraphStartTime(self, current_time):
    best_time = current_time-(self.x_range)
    if best_time-self.start_time < 0:
      best_time = self.start_time
    return best_time

  def getReleventData(self, graph_start_time):
    relevant_data = {}
    for time in self.data:
      if time >= graph_start_time:
        relevant_data[time] = self.data[time]
    return relevant_data

  def clearImage(self):
    """
    Returns the image to a blank state
    """
    self.points = []
    self.strings = []

  def drawOutline(self, graph_start_time):
    """
    Draws the graph's edges, ticks, and labels
    """
    self.drawEdges()
    self.drawStaticLabels()

  def drawEdges(self):
    """
    Draws the graph's edges
    """
    for line in self.edge_locations:
      self.points.append(line)

  def drawTicks(self, graph_start_time, y_tick_locations, y_tick_values, scale):
    """
    Draws ticks on the graph
    """
    self.drawTickMarks(y_tick_locations)
    self.drawTickLabels(graph_start_time, y_tick_locations, y_tick_values, scale)

  def drawTickMarks(self, y_tick_locations):
    """
    Draws tick marks
    """
    for x_tick in self.x_tick_locations:
      self.points.append((x_tick, (x_tick[0], x_tick[1]+self.tick_length)))
    for y_tick in y_tick_locations:
      self.points.append((y_tick, (y_tick[0]+self.tick_length, y_tick[1])))

  def drawTickLabels(self, graph_start_time, y_tick_locations, y_labels, scale):
    """
    Draws labels near the tick marks
    """
    #Generates x time values
    x_labels = frange(graph_start_time-self.start_time, graph_start_time+self.x_range-self.start_time, self.x_tick_space)
    for ind, x_tick_location in enumerate(self.x_tick_locations):
      #TODO: Fix these formulas for draw location
      draw_location = x_tick_location[0], x_tick_location[1]-self.number_spacing
      self.strings.append((draw_location, str(round(x_labels[ind], self.decimals)+1)))
    for ind, y_tick_location in enumerate(y_tick_locations):
      draw_location = y_tick_location[0]-(self.number_spacing*2), y_tick_location[1]
      if -1 < scale < 4:
        #If scale is within a range which will not cause numbers to be too big
        #show it without any transformation
        string = str(round(y_labels[ind]))
      else:
        #otherwise, show it in scientific notation
        string = str(round(y_labels[ind]/10**scale))+"E{}".format(scale)
      self.strings.append((draw_location, string))

  def drawStaticLabels(self):
    """
    Draws text labels which do not change dynamiclly
    """
    #Adds graph name tags
    self.strings.append(((self.graph_origin[0]+self.buffer_size*2, self.graph_origin[1]+self.graph_size[1]*1.2), self.name))
    #Adds axis tags
    self.strings.append(((self.graph_origin[0]-self.buffer_size*2.7, self.graph_origin[1]+self.graph_size[1]/1.5), makeVertical(self.y_axis_name)))
    self.strings.append(((self.graph_origin[0]+self.graph_size[0]/2, self.graph_origin[1]-self.buffer_size*2), self.x_axis_name))

  def plotData(self, data, graph_start_time, y_tick_range, tick_min):
    """
    Plots the graph's data
    """
    points = self.dataToPoints(data, graph_start_time, y_tick_range, tick_min)
    self.points.append(points)

  def dataToPoints(self, data, graph_start_time, y_tick_range, tick_min):
    """
    Converts data to Panda3D compatible points
    """
    points = []
    graph_shift = graph_start_time-self.start_time
    for x in data:
      y = (data[x]-tick_min)#/y_tick_range
      #Transform x relative to time graph was created
      x -= self.start_time+graph_shift
      location = (x*self.x_distance_per_value+self.graph_origin[0],
                  y*self.y_distance_per_value+self.graph_origin[1])
      points.append(location)
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
    #TODO: Keep this from being a memory leak
    self.data[time()] = y

  def dummyUpdate(self):
    self.data[time()] = 0

class PolarGraph(Graph):
  def __init__(self, name = "graph", location = (0, 0), points_per_circle = 40,
               radius = .3, magnitude_range = 1.2, magnitude_axis_name = "Magnitude",
               directional_axis_name = "Rotation", buffer_size = .04,
               magnitude_tick_space = .4, directional_tick_space = pi/8, tick_length = .1,
               number_spacing = .1, decimals = 1, dynamic_magnitude_ticks = False):
    """
    Initiates a polar graph
    """
    #Polar graphs only render one piece of data at a time
    #Reference name for use outside graph
    self.name = name
    #The location the graph will render on the screen
    self.location = location
    self.data = (0, 0)
    #The maximum magnitude
    self.magnitude_range = magnitude_range
    #The displayed names of the axes
    self.magnitude_axis_name = magnitude_axis_name
    self.directional_axis_name = directional_axis_name
    #The size of the graph, without labels
    self.radius = radius
    #The size of the buffer which hangs to the left and bottom of the graph
    #This number is added to both dimensions in graph_size to create the actual resolution
    self.buffer_size = buffer_size
    #Number of values between each tick on the graphs
    self.magnitude_tick_space = magnitude_tick_space
    self.directional_tick_space = directional_tick_space
    #Whether magnitude ticks will be generated dynamically or not
    self.dynamic_magnitude_ticks = dynamic_magnitude_ticks
    #The radii of each of the different magnitude ticks
    self.magnitude_tick_radii = []
    #Screen distance units per graph value
    self.distance_per_value = 0
    self.points_per_circle = points_per_circle
    self.origin = self.location
    if not dynamic_magnitude_ticks:
      self.magnitude_ticks = self.calculateStaticMagnitudeTickLocations()
    self.edge_locations, self.angular_tick_locations = self.calculateOutlineLocations()
    #Space between the graph and number labels in pixels
    self.number_spacing = number_spacing
    #Decimals to round numeric values to
    self.decimals = decimals
    #Start time
    self.start_time = time()
    #Length of each tick
    self.tick_length = tick_length
    #Each list within the points list is a line/polyline
    #Each tuple in the nested list is a point
    self.points = []
    #Strings are stored as (location, string) pairs
    self.strings = []

  def calculateOutlineLocations(self):
    """
    Finds the location of the static lines and ticks used to draw the circle outline
    """
    edge_location = calculateCirclePoints(self.radius, self.points_per_circle, self.origin)
    angular_tick_locations = self.calculateAngularTickLocations()
    return edge_location, angular_tick_locations

  def calculateAngularTickLocations(self):
    """
    Finds the location of non-dynamic angular tick marks
    """
    ticks = []
    angles = frange(0, 2*pi, self.directional_tick_space)
    for angle in angles:
      ticks.append((((self.origin[0]-self.radius*cos(angle)), (self.origin[1]-self.radius*sin(angle))),
                   ((self.origin[0]+self.radius*cos(angle)), (self.origin[1]+self.radius*sin(angle)))))
    return ticks

  def calculateStaticMagnitudeTickLocations(self):
    """
    Calculates magnitude tick ring locations
    """
    locations = []
    self.distance_per_value = self.radius/self.magnitude_range
    #Magnitude tick radii in graph values
    self.magnitude_tick_radii = frange(self.magnitude_tick_space,
                                       self.magnitude_range,
                                       self.magnitude_tick_space)
    for radius in self.magnitude_tick_radii:
      locations.append(calculateCirclePoints(radius*self.distance_per_value, self.points_per_circle, self.origin))
    return locations
  
  def calculateDynamicMagnitudeTickLocations(self):
    """
    Calculates magnitude tick ring locations dynamically
    Not yet implemented, possibly not needed
    """

  def render(self):
    """
    Renders the graph
    """
    self.points = []
    self.strings = []
    self.drawOutline()
    self.drawTicks()
    self.drawLabels()
    self.plotData()
    return self.points, self.strings
    
  def drawOutline(self):
    """
    Draws the outline of the graph
    """
    self.points.append(self.edge_locations)
    self.points += self.angular_tick_locations

  def drawTicks(self, data = None):
    """
    Draws ticks
    """
    if self.dynamic_magnitude_ticks:
      raise NotImplementedError("Dynamic tick generation has not been implemented for polar graphs")
    else:
      self.points += self.magnitude_ticks
  
  def drawLabels(self):
    """
    Draws the axis names and tick labels
    """
    self.strings.append(((0, self.magnitude_range*self.distance_per_value+self.number_spacing*2), self.name))
    angular_labels, magnitude_labels = self.drawAngularLabels(), self.drawMagnitudeLabels()
    self.strings += angular_labels
    self.strings += magnitude_labels

  def drawAngularLabels(self):
    labels = []
    angles = frange(0, 2*pi, self.directional_tick_space)
    for angle in angles:
      labels.append((((self.radius+self.number_spacing)*cos(angle)+self.origin[0]-.07,
                      (self.radius+self.number_spacing)*sin(angle)+self.origin[1]-.04),
                      str(round(angle, self.decimals))))
    return labels

  def drawMagnitudeLabels(self):
    labels = []
    label_texts = frange(self.magnitude_tick_space,
                         self.magnitude_range,
                         self.magnitude_tick_space)
    for ind, radius in enumerate(self.magnitude_tick_radii):
      labels.append(((radius-self.number_spacing+self.origin[0], self.origin[1]), str(label_texts[ind])))
    return labels

  def plotData(self):
    """
    Draws the data vector
    """
    magnitude, direction = self.data
    data_point = [magnitude*cos(direction), magnitude*sin(direction)]
    data_point[0] *= self.distance_per_value
    data_point[1] *= self.distance_per_value
    data_point[0] += self.origin[0]
    data_point[1] += self.origin[1]
    self.points.append((self.origin, data_point))

  def update(self, magnitude, direction):
    """
    Adds data to the graph
    Since polar graphs only render one piece of data at a time
    This will override any former data in the graph
    """
    self.data = magnitude, direction

  def dummyUpdate(self):
    self.data = (0, 0)

def makeVertical(text):
  """
  Makes text print vertically by placing a newline between each character
  """
  vertical_text = text[0]
  for character in text[1:]:
    vertical_text += "\n"+character
  return vertical_text

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

def calculateCirclePoints(radius, num_points, origin = (0, 0)):
  points = []
  for angle in frange(0, 2*pi+(2*pi)/num_points, (2*pi)/num_points):
    points.append((radius*cos(angle)+origin[0], radius*(sin(angle))+origin[1]))
  return points
