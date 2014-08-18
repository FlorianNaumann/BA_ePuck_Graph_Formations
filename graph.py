#standard imports
import logging
import numpy as np
import operator


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
							if self.check_for_leader_follower() and (self.my_graph[(self.firstfollower_id, self.leader_id)] != 0) :
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

		def _DFS( g, vertex_index, visited, max_depth, path=() ):

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

			vv = () # visited vertices

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

		self.graph_leader = None		

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
		self.classify_nodes()

		return True


#	I guess I wont need this:		
#
#	def get_minimally_rigid_graph(self, leader=None):
#
#		if ( self.Error ):
#			self._error_msg()
#			return None
#		
#		elif (self.min_graph is None):		
#			# get min_rigid_graph based on leader
#			# get shortest edges = risky, because one cannot assure that each robot has the same graph
#
#			self.min_graph = temp_graph
#		return self.min_graph


	def get_minimally_persistent_graph(self, leader=None):

		if ( self.Error ):
			self._error_msg()
			return None

		elif (self.min_graph == None):
			if self.is_rigid():
				# get min persistent graph based on leader
				# TODO [optional] analyse graph structure to get a better edge assignment
				# -> aquiring and maintaining persistence pp.455 construction algorithms

	#			# get leader
	#			if self.graph_leader is None:
	#				if len(self.leader_id) == 1:
	#					self.graph_leader = self.leader_id[0]
	#				else:
	#					print '[ERROR] Cannot get minimally persistent graph: leader not specified.'
	#					return None

				g = self.my_graph
				while True: # construct minimally persistent graph
					color_dict = self.classify_nodes(g)
					color_dict = self._role_reduction(color_dict)
					if ( np.count_nonzero(g) == min(g.shape)*2-3 ):
						break
					g = self._edge_reduction(color_dict, g)

				if self.check_for_leader_follower(g) == True:
					self.min_graph = g
				else:
					print 'uncontrollable!'
					# TODO [outside of my Bachelor's Thesis] what if i can't get a leader follower structure?

	#			# get firstfollower connected to the leader
	#			# remove graph_leader from firstfollower_list
	#			if self.vertices >= 2:
	#				ff_list = tuple( y for y in self.firstfollower_id if y != self.graph_leader)
	#				if len(ff_list) == 0:
	#					# no ff is preselected; get the one robot that follows the leader and has the lowest ID
	#					ff = next( i for i in xrange(self.vertices) if self.my_graph[(i,self.graph_leader)] != 0 )
	#				elif len(ff_list) == 1:
	#					ff = ff_list[0]
	#				else:
	#					print '[ERROR] cannot get minimally persistent graph: multiple firstfollowers'
	#					return None
	#			# all others can be connected to the leading robots or ones with lower ids, whatever does the 2 connections needed
	#			# connect the following robots (all robots that dont have )
	#			temp_graph = np.zeros((self.vertices, self.vertices))
	#			used_vertex = (self.graph_leader,)
	#			count = 0
	#			print "ff = ",ff
	#
	#			while len(used_vertex) != self.vertices and count != self.vertices:			
	#				count = count+1
	#				for robo in range(self.vertices):
	#					if robo in used_vertex:
	#						continue
	#					elif robo == ff: # first follower
	#						temp_graph[(robo,self.graph_leader)] = self.my_graph[(robo,self.graph_leader)]
	#						used_vertex = used_vertex + (robo,)
	#					else: # ordinary follower
	#						# assign two edges to him
	#						e = []
	#						for myleader in used_vertex :
	#							if self.my_graph[(robo, myleader)] != 0:
	#								e = e+[(robo,myleader)]
	#							if len(e) == 2: # if there are enough egdes
	#								# add vertex to graph and stop loop
	#								temp_graph[e[0]] = self.my_graph[e[0]]
	#								temp_graph[e[1]] = self.my_graph[e[1]]
	#								used_vertex = used_vertex + (robo,)
	#								break
	#				print used_vertex
	#			
	#			if count == self.vertices:
	#				print '[ERROR] cannot compute minimally persistent graph: some vertices are hard to assign'
	#				#temp_graph = None
	#				#return None
	#			self.min_graph = temp_graph
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
			self.base_graph = np.copy(self.my_graph)
			if (self.directed_edges != 0):		
				# get base_graph by mirroring undirected edges
				e=self.directed_edges;
				for x in xrange(0,self.vertices):
					for y in xrange(x+1,self.vertices):
						if (e==0):
							break
						if y==x:
							continue
						val1 = self.base_graph[(x,y)]
						val2 = self.base_graph[(y,x)]
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
	

	def check_for_leader_follower(self, graph=None):
		"""
		finds leader and first follower
		returns false if graph doesnt have leader-follower-structure otherwise true
		"""
		if (graph is None):
			graph = self.my_graph
		cd = self.classify_nodes(graph)
		cd = self._role_reduction(cd)
		
		# look for vertices with only leader attribute
		self.leader_id			= tuple( key for key in xrange(0,len(cd)) if 'l' in cd[key] )
		self.firstfollower_id	= tuple( key for key in xrange(0,len(cd)) if 'c' in cd[key] )
		
		if len(self.leader_id) == 1 and len(self.firstfollower_id) == 1:
			return True
		else:
			return False


	def classify_nodes(self, graph = None):	# EDITED HEAVILY
		if (graph == None):
			graph = self.my_graph
		color_dict = {}
		nodes = min(graph.shape)
		for vertex in xrange(0, nodes):
			# count out-degree
			d_out = np.count_nonzero(graph[vertex])
			# count in-degree
			d_in = np.count_nonzero(np.transpose(graph)[vertex])
			v_role = ()
			# classify
			if( d_in >= 2 ): # "leader"-type node
				v_role = v_role + ('l',)
			if( d_out >= 1 and d_in >= 1): # "coleader"-type node
				v_role = v_role + ('c',)
			if( d_out >= 2 ): # ordinary Follower type
				v_role = v_role + ('f',)
			# add to dictionary
			color_dict[vertex] = v_role
	
		return color_dict

	def _get_min_DOF(self, color_dict):
		minDOF = 0
		nodes = len(color_dict)
		for v in xrange(0,nodes):
			if 'f' in color_dict[v]:
				continue
			elif 'c' in color_dict[v]:
				minDOF = minDOF + 1
			elif 'l' in color_dict[v]:
				minDOF = minDOF + 2
		return minDOF

	def _role_reduction(self, color_dict):
		minDOF = self._get_min_DOF(color_dict)
		nodes = len(color_dict)
		for vertex in xrange(0, nodes):
			# get my DOF count
			myDOF = 2
			if 'c' in color_dict[vertex]:
				myDOF = 1
			if 'f' in color_dict[vertex]:
				myDOF = 0
			# skip roles that would exceed the DOF limit
			if (minDOF - myDOF) + 1 > 3:
					color_dict[vertex] = tuple( x for x in color_dict[vertex] if x!='l' and x!='c' )
			elif (minDOF - myDOF) + 2 > 3:
					color_dict[vertex] = tuple( x for x in color_dict[vertex] if x != 'l' )
		return color_dict


	def _edge_reduction(self, color_dict, graph):
		# make up costs for each node from the following rules
		# a) ff -> l  = -2
		# b) more outgoing than needed +1
		# c) double edges give +2 each
		# d) bei gleichstand: + (ziel - start)
		edge_cost = {}
		nodes = min(graph.shape)
		
		for v in xrange(0, nodes):
			d_in_blue = len([key for key in xrange(nodes) if (np.transpose(graph)[v])[key] != 0 and 'c' in color_dict[key]])
			d_out = np.count_nonzero(graph[v])
