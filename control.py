# standard imports
import logging
import numpy as np
import math
import platform

# project related imports
from constants import *
import communication as com
import localization as loc
import formation as form

if platform.machine() == 'armv7l':
	from ePuck import *
else:
	from fakebot import *


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
		else:
			self.robot = robot

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
			
		# save the estimated current formation as target formation
		self.formation = form.formation( est_graph, ID_Map )

		# who is the leader? am i the leader?
		# TODO do i have to do this only once? or in every loop later?
		leaderID = self.determine_leader()

		# give leaderID back to the formation
		self.formation.set_leader(leaderID)
		# and calculate a minimal control graph

		# ---------------- Part 2 ---------------- 
		# control loop
		while True:
		
			# do environment stuff
			#     communication
			msg = com.get_new_msg()
			#     get sensor data
			local = loc.get_localization(self.robot, self.myPin)

			# interpret sensor data
			#     update mission (new goals)
			self.update_goals(msg)
			#     get optimal position
			(dx,dy) = self.get_opt_pos(local)

			# calculate course update
			#     derive private (long term) goal from mission (general course)
			#     get (mid term) goal from local sensing (obstacle avoidance)
			#     choose formation correction from relative position
			
			# output motor speeds

			self.robot.step()
			break
		
		return
	
	
	def show_formation(self):
		print self.formation.get_graph()
		print self.formation.get_IDmap()
		return

	
	def update_goals(self, msg):
		return True

	
	def determine_leader(self):
		"""
		gets the id of the supposed leader robot of the formation
		the following priorities are used:
		1) get possible leaders from graph of the formation
		2) get further information from communication
		3) get the robots closest to the target / goal / mission
		4) get the robot with lowest btPIN

		return	btPIN of the chosen ONE(S)!
		rtype	int
		"""
		# TODO choose weights for good decisionmaking

		# empty	dictionary
		ranking = {}

		# gather data from the different sources
		# get robots that can lead the formation
		f = self.formation.get_possible_leaders()
		weight_f = 1.2

		# get desired leader from communication / base-station
		c = com.get_desired_leader() # dummy function
		weight_c = 1

		# get closest leader
		l = () # loc.get_closest_leader() #TODO is this from loc?
		weight_l = 0.7

		# calculate ratings for each robot
		for ids, weight in [(f,weight_f),(c,weight_c),(l,weight_l)]:
			if weight != 0:
				for ID in ids:
					if ID in ranking:
						ranking[ID] = ranking[ID] + weight
					else:
						ranking[ID] = weight

		# return the robot with the highest rating and the lowest btPin=ID
		return min( [key for key in ranking.keys() if ranking[key]==ranking[max(ranking)]] )


		
	def	get_motor_speeds(self):
		"""
		returns the needed motor speeds of the robot in order to maintain formation
		rtype: tuple
		"""
		return (spd_left, spd_right)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def get_opt_pos(self, local):

		# get leader IDs from formation
		leader = self.formation.get_agent_leaders(self.myPin)
		
		if len(leader) == 2 : # ordinary follower
			# calc optimal position x and y from formula and localization of both leaders
				# ------ the equation of the line of the intersections ax+by=c ------
				a = 2*(local[leader[1]][0] - local[leader[0]][0])
				b = 2*(local[leader[1]][1] - local[leader[0]][1])
				
				c = - ( local[leader[0]][0]**2 + local[leader[0]][1]**2 ) + self.formation.get_distance(self.myPin, leader[0])**2 + (local[leader[1]][0]**2 + local[leader[1]][1]**2) - self.formation.get_distance(self.myPin, leader[1])**2

				# ------ polynomial function with  y^2*d + y*e + f = 0 ------
				d = b**2 / a**2 + 1
				e = (-2*c*b/a**2) + (2*b/a*local[leader[0]][0]) + (-2*local[leader[0]][1])
				f = c**2/a**2 - 2*c/a*local[leader[0]][0] + local[leader[0]][0]**2 +local[leader[0]][1]**2 - self.formation.get_distance(self.myPin, leader[0])**2

				# ------ calculate both intersections from the quadratic equation ------
				D = e**2-4*d*f
				if D >= 0: # are there even intersections?
					y1 = ( -e + math.sqrt(D) ) / (2*d)
					x1 = (b*y1 - c) / a
					y2 = ( -e - math.sqrt(D) ) / (2*d)
					x2 = (b*y2 - c) / a
				else:
					#TODO what if there is no intersection?? HELP ME!!
					return (0,0)

				# check which pair of coordinates is closer to me
				if (y1**2+x1**2) > (y2**2+x2**2):
					dx = x2
					dy = y2
				else:
					dx = x1
					dy = y1

		return (round(dx,2), round(dy,2))

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

	ID = 3112

	A = [(3140, 2, 1, 4., 123123L),( 3139, 1, 5, 5., 12124L),( 3112, 9, 9, 0.,123121233L),( 3306, 7,2, 4.12, 12123L)]
	B = [(3140, 9, 9, 0., 123114L),( 3139, 1, 0, 3., 12412L),( 3112, 5, 5, 4.,123123123L),( 3306, 6,6, 6.4,  12314L)]
	C = [(3140, 9, 9, 0., 123114L),( 3139, 9, 9, 0., 12412L),( 3112, 5, 5, 4.,123123123L),( 3306, 6,6, 6.4,  12314L)]

	testi = A

	fakebot = ePuck(PIN=ID, val_tup=testi)
	fakebot.connect()

	c=control(robot=fakebot)
#	c.show_formation()

	c.run()
#	c.show_formation()
#	print c.get_opt_pos(local)

