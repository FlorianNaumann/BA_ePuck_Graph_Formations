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
			self.robot = ePuck()
			self.robot.connect()

		# setup formation
		# - do initial robot-assignment (btPIN to graph-vertex, same on all robots, hardcoded??)
		self.myPin = self.robot.get_btPin()

		# - setup localization
		loc.setup(self.robot)

		# setup communication modules
		com.setup(self.robot)
		
		return
		

	def run(self):
	
		# ---------------- Part 1 ---------------- 	
		#initial step
		self.robot.step()

		# estimate the current formation with the localization module
		est_graph, ID_Map = loc.get_formation(self.robot, self.myPin)
			
		# sense initial formation
		self.formation = form.formation( est_graph, ID_Map )

		# who is the leader? am i the leader?
		leaderID = self.determine_leader()
		return

		# ---------------- Part 2 ---------------- 
		# control loop
		while True:
		
			# do environment stuff
			#     communication
			mission = com.get_mission()
			#     get sensor data
			local = loc.get_localisation(self.robot, self.myPin)
			
			# interpret sensor data
			#     update mission (new goals)
			#     get optimal position
			(dx,dy) = get_opt_pos(local)
			
			# calculate course update
			#     derive private (long term) goal from mission (general course)
			#     get (mid term) goal from local sensing (obstacle avoidance)
			#     choose formation correction from relative position
			
			# output motor speeds

			self.robot.step()
		
		return
	
	
	def show_formation(self):
		print self.formation.get_graph()
		print self.formation.get_IDmap()
		return

	
	def determine_leader(self):
		"""
		gets the id of the supposed leader robot of the formation
		the following priorities are used:
		1) get possible leaders from graph of the formation
		2) get further information from communication
		3) get the robots closest to the target / goal / mission
		4) get the robot with lowest btPIN

		return	btPIN of the chosen ONE!
		rtype	int
		"""
		# empty	dictionary
		ranking = {}

		# gather data from the different sources
		a = self.formation.get_possible_leaders() # TODO implement this
		weight_a = 1

		b = com.get_desired_leader()
		weight_b = 1

		c = loc.get_closest_leader() #TODO is this from loc?
		weight_c = 1

		# calculate ratings for each robot		
		for ids, weight in [(a,weight_a),(b,weight_b),(c,weight_c)]:
			if weight != 0:
				for ID in ids:
					if ID in ranking:
						ranking[ID] = ranking[ID] + weight
					else:
						ranking[ID] = weight

		# return the robot with the highest rating and the lowest btPin=ID
		return min( [key for key in d.keys() if ranking[key]==ranking[max(ranking)]] )


		
	def	get_motor_speeds(self):
		"""
		returns the needed motor speeds of the robot in order to maintain formation
		rtype: tuple
		"""
		return (spd_left, spd_right)

	def get_opt_pos(self, local):


		return (dx, dy)

if __name__ == "__main__":
	
	c=control()
	c.run()