#			for role in color_dict[v]:
			for e in xrange(0, nodes):
				if graph[(v,e)] == 0:
					continue
				else:
					edge_cost[(v,e)] = 0
					# apply cost rules
					# TODO maybe choose better weights -> TIME FOR MACHINE LEARNING
					# 0) if there a incoming edges from blue nodes, all outgoing get +1					
					if ('l' in color_dict[v] ):
						edge_cost[(v,e)] = edge_cost[(v,e)] + d_in_blue					
					# a) ff -> l  = -2
					if ('c' in color_dict[v] and 'l' in color_dict[e]):
						edge_cost[(v,e)] = edge_cost[(v,e)] -2
					# b) more outgoing than needed +1
					if (('l' in color_dict[v]) and (d_out >= 1) ):
						edge_cost[(v,e)] = edge_cost[(v,e)] +2
					if (('c' in color_dict[v]) and (d_out >= 2) ):
						edge_cost[(v,e)] = edge_cost[(v,e)] +1
					if (('f' in color_dict[v]) and (d_out >= 3) ):
						edge_cost[(v,e)] = edge_cost[(v,e)] +1
					# c) double edges give +2 each
					if ( graph[(e,v)] != 0 ):
						edge_cost[(v,e)] = edge_cost[(v,e)] +2
		
		# delete edges with the highest count
		max_edges = [ key for key in edge_cost.keys() if edge_cost[key] == max(edge_cost.values()) ]

		if len(max_edges) > 1:
			# get the edge to delete by ID
			max_c = -nodes
			for e in xrange(len(max_edges)):
				c = (max_edges[e])[1] - (max_edges[e])[0]
				if c > max_c:
					del_edge = e
					max_c = c
			graph[max_edges[del_edge]] = 0
		else:
			graph[max_edges[0]] = 0

		return graph

	#-----------------------#
	#  interface functions  #
	#-----------------------#	
	
	def get_size(self):
		return self.vertices
	
	def set_leader(self, ID):
		self.graph_leader = ID
		return True
		
	def get_leader_id(self):
		"""
		if no leader is set manually, die robot with the lowest id is leader
		"""
		return self.graph_leader

	def get_agent_leader(self, myID):
		return tuple( a for a in xrange(self.vertices) if self.get_minimally_persistent_graph()[(myID,a)] != 0)

	def get_potential_leaders(self):
		"""
		return	list of nodes that can lead the formation
		rtype	tuple
		"""

		l_list = ()

		cd = self.classify_nodes(self.get_minimally_persistent_graph())
		cd = self._role_reduction(cd)

		l_list = tuple( key for key in xrange(0,len(cd)) if 'l' in cd[key] )

