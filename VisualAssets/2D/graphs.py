"""
graphs.py: Generates a graph image based off two related axes of data
6/27/2019 Holiday Pettijohn
"""

from PIL import Image, ImageDraw, ImageColor
from time import time
from collections import OrderedDict
from io import BytesIO

class Graph:
  def __init__(self, graph_size = (400, 400), x_range = (0, 10),
               y_range = (0, 10), x_axis_name = "Time", y_axis_name = "Value",
               buffer_size = 40, x_ticks = 1, y_ticks = 1, 
               line_color = (0, 0, 0, 255), edge_color = (0, 0, 0, 255), tick_color = (0, 0, 0, 255),
               label_color = (0, 0, 0, 255), background_color = (255, 255, 255, 100), tick_length = 4,
               number_spacing = 14, decimals = 1, last_value_offset = 1):
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
    #The offset of where the last value is displayed from the edge of the graph, in scaled seconds
    self.last_value_offset = last_value_offset
    #Number of values between each tick on the graphs
    self.x_ticks = x_ticks
    self.y_ticks = y_ticks
    #Saves edge and tick locations since they are constant unless explicitly changed
    self.x_pixels_per_value = 0
    self.y_pixels_per_value = 0
    self.edge_locations, self.tick_locations = self.calculateOutlineLocations()
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
    self.image = Image.new("RGBA", self.resolution, (0, 0, 0, 0))
    self.draw = ImageDraw.Draw(self.image)

  def calculateOutlineLocations(self):
    """
    Calculates where the edge and ticks of the graph will be drawn
    """
    #Line locations for edges
    edge_locations = [((self.buffer_size, 0), (self.buffer_size, self.graph_size[1])),
                      ((self.buffer_size, self.graph_size[1]), (self.resolution[0]-1, self.graph_size[1]))]
    #Starting points for x and y axis ticks, respectively
    tick_locations = [[], []]
    #The number of values between the x range parameters
    x_range_diff = self.x_range[1]-self.x_range[0]
    #The number of ticks to be plotted on the graph
    num_ticks = int(x_range_diff/self.x_ticks)
    pixels_per_value = self.graph_size[0]/x_range_diff
    self.x_pixels_per_value = pixels_per_value
    #Pixels between each tick
    tick_interval = self.x_ticks*pixels_per_value
    for tick_x in range(num_ticks):
      tick_locations[0].append((self.buffer_size+int(tick_x*tick_interval), self.graph_size[1]))
    y_range_diff = self.y_range[1]-self.y_range[0]
    num_ticks = int(y_range_diff/self.y_ticks)
    pixels_per_value = self.graph_size[1]/y_range_diff
    self.y_pixels_per_value = pixels_per_value
    tick_interval = self.y_ticks*pixels_per_value
    for tick_y in range(num_ticks):
      tick_locations[1].append((self.buffer_size, self.graph_size[1]-int(tick_y*tick_interval)))
    return edge_locations, tick_locations

  def saveImage(self, name = "image.png"):
    """
    Saves the current image to the given file name
    Returns the name of the image file saved
    """
    self.image.save(name)
    return name

  def bufferSave(self):
    """
    Saves the current image to an io buffer
    """
    buff = BytesIO()
    self.image.save(buff, format="png")
    return buff

  def render(self):
    """
    Renders the graph's current geometry to self.image
    Returns the current image
    """
    current_time = time()
    self.clearImage()
    graph_start_time = self.findGraphStartTime(current_time)
    self.drawOutline(graph_start_time)
    self.plotData(graph_start_time)
    self.saveImage()
    return self.image

  def findGraphStartTime(self, current_time):
    best_time = current_time-(self.x_range[1]-self.x_range[0])+self.last_value_offset
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
    self.draw.rectangle([(0, 0), (self.resolution[0], self.resolution[1])], fill = (0, 0, 0, 0))

  def drawOutline(self, graph_start_time):
    """
    Draws the graph's edges, ticks, and labels
    """
    self.drawBackground()
    self.drawEdges()
    self.drawTicks()
    self.drawLabels(graph_start_time)

  def drawBackground(self):
    """
    Draws the background of the image
    """
    self.draw.rectangle([(0, 0), (self.resolution[0], self.resolution[1])], fill = self.background_color)

  def drawEdges(self):
    """
    Draws the graph's edges
    """
    for line in self.edge_locations:
      self.draw.line(line, fill=self.edge_color)

  def drawTicks(self):
    """
    Draws ticks on the graph
    """
    for x_tick in self.tick_locations[0]:
      self.draw.line((x_tick, (x_tick[0], x_tick[1]-self.tick_length)), fill=self.tick_color)
    for y_tick in self.tick_locations[1]:
      self.draw.line((y_tick, (y_tick[0]+self.tick_length, y_tick[1])), fill=self.tick_color)

  def drawLabels(self, graph_start_time):
    """
    Draws number labels and axis names on the graph
    """
    self.draw.multiline_text((self.buffer_size/4, self.resolution[1]/3), makeVertical(self.y_axis_name), fill=self.label_color)
    self.draw.text((self.buffer_size+self.graph_size[0]/3, self.resolution[1]-self.buffer_size/4), self.x_axis_name, fill=self.label_color)
    #Generates numeric labels for time and value
    #Adjusts the time values to make them more readable
    x_labels = frange(graph_start_time-self.start_time, graph_start_time+self.x_range[1]-self.start_time, self.x_ticks)
    y_labels = frange(self.y_range[0], self.y_range[1], self.y_ticks)
    for ind, x_tick_location in enumerate(self.tick_locations[0]):
      draw_location = x_tick_location[0], x_tick_location[1]+self.number_spacing
      self.draw.text(draw_location, str(round(x_labels[ind], self.decimals)), fill=self.label_color)
    for ind, y_tick_location in enumerate(self.tick_locations[1]):
      draw_location = y_tick_location[0]-self.number_spacing, y_tick_location[1]
      self.draw.text(draw_location, str(round(y_labels[ind], self.decimals)), fill=self.label_color)

  def plotData(self, graph_start_time):
    """
    Plots the graph's data
    """
    points = self.dataToPoints(graph_start_time)
    self.draw.line(points, fill=self.line_color)

  def dataToPoints(self, graph_start_time):
    """
    Converts data to PIL compatible points
    """
    points = []
    graph_shift = graph_start_time-self.start_time
    for x in self.data:
      if x < graph_start_time:
        continue
      y = self.data[x]
      #Transform x relative to time graph was created
      x -= self.start_time+graph_shift
      points.append(((x*self.x_pixels_per_value)+self.buffer_size, -(y-self.y_range[1])*self.y_pixels_per_value))
    if len(points) == 1:
      new_point = self.propigateDataFromPoint(points, graph_start_time)
      x = new_point[0]-self.start_time-graph_shift
      y = new_point[1]
      points.insert(0, ((x*self.x_pixels_per_value)+self.buffer_size, -(y-self.y_range[1])*self.y_pixels_per_value))
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
