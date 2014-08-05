# standard imports
import numpy as np
import math as math
import platform

# project related imports
if platform.machine() == 'armv7l':
	from ePuck import *
else:
	from fakebot import *

from constants import *


# Names to indices for better readability
BT_PIN		= 0
MY_SENSOR	= 1
HIS_SENSOR	= 2
DISTANCE	= 3




######################################################
#-													-#
#-		I N T E R F A C E   F U N C T I O N S		-#
#-													-#
######################################################

def get_localization(robot, myPin, val_tup = None):
	"""
	this is the interface function that is used in Control.py
	it creates a grid that is aligned with the robot's view
	and returns the robots coordinates together with its IDs

	param robot: an active connected ePuck instance
	type robot:  an active connected ePuck instance

	return:	a dictionary that maps IDs to (x,y) coordinate pairs relative to this agent
	rtype:	dictionary
	"""
	# the dictionary to be returned
	IDcoords = {myPin : (0,0)}

	# get relative measurements
	if robot != None:
		val_tup = robot.get_rel_pos()

	active_bots = _filter_active_units(val_tup, myPin)
	IDdict = _get_id_lookup(active_bots)
	na = _get_neighbours(myPin, active_bots, IDdict)
	ad = _get_angles(myPin, active_bots)

	IDcoords = _calc_coords(myPin, na, IDdict, ad)

	return IDcoords

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def get_formation(robot, myPin, val_tup = None):
	"""
	this is the interface function that is used in Control.py
	it should provide the sensed graph that represents the current real formation

	param robot: an active connected ePuck instance
	type robot:  an active connected ePuck instance

	param myPin: btPin of this Agent
	type myPin:  int

	param val_tup: testing interface
	type val_tup:  tuple

	return	Graph(np.array) and ID Mappping(dict) as a tuple
	rtype:	tuple
	"""
	if robot != None:
		val_tup = robot.get_rel_pos()

	active_bots = _filter_active_units(val_tup, myPin)
	IDdict = _get_id_lookup(active_bots)
	na = _get_neighbours(myPin, active_bots, IDdict)
	ad = _get_angles(myPin, active_bots)
	fg = _fill_graph(myPin, na, IDdict, ad)

	return fg, IDdict

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def setup(robot):
	"""
	does the setup to use the relative position from Sophia Schillai
	"""

	robot.enable('relative_position')

	return

#####################################################
#													#
#		I N T E R N A L     F U N C T I O N S		#
#													#
#####################################################

def _filter_active_units(val_tup, myPin):
	# TODO implement timestamps here also?

	for robo in val_tup:
		if robo[BT_PIN] == myPin:
			continue
		if robo[MY_SENSOR] == 9 and robo[HIS_SENSOR] == 9 and robo[DISTANCE] == 0 :
			val_tup.remove(robo)

	return val_tup

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def _get_id_lookup(val_tup):
	# how many robots do we have?
	no_agents =	len(val_tup)

	# setup an ID to btPin
	return dict(zip(sorted([ int(robo[BT_PIN]) for robo in val_tup ]),range(no_agents)))

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def _get_neighbours(myPin, val_tup, dict_IDs):
	"""
	"""
	# how many robots do we have?
	no_agents =	len(val_tup)

	# --- transform tuple to array ---
	sensed_array = np.zeros((no_agents,no_agents))

	for i in xrange(no_agents): # do for each set of data
		coords = (dict_IDs[myPin], dict_IDs[val_tup[i][BT_PIN]])
		sensed_array[coords      ] = val_tup[i][DISTANCE] # assign distances
		sensed_array[coords[::-1]] = val_tup[i][DISTANCE] # assign distances

	return sensed_array

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def _get_angles(myPin, val_tup):

	# how many robots do we have?
	no_agents =	len(val_tup)

	# dict that maps IDs to angles
	angle = {}

	for i in xrange(no_agents): # do for each set of data
		if val_tup[i][BT_PIN] == myPin:
			angle[myPin] = 0
		angle[val_tup[i][BT_PIN]] = DICT_SENSOR_ANGLES[val_tup[i][MY_SENSOR]]

	return angle

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def _calc_coords(myPin, na, IDdict, ad):
	IDcoords = {}

	for v in IDdict.keys()	:
		y = math.sin(ad[v]) * na[IDdict[myPin]][IDdict[v]]
		x = math.cos(ad[v]) * na[IDdict[myPin]][IDdict[v]]
		IDcoords[v] = (round(x,2),round(y,2))
	return IDcoords

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

def _fill_graph( myPin, neighbour_array, IDdict, angle_map ):
	"""
	Use the Law of Cosines to get an estimate of the distances between the neighbours
	"""
	no_agents = neighbour_array.shape[0]

	# inverse mapping of IDdict. e.g. PINdict[myId] = mypin
	PINdict = dict((v,k) for k, v in IDdict.items())

	for v1 in xrange(no_agents):
		if v1 == IDdict[myPin] or angle_map[PINdict[v1]] == -1:
			continue
		for v2 in xrange(v1+1, no_agents):
			if v2 == IDdict[myPin] or angle_map[PINdict[v2]] == -1:
				continue
			# print 'processing edge from ',PINdict[v1],' to ',PINdict[v2]
			# translate detecting sensors into angles
			alpha = abs(angle_map[PINdict[v1]] - angle_map[PINdict[v2]])
			# calculate distance with the law of cosines
			d1 = neighbour_array[(IDdict[myPin],v1)]
			d2 = neighbour_array[(IDdict[myPin],v2)]
			dx = math.sqrt( d1**2 + d2**2 - 2*d1*d2*math.cos(alpha) )

			neighbour_array[(v1,v2)] = round(dx,2)
			neighbour_array[(v2,v1)] = round(dx,2)
	
	return neighbour_array



#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

if __name__ == "__main__":

	ID = 3112

	A = [(3140, 2, 1, 4., 123123L),( 3139, 1, 5, 5., 12124L),( 3112, 9, 9, 0.,123121233L),( 3306, 7,2, 4.12, 12123L)]
	B = [(3140, 9, 9, 0., 123114L),( 3139, 1, 0, 3., 12412L),( 3112, 5, 5, 4.,123123123L),( 3306, 6,6, 6.4,  12314L)]
	C = [(3140, 9, 9, 0., 123114L),( 3139, 9, 9, 0., 12412L),( 3112, 5, 5, 4.,123123123L),( 3306, 6,6, 6.4,  12314L)]

	testi = A

	fakebot = ePuck(PIN=ID, val_tup=testi)
	fakebot.connect()

	a = get_formation(fakebot,ID)
	print a

#	active_bots = _filter_active_units(testi, ID)
#	print active_bots
#	IDdict = _get_id_lookup(active_bots)
#	print IDdict
#	na = _get_neighbours(ID, active_bots, IDdict)
#	print na
#	ad = _get_angles(ID, active_bots)
#	print ad
#	cc = _calc_coords(ID, na, IDdict, ad)
#	print cc
#	fg = _fill_graph(ID, na, IDdict, ad)
#	print fg
	

