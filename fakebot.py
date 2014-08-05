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

	def get_rel_pos(self):
		return self.val_tup

	def enable(self, char):
		return char
