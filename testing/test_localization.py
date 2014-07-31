# standard imports
import numpy as np
import math
import time
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import pygraphviz as pgv
import random
import os, sys
lib_path = os.path.abspath('../')
sys.path.append(lib_path)

# project related
from constants import *
import localization as loc 


AGENTS = 4
roboID = (3112, 3139, 3140, 3306)

DIC_ANGLE_SENSORS = [ # angle(rad) : corresponding sensor
							(0.385,	2),
							(1.02, 1),
							(1.57, 0),
							(2.12, 7),
							(2.76, 6),
							(3.68, 5),
							(4.71, 4),
							(5.75, 3)]

#############################################

def create_graph(coords):
	# calculate distances and fill graph
	g = np.zeros((AGENTS,AGENTS))
	for v1 in xrange(0,AGENTS):
		for v2 in xrange(v1+1, AGENTS):
			e = round(math.sqrt((coords[v1][0]-coords[v2][0])**2 + (coords[v1][1]-coords[v2][1])**2  ),2)
			if e > 0:
				g[(v1,v2)] = e
				g[(v2,v1)] = g[(v1,v2)]
			else:
				return None
	return g

#############################################

def get_coords():
	# assign more or less random positions to {AGENTS} points in a plane
	coords = [ ( random.randint(0, 20), random.randint(0, 20) ) for k in xrange(AGENTS) ]
	return coords

#############################################

def get_orientations():
	# create orientations 0 = EAST = positive x
	o = [ (	random.uniform(0.,2*math.pi)) for k in xrange(AGENTS) ]
	return o

#############################################

def get_angles(g,c,o):
	angle = np.zeros((AGENTS,AGENTS))
	for v1 in xrange(AGENTS):
		for v2 in xrange(AGENTS):
			if v1==v2:
				angle[(v1,v2)] = -1
			else:
				a = math.atan2((c[v2][1]-c[v1][1]),(c[v2][0]-c[v1][0])) - o[v1]
				if a<0:
					a = a+2*math.pi
				angle[(v1,v2)] = a

	return angle

#############################################

def get_sensor(angle):
	if angle==-1 :
		return 9
	sensor = -1
	for x in xrange(8):
		if angle < (DIC_ANGLE_SENSORS[x][0]) :
			sensor = DIC_ANGLE_SENSORS[x][1]
			break
	if sensor == -1:
		sensor = 2
	return sensor

#############################################

def get_val_tab(angles,graph,targetID):
	val_tab = []
	for agent in xrange(AGENTS):
		val_tab = val_tab + [(roboID[agent],get_sensor(angles[(targetID, agent)]),9,round(graph[(targetID, agent)],2), 8008135)]
	return val_tab

#############################################

def create_graph_plot(c,g,o,number,name, timestr):
	A = pgv.AGraph(orientation='portrait', overlap='scale')

	# do nodes
	for v in xrange(AGENTS):
		if str(roboID[v]) == name:
			A.add_node( v,
					#pos=(str(c[v][0])+','+str(c[v][1])+'!'),
					shape='house',
					orientation=(180*math.pi/o[v]),
					label=str(roboID[v]),
					color="red"
					)
		else:
			A.add_node( v,
					#pos=(str(c[v][0])+','+str(c[v][1])+'!'),
					shape='house',
					orientation=(180*math.pi/o[v]),
					label=str(roboID[v])
					)

	# do edges
	for v1 in xrange(0,AGENTS):
		for v2 in xrange(v1+1, AGENTS):
			A.add_edge(v1,v2,label=g[(v1,v2)], len=g[(v1,v2)])

	A.layout()

	filename = timestr+"/"+str(number)+"/"+str(name)
	# A.write(filename+".dot")
	A.draw(filename+".png")

	return

#############################################

if __name__ == "__main__":

	random.seed()
	aerrors = []
	rerrors = []

	DO_PNGS = True

	if DO_PNGS:
		timestr=time.strftime("%Y%m%d-%H%M%S")
		# create folder
		if not os.path.exists(timestr):
			os.makedirs(timestr)

	# insert loop here to test more configurations	
	for k in xrange(5):
		c = get_coords()
		# get graph = groundtruth
		g = create_graph(c)
		# if we have vertices in the same place or far too close
		if ( g is None ):
			k = k-1
			continue
		# generate random orientations of the robots
		o = get_orientations()
		# get angles
		a = get_angles(g,c,o)

		# use pseudo-output for localization
		test_graphs = [loc.get_formation( None ,roboID[agent] ,get_val_tab(a,g,agent) ) for agent in xrange(AGENTS) ]

		# for every graph we got from the localization mechanism
	
		for graph in test_graphs:
			# calculate relative error of the upper right triangle of the table	
			for v1 in xrange(0,AGENTS):
				for v2 in xrange(v1+1, AGENTS):
					if (g[(v1,v2)] == 0.):
						print "g[",v1,',',v2,']=0 !'
						e = graph[(v1,v2)]
					else:
						# relative error
						re = abs( 1.- (graph[v1,v2] / g[v1,v2]) )
						# absolute error
						ae = abs( (graph[v1,v2] - g[v1,v2]) )
					if re > 0.000:
						rerrors = rerrors + [round (re,2)]
					if ae > 0.000:
						aerrors = aerrors + [round (ae,2)]
					#if e > 10:
					#	print graph
					#	print g
		if DO_PNGS:
			# do graphs
			# create folder
			if not os.path.exists(timestr+'/'+str(k)):
				os.makedirs(timestr+'/'+str(k))
			for i in xrange(AGENTS):
				create_graph_plot(c,test_graphs[i],o,k,str(roboID[i]), timestr)
			create_graph_plot(c,g,o,k,"groundtruth",timestr)

	# plt this
	plt.figure()
	plt.hist(rerrors, normed=False, facecolor='green', alpha = 0.5)
	plt.xlabel('relative error')
	plt.ylabel('occurrances')
	
	mu = round(np.mean(rerrors),3)
	sigma = round(np.std(rerrors),3)

	plt.title('relative estimation errors in '+str(k+1)+' test scenarios: $\mu='+str(mu)+'$, $\sigma='+str(sigma)+'$')

	if DO_PNGS:
		# do histogramm
		plt.savefig(timestr+'/rel_err.png')


	# plt this
	plt.figure()
	plt.hist(aerrors, normed=False, facecolor='blue', alpha = 0.5)
	plt.xlabel('absolute error')
	plt.ylabel('occurrances')
	
	mu = round(np.mean(aerrors),3)
	sigma = round(np.std(aerrors),3)

	plt.title('absolute estimation errors in '+str(k+1)+' test scenarios: $\mu='+str(mu)+'$, $\sigma='+str(sigma)+'$')

	if DO_PNGS:
		# do histogramm
		plt.savefig(timestr+'/abs_err.png')

	# plt.show()

#	print errors
	
