#standard imports
import logging
import numpy as np

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
		
		self.Error = False

		self.vertices = vertices
		self.my_graph = zeros((vertices, vertices))
		
		self.min_graph   = None
		self.base_graph  = None

		self.leader_id        = None
		self.firstfollower_id = None
		self.graph_is_rigid         = None
		self.graph_is_persistent    = None
	
	#----------------------------------#
	#  Testing for certain properties  #
	#----------------------------------#	
	
	def is_rigid(self):
		"""
		tests the underlying undirected graph for rigidity based on the peddle game algorithm
		"""
		if ( self.Error ):
			self._error_msg()
			return False

		if ( self.graph_is_rigid == None ):
			self.graph_is_rigid = False
			# only operate on the underlying undirected graph
			# test if no_of_edges is 2 v -3 (LAMAN condition)
			noEdges = self.undirected_edges + self.directed_edges
			if (noEdges >= 2*self.vertices -3) :
				if ( self.vertices < 4 ) :
					# for all graphs with less than 4 vertices this criterium is sufficient
					# because fulfilling the Laman condition also implies here that the graph
					# is complete and therefore rigid.
					self.graph_is_rigid = True
				else:
					#for more vertices we have to test all subgraphs or do the pebble algorithm
					self.graph_is_rigid = pebble_algorithm(self.get_base_graph())

		return self.graph_is_rigid
	

	def is_persistent(self): # = ready to roll out autobots!
		"""
		tests the directed graph for rigidity based rigidity and constraint consistence
		"""
		if ( self.Error ):
			self._error_msg()
			return False

		if ( self.graph_is_persistent == None ):
			self.graph_is_persistent = False
			# rigidity of the underlying undirected graph is necessary but not sufficient
			if ( self.is_rigid() ) :
				if ( self.vertices < 4 ) :
					self.graph_is_persistent = True
				else:
					# ~~~~~ test for constraint consistence ~~~~~ #
					# --- simple test for cycle-free or leader-follower structured graphs ---
					# step 1) find the one leader (out-degree of 0)
					# step 2) indentify the coleader (out-degree of 1 AND connection to the leader)
					# step 3) every other vertex has to have more than 2 outgoing edge
					if self._check_for_leader_follower() :
						if (self.my_graph[(self.firstfollower_id, self.leader_id)] != 0) :
							self.graph_is_persistent = True
		return self.graph_is_persistent
		

	def is_complete(self):
		"""
		checks for complete graphs
		"""
		# verify functionality
		if not self.is_directed():
			if (self.undirected_edges == 0.5*self.vertices*(self.vertices-1)):
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

		# Reset Error Flag
		self.Error = False

		#get number of vertices
		self.vertices = min(array.shape)

		# count directed and undirected edges
		self._get_number_of_edges()
		
		# reset some stored graphs
		self.min_graph  = None
		self.base_graph = None
		
		# reset saved properties		
		self.leader_id        = None
		self.firstfollower_id = None
		self.graph_is_rigid         = None
		self.graph_is_persistent    = None

		return True
		

	def get_minimally_rigid_graph(self):

		if ( self.Error ):
			self._error_msg()
			return None
		
		elif (self.min_graph is None):		
			# TODO get min_graph based on leader

			self.min_graph = temp_graph
		return self.min_graph


	def get_base_graph(self):
		"""
		returns the underlying undirected graph of the specified graph		
		"""
		if ( self.Error ):
			self._error_msg()
			return None

		# do we already have an base_graph set?
		elif (self.base_graph is None):
			# No, therefore get one
			if (self.directed_edges == 0):		
				self.base_graph = np.copy(self.my_graph)
			else:
				# get base_graph by mirroring undirected edges
				self.base_graph = np.copy(self.my_graph)
				e=self.directed_edges;
				for x in xrange(0,self.vertices):
					if (e==0):
						break
					for y in xrange(x,self.vertices):
						if (e==0):
							break
						if y==x:
							continue
						val1 = self.my_graph[(x,y)]
						val2 = self.my_graph[(y,x)]
						if ( val1 != val2 ): # undirected edge
							if ( val1 == 0 ):
								self.base_graph[(x,y)] = val2
								e=e-1
							elif ( val2 == 0 ):
								self.base_graph[(y,x)] = val1
								e=e-1
							else:
								self.Error = True
								self.base_graph = None
								raise ValueError('Uneven undirected edge in Graph')

		return self.base_graph

	#-----------------------#
	#   helper  functions   #
	#-----------------------#	

	def _error_msg(self):
		print 'Your Graph seems uneven or corrupted. Please set new one to ensure functionality.'
		print self.my_graph
	

	def _check_for_leader_follower(self):
		"""
		finds leader and first follower
		returns false if graph doesnt have leader-follower-structure otherwise true
		"""
		for vertex in xrange(0, self.vertices):
			# count out degree
			d_out = np.count_nonzero(self.my_graph[vertex])
			if ( d_out == 0 ): # leader
				if ( self.leader_id is None ):
					self.leader_id = vertex 
				elif ( self.leader_id != vertex ): # found unknown leader
					# 2 leaders -> independent robots -> no structure -> not even rigid
					return False
			elif ( d_out == 1 ): # first follower
				if ( self.firstfollower_id is None ):
					self.firstfollower_id = vertex
				elif ( self.firstfollower_id != vertex ):
					# found more than one firstfollower, therefore no leader-ff-structure	
					return False
		
		if self.firstfollower_id is not None and self.leader_id is not None :
			return True
		else:
			return False

	#-----------------------#
	#  interface functions  #
	#-----------------------#	
	
	def get_size(self):
		return self.vertices
	
	def set_leader(self, ID):
		# TODO mabye change this to variable to user_leader or sth...
		self.leader_id = ID
		return
		
	def get_leader_id(self):
		"""
		if no leader is set manually, die robot with the lowest id is leader
		"""
		if self.leader_id == None :
			# TODO get lowest id to leader
			pass
		return self.leader_id
		
		
