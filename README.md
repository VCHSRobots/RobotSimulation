# RobotSimulation

This project simulates a swerve drive robot in a 3D like game environment.  The primary purpose is to provide a platform to study and develop user interfaces to control a swerve drive robot.  Consequently, the simulation attempts to both be visually accurate, and be somewhat realistic with the interaction between the the robot and the floor.  That is, some pains have been taken to accurately simulate the interaction of the wheels and the carpet for skid responses as well as simple rolling.

The simulation is built on the Panda3D framework.  It should be able to be easily ported to Windows, Mac, and Linux.  The visual models were developed with Blender 2.8.  The models where transferred between blender and Panda3d by way of wavefront (obj) files.

## Development

For continued development, you will need the following:

	1. Access to github.  Clone the RobotSimulation project under github.com/VCHSRobots.
	2. Installation of python 3.7 or higher.
	3. Installation of pip (for phython).
	4. Installation of Panda3D.  As of this writing, we are using version 1.10.3.
	5. Installation of Blender 2.8, if you want to improve the models.
	6. Installation of minor python packages, such as pygame. (Use pip for this.)
	7. Access to a text editor, such as notepad++ or sublime.
	8. A computer with a decent graphics card.
	9. A game pad or joystick, along with a normal mouse.
	10. Patience, a browser, an internet connection, and an aptitude to self-start. 

## Using the Simulator

To run the simulator, you will need most of the above, as well as some configuration of things like the Panda3D's configuration file.  Most of the steps to get a running simulaion have not been fully documented thus far -- so good luck.

Once the right stuff is installed and configured for your system, try:

	>python .../code/robotsim.py 

## Credits

	Holiday Pettijohn -- Lead Student, 2019
	Dalbert Brandon   -- Mentor




