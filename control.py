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
		
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def main(self):
		
		self.setup()
		while(True):
			try:
				self.run()
			except KeyboardInterrupt:
				print 'stopped by user'
				break

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	
	def setup(self):
		# ---------------- Part 1 ----------------
		#initial setup
		self.robot.step()

		# estimate the current formation with the localization module
		est_graph, ID_Map = loc.get_formation(self.robot, self.myPin)
			
		# save the estimated current formation as target formation
		self.formation = form.formation( est_graph, ID_Map )

		# who is the leader? am i the leader?
		# do this here once. if any changes for the leader occur, they are introduced from the com and handled at update_goals
		leaderID = self.determine_leader()

		# give leaderID back to the formation
		self.formation.set_leader(leaderID)
		# and calculate a minimal control graph (DEBUG OUTPUT, making sure to NOT do this calculation inside the loop)
		print self.formation.setup_control_graph()

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def run(self):
		# ---------------- Part 2 ---------------- 
		# control loop
	
		# do environment stuff
		#     communication
		msg = com.get_new_msg()
		#     get sensor data
		local = loc.get_localization(self.robot, self.myPin)

		# interpret sensor data
		#     update mission (new goals) from the gotten message
		self.update_goals(msg)
		#     get optimal position
		(dx,dy) = self.get_opt_pos(local)
	
		if self.myPin == 3140 or self.myPin == 3306: #TODO remove this debug output
			print 'Agent#',self.myPin,' opt_pos = ',(dx,dy)

		# calculate course update (done in get_speed_vector)
		#     derive private (long term) goal from mission (my final position)
		#     get (mid term) goal from local sensing (obstacle avoidance) -> not_implemented
		#     choose formation correction from relative position (from local)
		v = self.get_speed_vector((dx,dy))
#		print 'Agent#',self.myPin,' speed_v = ',v

		# get and set motor speeds
		(lmotor, rmotor) = self.get_motor_speeds(v)
		self.robot.set_motors_speed(lmotor, rmotor);
		self.robot.step()
	
		return
	
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def show_formation(self):
		print self.formation.get_graph()
		print self.formation.get_IDmap()
		return

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	
	def update_goals(self, msg):
		# just a dummy function, because the communication is not implemented
		# e.g.: for a formation change introduced by the base station, do the following here:
		#	1) save the new formation as target formation
		#		self.formation = form.formation( new_graph, new_ID_Map )
		# 	2) start the leader election:
		#		leaderID = self.determine_leader()
		# 	3) give leaderID back to the formation
		#		self.formation.set_leader(leaderID)
		if (msg is None):
			return True
		else:
			# DO the fancy stuff here
			return True

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
	
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
		l = () # loc.get_closest_leader() #TODO [optional] make this work
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
		top_candidates = [key for key in ranking.keys() if ranking[key]==ranking[max(ranking)]]
		if len(top_candidates) == 0:
			return ()
		else:
			return min( top_candidates )

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
		
	def	get_speed_vector(self, target, final_pos = None):
		"""
		returns the needed motor speeds of the robot in order to maintain formation
		rtype: tuple
		"""
		target_pos = np.array(target)
		
		# if no final position is set, let the formation drive straight ahead
		if(final_pos == None):
			final_pos = target_pos


		# get my robot type (leader, firstfollower, follower)		
		lc = len(self.formation.get_agent_leaders(self.myPin))
		if lc == 0:
			me = 'l' # leader 
		elif lc == 1:
			me = 'c' # first follower
		else:
			me = 'f' # ordinary follower

		# step 1) get speed-vectors from the formula		
		# ordinary follower:
		dist = np.linalg.norm(target_pos)
		if dist < MIN_ERROR:
			beta = 0
		elif MIN_ERROR <= dist < 2*MIN_ERROR:
			beta = (dist-MIN_ERROR)/MIN_ERROR
		else:
			beta = 1

		dist_final = np.linalg.norm(final_pos)
		# another drive straight-hack:
		beta_final = 1
		#if dist_final < MIN_ERROR_FINAL:
		#	beta_final = 0
		#elif MIN_ERROR_FINAL <= dist < 2*MIN_ERROR_FINAL:
		#	beta_final = (dist-MIN_ERROR_FINAL)/MIN_ERROR_FINAL
		#else:
		#	beta_final = 1

		if ( me == 'f' ):
			if beta != 0: # prevent division by zero
				v = (MAX_SPD) * beta * target_pos / dist
			else:
				v = np.array([0,0])
			print 'follower speed vector: ',v, '  beta: ',beta
		elif ( me == 'c' ):
			if beta != 0: # prevent division by zero
				# maintain formation position speed
				v1 = MAX_SPD * target_pos / dist
				# turn speed to get close to the final position
				circle_vector = np.array([-target_pos[1], target_pos[0]])
				v2 = MAX_SPD * beta_final * np.dot(circle_vector, final_pos) * (circle_vector / dist) # end_pos
				v = beta * v1 + math.sqrt(1-beta**2) * v2
			else:
				v = np.array([0,0])
			#print 'firstfollower speed vector: ',v, '  beta: ',beta
		elif (me == 'l'):
			if beta_final != 0: # TODO here i set a reduced maximum speed
				v = (MAX_SPD*0.7) * beta_final * (final_pos / np.linalg.norm(final_pos)) # note: in the case of the leader the final_pos is identical to the target_pos
			else:
				v = np.array([0,0])

		return v

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def get_motor_speeds(self, speed_vector):
		# step 2) calculate motor updates		
		# hopefully smoother curve implementation for 2 motors
		# TODO sort out some small radii that result in a bad movement;
		#print 'speedy:', speed_vector # TODO remove
		if ( speed_vector[0] != 0 ): # curve

			alpha = math.pi - 2*math.atan2(speed_vector[1],speed_vector[0])
			d = np.linalg.norm(speed_vector) * math.pi / 1000 * (5*STEP_SIZE) * WHEEL_DIAMETER

			r = d/alpha

			if abs(r) < WHEEL_DIAMETER/2 or True:
				spd_left  = np.linalg.norm(speed_vector) * math.copysign(1,speed_vector[1]) * ( r+(WHEEL_DISTANCE/2) )/r
				spd_right = np.linalg.norm(speed_vector) * math.copysign(1,speed_vector[1]) * ( r-(WHEEL_DISTANCE/2) )/r
			else:
				spd_left  = speed_vector[1]
				spd_right = speed_vector[1]
		else: # drive straight
			spd_left  = speed_vector[1]
			spd_right = speed_vector[1]

		return (round(spd_left), round(spd_right))

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def get_opt_pos(self, local):

		# get leader IDs from formation
		leaders = self.formation.get_agent_leaders(self.myPin)
		if len(leaders) == 0 : # leader of the formation
			# fake; drive forward
			dx = 0
			dy = 1
		else:
			ref1 = 0 # first reference robot
			ref2 = 1 # second reference robot
			while True: # calculate intersection of optimal distances
				if len(leaders) == 1 : # first follower
					# follow the mainleader 
					a = local[leaders[ref1]][1]
					b = local[leaders[ref1]][0]
					c = 0
