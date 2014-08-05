"""
Graph ePuck framework:
formation.py
"""


# standard imports
import logging
import numpy as np

# project related imports
from constants import *
from graph import *




class formation():
	"""
	class that wraps the graph and stores a mapping from the nodes to the robotIDs
	"""
	
	def __init__(self, graph=None, ID_Map={}):
		
		if graph is not None :
			if self.set_graph(graph) is not True:
				raise TypeError('invalid type of graph')			
		else: 
			self.my_graph = None
				
		# ID to table - dictionary
		self.ID_lookup = ID_Map

		return
		


#	def run(self, graph):
#		if self.my_graph.is_complete():
#			if not self.my_graph.is_directed():
#				# we have an complete undirected graph
#				# henneberg sequence
#				pass
#		return


	def get_possible_leaders(self):
		return [ ID for ID in self.ID_lookup.keys() if self.ID_lookup[ID] in self.my_graph.get_potential_leaders() ] # easy einzeiler ;)

#####################################################
#													#
#		G E T   &   S E T   F U N C T I O N S		#
#													#
#####################################################

	def set_graph(self, new_graph):
		g = self._make_usable_graph(new_graph)
		if g is not None :
			self.my_graph = g
			return True
		return False


	def get_graph(self):
		return self.my_graph.get_base_graph()

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def set_IDmap(self, new_IDmap):
		if isinstance(new_IDmap, dict):
			self.ID_lookup = new_IDmap
			return True
		return False


	def get_IDmap(self):
		return self.ID_lookup

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def get_distance(self, fromID, toID):
		return self.my_graph[(self.ID_lookup[fromID], self.ID_lookup[toID])]

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def get_agent_leaders(self, myID):
		# TODO get my leaders
		return (3140,3139)

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

	def set_leader(self, leaderID):
		# TODO get my leaders
		return

	def get_leader(self):
		# TODO get my leaders
		return self.leaderID

#####################################################
#													#
#		I N T E R N A L     F U N C T I O N S		#
#													#
#####################################################

	def _make_usable_graph(self, g):
		if type(g).__module__ == 'numpy' and type(g).__name__ == 'ndarray':
			# check for the lowest dimensions
			v = min(g.shape)
			# make up graph object
			gg = graph(v)
			gg.set_graph(g)
			return gg
			
		elif type(g) is 'instance' and isinstance(g, graph) :
			return g

		return None

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
##-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-##
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

# simple test run
if __name__ == "__main__":

	# Adjacency matrices
	# ------------------
	#
	#  a (not rigid)					#  b (rigid)
	# 	    A B C D E					# 	    A B C D E
	#                                   #  
	#  A    X 7 0 0 0 					#  A    X 1 0 0 1
	#  B    1 X 5 2 1					#  B    1 X 1 1 0
	#  C    0 5 X 4 1					#  C    0 1 X 1 1
	#  D    0 2 4 X 2					#  D    0 1 1 X 1
	#  E    0 1 1 2 X					#  E    1 0 1 1 X

	a = array([[0,7,0,0,0],[1,0,5,2,1],[0,5,0,4,1],[0,2,4,0,2],[0,1,1,2,0]])
	b = array([[0,1,0,0,1],[1,0,1,1,0],[0,1,0,1,1],[0,1,1,0,1],[1,0,1,1,0]])

	test = formation(b)	
	test.set_graph(b)
	print 'successful'
