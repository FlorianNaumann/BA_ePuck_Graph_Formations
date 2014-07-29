# standard imports
import logging
import numpy as np
import platform

# project related imports
from constants import *
import communication as com
import localization as loc
import formation as form

if platform.machine() == 'armv7l':
	from ePuck import ePuck


class control():
	"""
	Description stuff
	"""
	
	def __init__(self, robot = None):
		
		#logging.basicConfig(level=logging.DEBUG,
		#					format='%(asctime)s %(levelname)-8s %(message)s',
		#					datefmt='%a, %d %b %Y %H:%M:%S',
		#					filename='/logs/control.log',
		#					filemode='w'))
		
		# setup robot
		if (robot == None):
			robot = ePuck()
			robot.connect()

		# setup formation
		# - do initial robot-assignment (btPIN to graph-vertex, same on all robots, hardcoded??)
		myPin = robot.get_btPin()

		# - setup localization
		loc.setup(robot)

		# setup communication modules
		com.setup(robot)
		
		return
		

	def run():
	
		robot.step()
		
		# sense initial formation
		self.formation = form.formation( loc.get_formation() )

		# loop
		while True:
		
			# do environment stuff
			#     communication
			mission = com.get_mission()
			#     get sensor data
			local = loc.get_localisation(robot, myPin)
			
			# interpret sensor data
			#     update mission (new goals)
			#     get optimal position
			(dx,dy) = get_opt_pos(local)
			
			# calculate course update
			#     derive private (long term) goal from mission (general course)
			#     get (mid term) goal from local sensing (obstacle avoidance)
			#     choose formation correction from relative position
			
			# output motor speeds

			robot.step()
		
		return
	
		
	def	get_motor_speeds():
		"""
		returns the needed motor speeds of the robot in order to maintain formation
		rtype: tuple
		"""
		return (spd_left, spd_right)

	def get_opt_pos(local):


		return (dx, dy)

if __name__ == "__main__":
	
	c=control()
	c.run()