#					print "coming from firstfollower, leader = ", (local[leaders[ref1]][0], local[leaders[ref1]][1])
				elif len(leaders) >= 2 : # ordinary follower
					# calc optimal position x and y from formula and localization of both leaders
					# ------ the equation of the line of the intersections ax+by=c ------ # TODO check this!!
					a = 2*(local[leaders[ref1]][0] - local[leaders[ref2]][0]) # same x on both leaders produces 0!!
					b = 2*(local[leaders[ref1]][1] - local[leaders[ref2]][1])
					c = (( local[leaders[ref1]][0]**2 + local[leaders[ref1]][1]**2 ) - self.formation.get_distance(self.myPin, leaders[ref1])**2 - (local[leaders[ref2]][0]**2 + local[leaders[ref2]][1]**2) + self.formation.get_distance(self.myPin, leaders[ref2])**2)
					print "coming from ordinary follower"
					print "leader1 = ", (local[leaders[ref1]][0], local[leaders[ref1]][1])
					print "leader2 = ", (local[leaders[ref2]][0], local[leaders[ref2]][1])

				if a != 0:
					# ------ polynomial function with  y^2*d + y*e + f = 0 ------
					#if self.myPin != 3139:
					#	print "x = (",round(c/a,2),') - (' ,round(b/a,2),')*y'
					d = 1 - b**2 / a**2
					e = (-2*c*b/(a**2)) - (2*b/a*local[leaders[ref1]][0]) -2*local[leaders[ref1]][1]
					f = c**2/a**2 - 2*c/a*local[leaders[ref1]][0] + local[leaders[ref1]][0]**2 +local[leaders[ref1]][1]**2 - self.formation.get_distance(self.myPin, leaders[ref1])**2
				else:
					#if self.myPin != 3139:
					#	print "y = (",round(c/b,2),') - (' ,round(a/b,2),')*x'
					d = 1 - a**2 / b**2
					e = -2*c*a/(b**2) - 2*a/b*local[leaders[ref1]][1] -2*local[leaders[ref1]][0]
					f = local[leaders[ref1]][0]**2 + (c/b - local[leaders[ref1]][1])**2 - self.formation.get_distance(self.myPin, leaders[ref1])**2

				# ------ calculate both intersections from the quadratic equation ------
				D = e**2-4*d*f
				if D >= 0: # are there even intersections?
					if a != 0:
						if d != 0:
							y1 = ( -e + math.sqrt(D) ) / (2*d)
							y2 = ( -e - math.sqrt(D) ) / (2*d)
						else:
							y1 = y2 = -f/e
						x1 = (c - b*y1) / a
						x2 = (c - b*y2) / a
					else:
						if d != 0:
							x1 = ( -e + math.sqrt(D) ) / (2*d)
							x2 = ( -e - math.sqrt(D) ) / (2*d)
						else:
							x1 = x2 = -f/e
						y1 = -(a*x1 - c) / b
						y2 = -(a*x2 - c) / b
					break # escape loop
				else:
					print len(leaders)
					# if there is no intersection try again with another pair of leaders if possible (not the case for minimally persistent graphs)
					if ( len(leaders) > ref2+1 ): #if there are alternative leader-circles try them
						ref1 = ref1+1
						ref2 = ref2+1
					elif ( len(leaders) == ref1+2 and ref1 != 0):
						ref1 = 0
					else: # there are no alternative leaders and we have no intersection;
						# drive towards the point halfway in between the first two leader-robots
						print 'alternative!'
						dy = (local[leaders[ref1]][1]+local[leaders[ref2]][1])*0.5
						dx = (local[leaders[ref1]][0]+local[leaders[ref2]][0])*0.5
						return (round(dx,2), round(dy,2))

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

