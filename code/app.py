from direct.showbase.ShowBase import ShowBase

class RobotSim (ShowBase) :
	def __init__(self):
		ShowBase.__init__(self)

app = RobotSim()
app.run()

