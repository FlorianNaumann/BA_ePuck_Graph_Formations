"""
Graph ePuck framework:
communication.py

You can put Bluetooth or WLAN communication in here
that sets up a connection and sends/receives mission goals

"""

# standard imports
import numpy as np
import platform

# project related imports
if platform.machine() == 'armv7l':
	from ePuck import *
else:
	from fakebot import *
from constants import *



def get_new_msg():
	return None

def get_desired_leader():
	"""
	decides the leader of the formation
	idea:	can be divided into "server setting" and "election by the swarm",
			perhaps switching between these modes or depending on connection to server -> increasing stability
	"""	
	return []

def setup(robot):
	return True