#		if self.is_rigid(): # filtering rigid cases, so we dont need to care about cases with more than 1 leader
#			if len(self.leader_id) == 0:
#				if   len(self.firstfollower_id) == 0:
#					l_list = self.follower_id
#				elif len(self.firstfollower_id) == 1:
#					l_list = self.firstfollower_id + ( next( i for i, e in enumerate( self.my_graph[self.firstfollower_id[0]] ) if e!= 0 ), )
#				elif len(self.firstfollower_id) >= 2:
#					# best leaders are the firstfollowers that are followed by others
#					ff_leaders = ()
#					for ff in self.firstfollower_id:
#						ff_leaders = ff_leaders + (next( i for i, e in enumerate( self.my_graph[ff] ) if e!= 0 ),)
#					l_list = tuple( i for i in ff_leaders if i in self.firstfollower_id )
#					if len(l_list)==0:
#						l_list = self.firstfollower_id
#			elif len(self.leader_id) == 1:
#				if   len(self.firstfollower_id) == 0:
#					l_list = self.leader_id
#				elif len(self.firstfollower_id) == 1:
#					# does the one firstfollower follower the one leader?
#					if ( self.my_graph[(self.firstfollower_id[0],self.leader_id[0])] != 0 ):
#					#	yes:	the leader is the best potential leader
#						l_list = self.leader_id
#					else:						
#					#	no:		-> problem: not all robots can be controlled as one formation;
#					#						potential leaders can be: the leader, the FirstF, the robot being followed by the FirstF
#						l_list = self.leader_id + self.firstfollower_id + (next( i for i, e in enumerate( self.my_graph[self.firstfollower_id[0]] ) if e!= 0 ),)
#				elif len(self.firstfollower_id) >= 2:
#					# target of the firstfollowers can be leaders, best case: one of the leaders or FF's is being followed by a FF
#					for ff in self.firstfollower_id:
#						ff_leaders = ff_leaders + (next( i for i, e in enumerate( self.my_graph[ff] ) if e!= 0 ),)
#					l_list = tuple( i for i in ff_leaders if i in self.firstfollower_id or i in self.leader_id)
#					if len(l_list)==0:
#						l_list = self.firstfollower_id + self.leader_id
#			else:
#				l_list = self.leader_id
#				# else there are more than 2 leaders and the formation is not rigid as a whole
#				# cases if there are more than 2 leaders (non rigid cases)

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
	
	# test cases
	l1 = np.array([[0,0,1,0,0],[0,0,1,0,1],[0,1,0,1,0],[1,0,1,0,0],[0,0,1,1,0]])
	l2 = np.array([[0,1,0,0,1],[1,0,1,0,1],[0,0,0,1,0],[0,1,1,0,0],[0,0,1,1,0]])
	l3 = np.array([[0,0,0,0,0],[0,0,0,1,1],[0,1,0,1,0],[1,0,0,0,0],[1,0,0,1,0]])
	l4 = np.array([[0,1,0,0,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,0],[1,0,0,1,0]])
	l5 = np.array([[0,1,0,0,1],[0,0,0,1,1],[1,1,0,0,0],[1,0,1,0,0],[0,0,1,1,0]])
	l6 = np.array([[0,1,1,0,0],[0,0,1,0,1],[0,1,0,1,0],[1,0,0,0,0],[0,1,1,0,0]])
	l6b = np.array([[0,1,1,0],[0,0,1,0],[0,1,0,1],[1,0,0,0]]) # without the last vertex

	l7 = np.array([[0,0,0,0,0],[0,0,0,0,0],[1,0,0,1,1],[1,1,0,0,0],[1,1,0,0,0]])

	g = l4

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

	ll = test.get_potential_leaders()
	print 'get_potential_leaders() = ', ll
#	print 'set_leader(',ll[0],') = ', test.set_leader(ll[0])
	print 'get_min_pers_graph() =', test.get_minimally_persistent_graph()

	print g

