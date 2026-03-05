from grid import Grid
from blocks import *
from abilities import BombAbility
import random

class Game:
	def __init__(self):
		self.grid = Grid()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
		self.next_block = self.get_random_block()
		self.game_over = False
		self.score = 0
		self.time_left = 120
		
		# Ability system
		self.bomb_ability = BombAbility()
		self.bomb_active = False  # Flag indicating bomb is active for next block
		self.has_bomb = False  # Flag indicating player owns bomb ability
		self.last_block_position = None  # Track position of last locked block for bomb explosion

	def update_score(self, lines_cleared, move_down_points):
		if lines_cleared == 1:
			self.score += 100 
		elif lines_cleared == 2:
			self.score += 300
		elif lines_cleared == 3:
			self.score += 500
		elif lines_cleared == 4:
			self.score += 1000
		self.score += move_down_points
	
	def get_random_block(self):
		if len(self.blocks) == 0:
			self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		block = random.choice(self.blocks)
		self.blocks.remove(block)
		return block
	
	def move_left(self):
		self.current_block.move(0, -1)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(0, 1)
	def move_right(self):
		self.current_block.move(0, 1)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(0, -1)
	def move_down(self):
		self.current_block.move(1, 0)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(-1, 0)
			self.lock_block()

	def hard_drop(self):
		while self.block_inside() and self.block_fits():
			self.current_block.move(1, 0)
			if not self.block_inside() or not self.block_fits():
				self.current_block.move(-1, 0)
				self.lock_block()
				break
		
		self.update_score(0, 2)

	def lock_block(self):
		tiles = self.current_block.get_cell_positions()
		
		# Check if current block is a bomb block - if so, trigger explosion
		if self.current_block.id == 8:  # BombBlock has id 8
			# Get the center position of the bomb (should be single cell)
			if tiles:
				bomb_pos = tiles[0]
				self.grid.bomb_explosion(bomb_pos.row, bomb_pos.column)
			self.has_bomb = False
			self.bomb_active = False
		else:
			# Normal block locking
			for position in tiles:
				self.grid.grid[position.row][position.column] = self.current_block.id
		
		# Set position for potential bomb explosion tracking
		if tiles:
			self.last_block_position = tiles[0]
		
		self.current_block = self.next_block
		self.next_block = self.get_next_block()
		rows_cleared = self.grid.clear_full_rows()
		
		if rows_cleared > 0:
			self.update_score(rows_cleared, 0)
			# Grant bomb ability on Tetris (4 row clear)
			if rows_cleared == 4:
				self.has_bomb = True
		
		if self.block_fits() == False:
			self.game_over = True
	
	def get_next_block(self):
		"""Get the next block - either a BombBlock if bomb is active, or a regular block"""
		if self.bomb_active:
			return BombBlock()
		else:
			return self.get_random_block()
	
	def use_bomb_ability(self):
		"""Activate the bomb ability for the next block"""
		if self.has_bomb and not self.bomb_active:
			self.bomb_ability.activate(self)
			return True
		return False
	
	def reset(self):
		self.grid.reset()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.get_random_block()
		self.next_block = self.get_random_block()
		self.score = 0
		self.time_left = 120
		self.bomb_active = False
		self.has_bomb = False
		self.last_block_position = None

	def block_fits(self):
		tiles = self.current_block.get_cell_positions()
		for tile in tiles:
			if self.grid.is_empty(tile.row, tile.column) == False:
				return False
		return True

	def rotate(self):
		self.current_block.rotate()
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.undo_rotation()

	def block_inside(self):
		tiles = self.current_block.get_cell_positions()
		for tile in tiles:
			if self.grid.is_inside(tile.row, tile.column) == False:
				return False
		return True
	
	def draw(self, screen):
		self.grid.draw(screen)
		if self.game_over == False:
			self.current_block.draw(screen, 11, 11)

		if self.next_block.id == 3:
			self.next_block.draw(screen, 250, 260)
		elif self.next_block.id == 4:
			self.next_block.draw(screen, 250, 245)
		elif self.next_block.id == 8:  # BombBlock
			self.next_block.draw(screen, 295, 290)
		else:
			self.next_block.draw(screen, 265, 240)

	def countdown(self):
		if self.game_over:
			return
		if self.time_left > 0:
			self.time_left -= 1
		if self.time_left <= 0:
			self.time_left = 0
			self.game_over = True

	def get_time_text(self):
		mins, secs = divmod(self.time_left, 60)
		return f"{mins:02d}:{secs:02d}"