# standard imports
import numpy as np
import math as math
import platform

# project related imports
if platform.machine() == 'armv7l':
	from ePuck import ePuck
from constants import *


def get_localization(robot, myPin, val_tup = None):
	"""
	this is the interface function that is used in Control.py
	it should provide the sensed graph that represents the current real formation

	param robot: an active connected ePuck instance
	type robot:  an active connected ePuck instance
	"""
	return


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
	"""
	if robot != None:
		val_tup = robot.get_rel_pos()

	IDdict = _get_id_lookup(val_tup)
	na = _get_neighbours(myPin, val_tup, IDdict)
	ad = _get_angles(myPin, val_tup)
	fg = _fill_graph(myPin, na, IDdict, ad)

	return fg


def _get_id_lookup(val_tup):
	# how many robots do we have?
	no_agents =	len(val_tup)/5

	# setup an ID to btPin
	return dict(zip(sorted(np.array(val_tup)[0::5].astype(int)),range(no_agents)))


def _get_neighbours(myPin, val_tup, dict_IDs):
	"""
	this is the interface function that is used in Control.py
	it should provide the sensed graph that represents the current real formation

	param robot: an active connected ePuck instance
	type robot:  an active connected ePuck instance
	"""
	# how many robots do we have?
	no_agents =	len(val_tup)/5

	# --- transform tuple to array ---
	sensed_array = np.zeros((no_agents,no_agents))

	for i in xrange(no_agents): # do for each set of data
		coords = (dict_IDs[myPin],dict_IDs[val_tup[i*5]])
		sensed_array[coords      ] = val_tup[i*5+3] # assign distances
		sensed_array[coords[::-1]] = val_tup[i*5+3] # assign distances

	return sensed_array


def _get_angles(myPin, val_tup):

	# how many robots do we have?
	no_agents =	len(val_tup)/5

	# dict that maps IDs to angles
	angle = {}

	for i in xrange(no_agents): # do for each set of data
		if val_tup[i*5] == myPin:
			continue
		angle[val_tup[i*5]] = DICT_SENSOR_ANGLES[val_tup[i*5+2]]

	return angle


def _fill_graph( myPin, neighbour_array, IDdict, angle_map ):
	"""
	Use the Law of Cosines to get an estimate of the distances between the neighbours
	"""
	no_agents = neighbour_array.shape[0]

	# inverse mapping of IDdict. e.g. PINdict[myId] = mypin
	PINdict = {v:k for k, v in IDdict.items()}

	for v1 in xrange(no_agents):
		if v1 == IDdict[myPin]:
			continue
		for v2 in xrange(v1+1, no_agents):
			if v2 == IDdict[myPin]:
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


def setup(robot):
	"does the setup to use the relative position from Sophia Schillai"

	robot.enable('relative_position')

	return



if __name__ == "__main__":

	ID = 3112

	A = (3140, 1, 2, 4., 123123L, 3139, 5, 1, 5., 123124L, 3112, 9, 9, 0.,123123L,    3306, 2,7, 4.12, 123123L)
	B = (3140, 9, 9, 0., 123114L, 3139, 1, 0, 3., 12412L,  3112, 5, 5, 4.,123123123L, 3306, 6,6, 6.4, 12314L)

	testi = B

	fg = get_formation(None,3140,testi)

#	IDdict = _get_id_lookup(testi)
#	print IDdict
#	na = _get_neighbours(ID, testi, IDdict)
#	print na
#	ad = _get_angles(ID, testi)
#	print ad
##	fg = _fill_graph(ID, na, IDdict, ad)
	print fg
	

