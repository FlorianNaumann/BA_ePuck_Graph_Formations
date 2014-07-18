
import logging
from numpy import *

from ePuck import ePuck

class control():
	"""
	Description stuff
	"""
	
	def __init__(self, robot = None):
		
		logging.basicConfig(level=logging.DEBUG,
							format='%(asctime)s %(levelname)-8s %(message)s',
							datefmt='%a, %d %b %Y %H:%M:%S',
							filename='/logs/control.log',
							filemode='w'))
		
		# setup robot
		if (robot = None):
			robot = ePuck()
			robot.connect()
		# setup formation
		# setup communication modules
		
		return
		
	def run():
	
		# loop
		while True:
		
			# do environment stuff
			#     communication
			#     get sensor data
			local = get_localisation()
			
			# interpret sensor data
			#     update mission (new goals)
			#     get optimal position
			(dx,dy) = get_opt_pos(local)
			
			# calculate course update
			#     derive private (long term) goal from mission (general course)
			#     get (mid term) goal from local sensing (obstacle avoidance)
			#     choose formation correction from relative position
			
			# output motor speeds
		
		return
	
		
	def	get_motor_speeds():
		"""
		returns the needed motor speeds of the robot in order to maintain formation
		rtype: tuple
		"""
		return (spd_left, spd_right)