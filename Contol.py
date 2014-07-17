
import logging
from numpy import *

class control():
	"""
	Description stuff
	"""
	
	def __init__(self):
		
		logging.basicConfig(level=logging.DEBUG,
							format='%(asctime)s %(levelname)-8s %(message)s',
							datefmt='%a, %d %b %Y %H:%M:%S',
							filename='/logs/control.log',
							filemode='w'))
		
		# setup robot
		# setup formation
		# setup communication modules
		
		return
		
	def run():
	
		# loop
		
			# do environment stuff
			#     communication
			#     get sensor data
			
			# interpret sensor data
			#     update mission (new goals)
			#     get relative Localisation
			
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