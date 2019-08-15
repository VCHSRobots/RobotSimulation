# skid.py -- Draws arbitary skid marks 
# DLB 08-09-2019
#
from direct.showbase.ShowBase import ShowBase
import math
from math import pi, sin, cos
from direct.task import Task
from panda3d.core import PointLight 
from panda3d.core import VBase4
from panda3d.core import Geom
from panda3d.core import GeomNode
from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import GeomVertexWriter
from panda3d.core import GeomTriangles
from overlay import Overlay

class SkidTrack:
	"""
	SkidTrack class maintains skid marks that fade over time.  Maintian one instance of this class for
	each wheel that produces a skid mark.
	"""
	def __init__(self, nrects: int = 100, wheel_width=0.2, zpos=-0.38):
		"""
		Initalizes one track for a skid mark.  The mark will be placed parallel to X-Y in world coordinates.
		They will be placed at the given height given by 'zpos'.  The 'nrects' argument specifies how long
		the skid can be in input point locations.  You can make the skid mark longer by increasing nrects, or
		spreading out the distance between input points.  Once nrect points have been input, the earlier points
		will disappear.  The 'wheel-width' parameter is the thickness of the wheel that is producing the marks.
		"""
		self.wheel_width = wheel_width  # One unit = about 10 inches in current world.
		self.wheel_state = [] 	# Tupels of: X, Y position of wheel, While Direction in degrees, and force
		self.nrects = nrects
		self.zpos = zpos
		self.vdata = GeomVertexData("skid", GeomVertexFormat.getV3c4(), Geom.UHStatic)
		self.vdata.setNumRows(4*nrects)
		vtx = GeomVertexWriter(self.vdata,  "vertex")
		cx  = GeomVertexWriter(self.vdata,  "color")
		prim = GeomTriangles(Geom.UHStatic)
		c = self.forceToColor(0.0)
		# Here we set up all the vertexts and the primatives that use them.  For each set of four vertices, a
		# flat rectangle is defined. Then 4 primatives are defined by splitting up the rectangle into pair of 2
		# triangles -- 4 triangles per rectangle. Each pair of triangles are identical, except that their normals
		# are opposite, so that we don't have to worry about back culling later.  Although it would be possible
		# to share vertics between the rectangles we don't do that here so that the chain can be cut at any point
		# by only operating on the vertics and not visiting the primatives.  Finally, to "disable" a rectangle,
		# we set all the vertics to the same point in 3D space (and therefore create a zero-area rectangle).  
		for i in range(nrects):
			vtx.addData3f(0.0, 0.0, 0.0)
			vtx.addData3f(0.0, 0.0, 0.0)
			vtx.addData3f(0.0, 0.0, 0.0)
			vtx.addData3f(0.0, 0.0, 0.0)
			cx.addData4f(*c)
			cx.addData4f(*c)
			cx.addData4f(*c)
			cx.addData4f(*c)
			j = i * 4
			j0,j1,j2,j3 = j+0, j+1, j+2, j+3
			prim.addVertices(j0, j1, j3)
			prim.addVertices(j3, j1, j0)
			prim.addVertices(j0, j3, j2)
			prim.addVertices(j2, j3, j0)
		prim.closePrimitive()
		geom = Geom(self.vdata)
		geom.addPrimitive(prim)
		node = GeomNode('Skid')
		node.addGeom(geom)
		self.nodepath = render.attachNewNode(node)
		self.nextrect = 0
		self.havelast = False
		self.lastpoints = (0,0,0,0)

	def forceToColor(self, force):
		if force < 0.1:
			force = 0.1
		if force > 1.0:
			force = 1.0
		if force < 0.2:
			return (1, 1, 1, 1)
		w = 1.0 - force
		return(w, w, w, 1)

	def addPoint(self, x, y, wheel_dir, force):
		"""
		Adds a point to the skid mark trail.  The coordinates are in the world frame. The force is
		a number between zero and one, where one is the max force and makes the biggest and darkest
		skid mark.  The argument 'wheel_dir' is given in degrees, where zero points toward the
		positive X axis.
		"""
		h = self.wheel_width * 0.5
		rads = (wheel_dir-90) * math.pi / 180.0
		x0b, y0b = x + h*math.cos(rads), y + h*math.sin(rads)
		rads = (wheel_dir+90) * math.pi / 180.0
		x1b, y1b = x + h*math.cos(rads), y + h*math.sin(rads)
		x0a, y0a, x1a, y1a = self.lastpoints
		self.lastpoints = (x0b, y0b, x1b, y1b)
		if not self.havelast:
			self.havelast = True
			return
		indx = self.nextrect*4
		self.nextrect += 1
		if self.nextrect >= self.nrects:
			self.nextrect = 0
		vtx = GeomVertexWriter(self.vdata,  "vertex")
		cx  = GeomVertexWriter(self.vdata,  "color")
		vtx.setRow(indx)
		cx.setRow(indx)
		c = self.forceToColor(force)
		vtx.addData3f(x0a, y0a, self.zpos)
		vtx.addData3f(x1a, y1a, self.zpos)
		vtx.addData3f(x0b, y0b, self.zpos)
		vtx.addData3f(x1b, y1b, self.zpos)
		cx.addData4f(*c)
		cx.addData4f(*c)
		cx.addData4f(*c)
		cx.addData4f(*c)

