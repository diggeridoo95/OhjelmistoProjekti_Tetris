
from blocks import *
import random

class Game:
	def __init__(self):

		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
	
	def get_random_block(self):
		return random.choice(self.blocks)

	def draw(self, screen):
		self.current_block.draw(screen, 11, 11)