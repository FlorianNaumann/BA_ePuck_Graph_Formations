#constants

#MY_BT     = 1321  # not needed anymore
MAX_SPD   =  500
MIN_ERROR =    5

WHEEL_DISTANCE = 5.3 # cm

# data taken from http://www.cyberbotics.com/dvd/common/doc/webots/guide/section8.1.html table8.4
DICT_SENSOR_ANGLES = { # sensor_no : angle from the front of the robot in rad
							0	   :	1.27,	#5.98	,	# 1.27
							1	   :	0.77,	#5.48	,	# 0.77
							2	   :	0.00,	#4.71	,	# 0.00
							3	   :	5.21,	#3.64	,	# 5.21
							4	   :	4.21,	#2.64	,	# 4.21
							5	   :	3.14159,#1.57	,	# 3.14159
							6	   :	2.37,	#0.80	,	# 2.37
							7	   :	1.87,	#0.30	,	# 1.87
							9	   :	 -1     }   # unrecognized angle