class SkidTrackOld:
	"""
	First try at doing skid marks -- obsolete.
	"""
	def __init__(self, wheel_width):
		self.wheel_width = wheel_width  # One unit = about 10 inches in current world.
		self.wheel_state = [] 	# Tupels of: X, Y position of wheel, While Direction in degrees, and force
		self.nodepath = None

	def forceToColor(self, force):
		if force < 0.1:
			force = 0.1
		if force > 1.0:
			force = 1.0
		if force < 0.2:
			return (1, 1, 1, 1)
		w = 1.0 - force
		return(w, w, w, 1)

	def calWeight(self, x0, y0, x1, y1, angle_of_wheel):
		"""
		Returns a weight factor between zero and one depending on 
		the direction of wheel travel and the direction of skid motion.
		"""
		angle_of_wheel = math.fmod(angle_of_wheel, 360.0)
		if angle_of_wheel < 0.0:
			angle_of_wheel = angle_of_wheel + 360
		dy, dx = y1 - y0, x1 - x0
		angle_of_motion = math.atan2(dy, dx) * 180 / math.pi 
		if angle_of_motion < -360 or angle_of_motion > 360:
			print("WOW  Angle of motion out of range: ", angle_of_motion, dy, dx)
		if angle_of_motion < 0.0:
			angle_of_motion = angle_of_motion + 360
	
		# Calculate closest angle between
		angle = 180 - math.fabs(math.fabs(angle_of_wheel - angle_of_motion) - 180)
		Overlay().setText(5, "wheel:  %5.1f" % angle_of_wheel)
		Overlay().setText(4, "motion: %5.1f" % angle_of_motion)
		Overlay().setText(3, "angle:  %5.1f" % angle)
		Overlay().setText(2, "motion: %5.1f" % angle_of_motion)
		return angle / 180

	def addPoint(self, x, y, wheel_dir, force):
		self.wheel_state.append((x, y, wheel_dir, force))
		if len(self.wheel_state) < 1:
			return
		h = self.wheel_width * 0.5
		vdata = GeomVertexData("skid", GeomVertexFormat.getV3c4(), Geom.UHStatic)
		vdata.setNumRows(len(self.wheel_state)+2)
		vtx = GeomVertexWriter(vdata,  "vertex")
		cx  = GeomVertexWriter(vdata,  "color")
		prim = GeomTriangles(Geom.UHStatic)
		i = 0
		lastx, lasty = self.wheel_state[0][0], self.wheel_state[0][1]
		for ws in self.wheel_state:
			x, y, a, f = ws  
			weight = h * (self.calWeight(lastx, lasty, x, y, a) + 0.1)
			rads = (a-90) * math.pi / 180.0
			x0, y0 = x + weight*math.cos(rads), y + weight*math.sin(rads)
			rads = (a+90) * math.pi / 180.0
			x1, y1 = x + weight*math.cos(rads), y + weight*math.sin(rads)
			c = self.forceToColor(f)
			vtx.addData3f(x0, y0, -0.4)
			vtx.addData3f(x1, y1, -0.4)
			cx.addData4f(*c)
			cx.addData4f(*c)
			i += 2
			if i > 2:
				prim.addVertices(i-4, i-2, i-3)
				prim.addVertices(i-1, i-3, i-2)
				prim.addVertices(i-3, i-2, i-4)
				prim.addVertices(i-2, i-3, i-1)
		prim.closePrimitive()
		geom = Geom(vdata)
		geom.addPrimitive(prim)
		node = GeomNode('Skid')
		node.addGeom(geom)
		if self.nodepath:
			self.nodepath.removeNode()
		self.nodepath = render.attachNewNode(node)

