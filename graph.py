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
		
		self.set_graph(zeros((vertices, vertices)))


	def __getitem__(self, index):
		return self.my_graph[index]


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
				if ( self.is_directed() ):
					if ( self.vertices < 4 ) :
						self.graph_is_persistent = True
					else:
						# test for cycle-free
						if self.is_cycle_free():
							# ~~~~~ test for constraint consistence ~~~~~ #
							# --- simple test for cycle-free or leader-follower structured graphs ---
							# step 1) find the one leader (out-degree of 0)
							# step 2) indentify the coleader (out-degree of 1 AND connection to the leader)
							# step 3) every other vertex has to have at least 2 outgoing edges
							if self.check_for_leader_follower() :
								#TODO check for functionality
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
		
	
	def is_cycle_free(self):

		def _DFS( g, vertex_index, visited, max_depth, path=(None,) ):

			path = path + (vertex_index,)
			visited = visited + (vertex_index,)

			if max_depth>0: # if a deeper search is allowed
				for vi2 in xrange(self.vertices): # then look for all outgoing connections
					if( g[vertex_index][vi2] > 0 ):
						if (vi2 in path): # cycle detected
							return False
						elif (vi2 not in visited): # cycle detected
							visited = _DFS( g, vi2, visited, max_depth-1, path )
							if visited == False :
								break
			return visited

		if self.acyclic == None :
			self.acyclic = True
			# test for cycles with modified Tarjan's Algorithm (DFS)

			vv = (None,) # visited vertices

			for v in xrange(self.vertices):	
				if ( v not in vv ):		
					nv = _DFS(self.my_graph,v,vv,self.vertices)
					if nv == False: # found cycle
						self.acyclic = False
						break
					else:
						vv = nv
		
		return self.acyclic


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
		
		# reset some stored graphs
		self.min_graph  = None
		self.base_graph = None
		
		# reset node classifications
		self.leader_id				= ()
		self.firstfollower_id		= ()
		self.follower_id			= ()

		# reset saved properties		
		self.acyclic				= None
		self.graph_is_rigid         = None
		self.graph_is_persistent    = None
		
		# do initial counting
		self._get_number_of_edges()
		self._classify_nodes()

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
	

	def check_for_leader_follower(self):
		"""
		finds leader and first follower
		returns false if graph doesnt have leader-follower-structure otherwise true
		"""

		if len(self.firstfollower_id) == 1 and len(self.leader_id) == 1 :
			return True
		else:
			return False



	def _classify_nodes(self):
		for vertex in xrange(0, self.vertices):
			# count out degree
			d_out = np.count_nonzero(self.my_graph[vertex])
			#classify
			if   ( d_out == 0 ): # "leader"-type node
				self.leader_id = self.leader_id + (vertex,)
			elif ( d_out == 1 ): # "first follower"-type node
				self.firstfollower_id = self.firstfollower_id + (vertex,)
			else: # ordinary Follower type
				self.follower_id= self.follower_id + (vertex,)
		return

	#-----------------------#
	#  interface functions  #
	#-----------------------#	
	
	def get_size(self):
		return self.vertices
	
	def set_leader(self, ID):
		# TODO mabye change this variable to user_leader or sth...
		# self.leader_id = (ID,)
		return
		
	def get_leader_id(self):
		"""
		if no leader is set manually, die robot with the lowest id is leader
		"""
		if len(self.leader_id) != 1 :
			return None
		return self.leader_id

	def get_potential_leaders(self):
		"""
		return	list of nodes that can lead the formation
		rtype	tupel
		"""
		# TODO the return type is currently not always a tuple; sometimes its a list... someone should fix this

		l_list = ()

		if self.is_rigid() or True: #TODO remove always true
			if len(self.leader_id) == 0:
				if   len(self.firstfollower_id) == 0:
					l_list = self.follower_id
				elif len(self.firstfollower_id) == 1:
					l_list = self.firstfollower_id + ( next( i for i, e in enumerate( self.my_graph[self.firstfollower_id[0]] ) if e!= 0 ), )
				elif len(self.firstfollower_id) >= 2:
					# best leaders are the firstfollowers that are followed by others
					ff_leaders = ()
					for ff in self.firstfollower_id:
						ff_leaders = ff_leaders + (next( i for i, e in enumerate( self.my_graph[ff] ) if e!= 0 ),)
					l_list = [ i for i in ff_leaders if i in self.firstfollower_id ]
					if len(l_list)==0:
						l_list = self.firstfollower_id
			elif len(self.leader_id) == 1:
				if   len(self.firstfollower_id) == 0:
					l_list = self.leader_id
				elif len(self.firstfollower_id) == 1:
					# does the one firstfollower follower the one leader?
					if ( self.my_graph[(self.firstfollower_id[0],self.leader_id[0])] != 0 ):
					#	yes:	the leader is the best potential leader
						l_list = self.leader_id
					else:						
					#	no:		-> problem: not all robots can be controlled as one formation;
					#						potential leaders can be: the leader, the FirstF, the robot being followed by the FirstF
						l_list = self.leader_id + self.firstfollower_id + (next( i for i, e in enumerate( self.my_graph[self.firstfollower_id[0]] ) if e!= 0 ),)
				elif len(self.firstfollower_id) >= 2:
					# target of the firstfollowers can be leaders, best case: one of the leaders or FF's is being followed by a FF
					for ff in self.firstfollower_id:
						ff_leaders = ff_leaders + (next( i for i, e in enumerate( self.my_graph[ff] ) if e!= 0 ),)
					l_list = [ i for i in ff_leaders if i in self.firstfollower_id or i in self.leader_id]
					if len(l_list)==0:
						l_list = self.firstfollower_id + self.leader_id
			else:
				l_list = self.leader_id
				# else there are more than 2 leaders and the formation is not rigid as a whole
				# TODO cases if there are more that 2 leaders

		return l_list
		
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

	a  = np.array([[0,7,0,0,0],[7,0,5,2,1],[0,5,0,4,1],[0,2,4,0,2],[0,1,1,2,0]])
	b  = np.array([[0,1,0,0,1],[1,0,1,1,0],[0,1,0,1,1],[0,1,1,0,1],[1,0,1,1,0]])
	c  = np.array([[0,0,0,0,0],[1,0,0,0,0],[1,1,0,0,0],[0,1,1,0,0],[0,1,1,0,0]])
	d  = np.array([[0]])
	
	l1 = np.array([[0,0,1,0,0],[0,0,1,0,1],[0,1,0,1,0],[1,0,1,0,0],[0,0,1,1,0]])
	l2 = np.array([[0,1,0,0,1],[1,0,1,0,1],[0,0,0,1,0],[0,1,1,0,0],[0,0,1,1,0]])
	l3 = np.array([[0,0,0,0,0],[0,0,0,1,1],[0,1,0,1,0],[1,0,0,0,0],[1,0,0,1,0]])
	l4 = np.array([[0,1,0,0,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,0],[1,0,0,1,0]])


	g = l1

	test = graph(5)
	test.set_graph(g)
	print 'get_size() =      ', test.get_size()
	print 'is_complete() =   ', test.is_complete()
	print 'is_directed() =   ', test.is_directed()
	print 'is_rigid() =      ', test.is_rigid()
	print 'is_cycle_free() = ', test.is_cycle_free()
	print 'is_persistent() = ', test.is_persistent()
	print 'get_leader_id() = ', test.get_leader_id()
	print 'f_ids	= ', test.follower_id
	print 'ff_ids	= ', test.firstfollower_id

	print 'get_potential_leaders() = ', test.get_potential_leaders()

	print g
