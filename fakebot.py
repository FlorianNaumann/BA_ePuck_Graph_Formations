# fakerobot

class ePuck():
	
	def __init__(self, PIN=3112, val_tup = None):
		self.myPin = PIN
		self.val_tup = val_tup
		return

	def connect(self):
		return True

	def get_btPin(self):
		return self.myPin

	def step(self):
		return

	def set_rel_pos(self, new_val_tup):
		self.val_tup = new_val_tup
		return

	def get_rel_pos(self):
		return self.val_tup

	def enable(self, char):
		return char

	def set_motors_speed(self, lmotor, rmotor):
		self.left_motor = lmotor
		self.right_motor = rmotor

	def get_motors_speed(self):
		return (self.left_motor, self.right_motor)
