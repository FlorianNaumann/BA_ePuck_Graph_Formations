# standard imports
import logging
import numpy as np

# project related imports
from graph import *

#constants
MY_BT = 1321


class formation():
	"""
	"""
	
	def __init__(self, graph=None):
		
		if graph is not None :
			if self.set_graph(graph) is not True:
				raise TypeError('invalid type of graph')			
		else:
			self.my_graph = None
				
		# ID to table entry dictionary
		self.ID_lookup = {MY_BT : 0, 1234 : 1}

		return
		

	
	
	def run(self, graph):
		if self.my_graph.is_complete():
			if not self.my_graph.is_directed():
				# we have an complete undirected graph
				# henneberg sequence
				pass


	def set_graph(self, new_graph):
		g = self._make_usable_graph(new_graph)
		if g is not None :
			self.my_graph = g
			return True
		return False


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



#lets test this shit
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
