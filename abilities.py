from abc import ABC, abstractmethod


class Ability(ABC):
	"""Base class for all abilities"""
	def __init__(self, name):
		self.name = name
		self.is_active = False
	
	@abstractmethod
	def activate(self, game):
		"""Activate the ability - implemented by subclasses"""
		pass
	
	@abstractmethod
	def deactivate(self, game):
		"""Deactivate the ability - implemented by subclasses"""
		pass


class BombAbility(Ability):
	"""Bomb ability - next block becomes a single square that explodes on collision"""
	def __init__(self):
		super().__init__("Bomb")
		self.bomb_radius = 2  # Explosion radius in blocks
	
	def activate(self, game):
		"""Activate bomb - next block will be a bomb block"""
		self.is_active = True
		game.bomb_active = True
	
	def deactivate(self, game):
		"""Deactivate bomb after use"""
		self.is_active = False
		game.bomb_active = False
	
	def explode(self, grid, center_row, center_col):
		"""
		Trigger bomb explosion at the given center position.
		Removes blocks in a circular pattern around the center.
		
		Args:
			grid: The game grid
			center_row: Row position of bomb center
			center_col: Column position of bomb center
		"""
		# Define bomb explosion pattern (relative positions)
		explosion_pattern = [
			(0, 0),    # center
			(-1, 0), (1, 0), (0, -1), (0, 1),  # adjacent cells (cross)
			(-1, -1), (-1, 1), (1, -1), (1, 1),  # diagonals
			(-2, 0), (2, 0), (0, -2), (0, 2),  # extended cross
		]
		
		# Remove blocks in explosion area
		for row_offset, col_offset in explosion_pattern:
			target_row = center_row + row_offset
			target_col = center_col + col_offset
			
			if grid.is_inside(target_row, target_col):
				grid.grid[target_row][target_col] = 0
		
		# Clear rows that might have been completed
		grid.clear_full_rows()
