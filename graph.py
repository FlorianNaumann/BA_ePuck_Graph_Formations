#standard imports
import logging
from numpy import *

#project related imports
from pebbles import *



class graph():
	"""
	Description stuff
	"""
	
	def __init__(self, vertices = 3):
		"""
		vertices is number of agents
		"""
		#logging.basicConfig(level=logging.DEBUG,
		#					format='%(asctime)s %(levelname)-8s %(message)s',
		#					datefmt='%a, %d %b %Y %H:%M:%S',
		#					filename='/logs/graph.log',
		#					filemode='w'))
							
		self.vertices = vertices
		self.my_graph = zeros((vertices, vertices))
		
		self.leader_id = None
		self.min_graph = None
	
	#----------------------------------#
	#  Testing for certain properties  #
	#----------------------------------#	
	
	def is_rigid(self):
		"""
		tests for rigidity based on the peddle game algorithm
		"""
		# test if no_of_edges is 2 v -3 (LAMAN condition)
		noEdges = self.undirected_edges + self.directed_edges
		if (noEdges >= 2*self.vertices -3) :
			if ( self.vertices < 4 ) : 
				# for all graphs with less than 4 vertices this criterium is sufficient
				# because fulfilling the Laman condition also implies here that the graph
				# is complete and therefore rigid.
				return True
			else:
				#for more vertices we have to test all subgraphs or do the pebble algorithm
				return pebble_algorithm(self.my_graph)
		else:
			return False
	
	def is_persistent(self): # = ready to roll!
		if ( self.is_rigid() ) :
			if ( self.vertices < 4 ) :
				return true
		#elif:
			#TODO
		
			# persistence, if all subgraphs are persistent
		return True
		
	def is_complete(self):
		if self.is_directed():
			if (self.directed_edges == 0.5*self.vertices*(self.vertices-1)):
				return True		
		return False
		
	def is_directed(self):
		if self.directed_edges == 0:
			return False
		else:
			return True
		
	def _get_number_of_edges(self):
		self.directed_edges=0;
		self.undirected_edges=0;
		e=0;
		for x in xrange(0,self.vertices):
			for y in xrange(x,self.vertices):
				if y==x:
					continue
				if ( self.my_graph[(x,y)] > 0 ) or ( self.my_graph[(y,x)] > 0 ): # edge
					e=e+1
					if ( self.my_graph[(x,y)] == self.my_graph[(y,x)] ): # undirected edge
						self.undirected_edges=self.undirected_edges+1
		self.directed_edges = e-self.undirected_edges
		return e
		
	#----------------------#
	#  Graph manipulation  #
	#----------------------#		
		
	def set_graph(self, array):
		"""
		Sets the graph
		"""
		self.my_graph = array

		#get number of vertices
		self.vertices = min(array.shape)

		# count directed and undirected edges
		self._get_number_of_edges()
		
		self.min_graph = None
		
		# TODO if directed, get leader
		return True
		

	def get_minimally_rigid_graph(self):

		if (self.min_graph is None):		
			# get min_graph
			#TODO

			self.min_graph = temp_graph
		return self.min_graph
		
	#-----------------------#
	#  interface functions  #
	#-----------------------#	
	
	def get_size(self):
		return self.vertices
	
	def set_leader(self, ID):
		
		self.leader_id = ID
		return
		
	def get_leader_id(self):
		"""
		if no leader is set manually, die robot with the lowest id is leader
		"""
		if self.leader_id == None :
			# get lowest id to leader
			pass
		return self.leader_id
		
		
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
	
	test = graph(5)
	test.set_graph(b)
	print 'b.get_size() =      ', test.get_size()
	print 'b.get_leader_id() = ', test.get_leader_id()
	print 'b.is_rigid() =      ', test.is_rigid()
	print 'b.is_complete() =   ', test.is_complete()
	print 'b.is_directed() =   ', test.is_directed()
