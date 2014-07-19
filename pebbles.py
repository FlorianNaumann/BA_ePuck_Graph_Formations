from numpy import *

DEBUG = False

def pebble_algorithm(adjacency_matrix):

	if not (type(adjacency_matrix).__module__ == 'numpy' and type(adjacency_matrix).__name__ == 'ndarray'):
		return False

	# ------------- intialization --------------
	# get number of nodes
	nodes = min(adjacency_matrix.shape)
	# get an empty table
	pebtab = zeros((nodes,nodes))
	edges=0
	
	# ------------- looplooplooop --------------
	# loop through all possible edges
	
	for v1 in xrange(0, nodes):
		for v2 in xrange(v1+1, nodes):
			# pick new edge
			edge = (v1, v2)
			# check if that edge is part of the graph
			if adjacency_matrix[edge]<=0:
				continue
			
			add_edge = True
			new_pebtab = pebtab
			
			# check if we have 2 free pebbles at each end of the edge
			for vertex in edge:
				while _number_of_free_pebbles(pebble_table=new_pebtab, vertex_index=vertex) < 2 :
					# can I move more pebbles to that edge?
					swap_path = _search_for_pebbles(pebble_table=new_pebtab, vertex_index=vertex, edge=edge)
					if ( swap_path == None ):
						# No pebbles can be moved to that vertex => edge cannot be added
						add_edge = False
						break
					else:
						new_pebtab = _rearrange_pebbles(pebble_table=new_pebtab, vertex_index=vertex, path=swap_path)
			
				# skip second vertex if first one can't have 2 pebbles
				if(add_edge == False):
					break
			
			if(add_edge == True):
				# add edge
				#if(DEBUG):
				#	print 'inserted edge ',edge
				edges=edges+1
				new_pebtab[edge] = 1
				pebtab = new_pebtab
				
	# ------------- end of loop --------------
		
	if(DEBUG):
		print(pebtab)
	
	# check for laman condition
	if ( edges == 2*nodes-3 ):
		return True #is rigid
	else:
		return False #is flexible
	
	
def _number_of_free_pebbles(pebble_table, vertex_index):
	if (vertex_index < pebble_table.shape[0]) :
		return 2-( pebble_table[vertex_index].sum() )
	else:
		return None

def _search_for_pebbles(pebble_table, vertex_index, edge):
	"""
	doing a depth first search along the already established edges
	
	@return: path or None		
	"""
	def _DFS( pebble_table, vertex_index, edge, max_depth ):
		path=None
		
		if max_depth>0: # if a deeper search is allowed
			for vi2 in xrange(pebble_table.shape[0]): # then look for all connections
				if( pebble_table[vertex_index][vi2] > 0 ):
					if (vi2 in edge): # skip connections to the new edge vertices
						continue
					if( _number_of_free_pebbles(pebble_table, vi2) > 0 ):
						path = (vi2,)
					else:
						path = _DFS( pebble_table, vi2, edge, max_depth-1 )
					if (path != None):
						return path+(vertex_index,)
		
		return path
			
	max_depth = 7
	path = _DFS( pebble_table, vertex_index, edge, max_depth )
	
	return path
		
def _rearrange_pebbles(pebble_table, vertex_index, path):
	"""
	@return:	rearranged pebble_table or None if cannot be rearranged accordingly
	"""
	
	for i in xrange(1,len(path)):
		#if(DEBUG):
		#	print 'flipping edge', path[i-1],path[i]
		pebble_table[(path[i-1],path[i])] = 1
		pebble_table[(path[i],path[i-1])] = 0
	
	return pebble_table
	
	
#lets test this shit
if __name__ == "__main__":

	DEBUG = True
	
	# Adjacency matrices
	# ------------------
	#
	#  a (not rigid, uneven)			#  b (rigid)
	# 	    A B C D E					# 	    A B C D E
	#                                   #  
	#  A    X 7 0 0 0 					#  A    X 1 0 0 1
	#  B    1 X 5 2 1					#  B    1 X 1 1 0
	#  C    0 5 X 4 1					#  C    0 1 X 1 1
	#  D    0 2 4 X 2					#  D    0 1 1 X 1
	#  E    0 1 1 2 X					#  E    1 0 1 1 X

	a = array([[0,7,0,0,0],[1,0,5,2,1],[0,5,0,4,1],[0,2,4,0,2],[0,1,1,2,0]])
	b = array([[0,1,0,0,1],[1,0,1,1,0],[0,1,0,1,1],[0,1,1,0,1],[1,0,1,1,0]])
	
	print 'test a on rigidity'
	print pebble_algorithm(a)
	print 'test b on rigidity'
	print pebble_algorithm(b)