#lets test this shit
if __name__ == "__main__":

	# Adjacency matrices
	# ------------------
	#
	#  a (not rigid, uneven)			#  b (rigid)						#  c (rigid, persistent)
	# 	    A B C D E					# 	    A B C D E					# 	    A B C D E
	#                                   #  									#
	#  A    X 7 0 0 0 					#  A    X 1 0 0 1 					#  A    X 0 0 0 0
	#  B    0 X 5 2 1					#  B    1 X 1 1 0 					#  B    1 X 0 0 0
	#  C    0 5 X 4 1					#  C    0 1 X 1 1 					#  C    1 1 X 0 0
	#  D    0 2 4 X 2					#  D    0 1 1 X 1 					#  D    0 1 1 X 0
	#  E    0 1 1 2 X					#  E    1 0 1 1 X 					#  E    0 1 1 0 X

	a = np.array([[0,7,0,0,0],[7,0,5,2,1],[0,5,0,4,1],[0,2,4,0,2],[0,1,1,2,0]])
	b = np.array([[0,1,0,0,1],[1,0,1,1,0],[0,1,0,1,1],[0,1,1,0,1],[1,0,1,1,0]])
	c = np.array([[0,0,0,0,0],[1,0,0,0,0],[1,1,0,0,0],[0,1,1,0,0],[0,1,1,0,0]])
	
	g = c

	test = graph(5)
	test.set_graph(g)
	print 'get_size() =      ', test.get_size()
	print 'is_complete() =   ', test.is_complete()
	print 'is_directed() =   ', test.is_directed()
	print 'is_rigid() =      ', test.is_rigid()
	print 'is_persistent() = ', test.is_persistent()
	print 'get_leader_id() = ', test.get_leader_id()
	print g
