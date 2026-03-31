from abc import ABC, abstractmethod
import random


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


class MagicWandAbility(Ability):
	"""Magic wand ability - fills 3-5 random empty cells on the grid."""
	def __init__(self, min_fill=3, max_fill=5):
		super().__init__("Magic Wand")
		self.min_fill = max(1, min_fill)
		self.max_fill = max(self.min_fill, max_fill)

	def activate(self, game):
		"""Fill holes along current gravity direction and consume the ability."""
		if not game.has_magic_wand:
			return False

		gravity_step = game.get_gravity_step()

		occupied_by_current = set()
		for tile in game.current_block.get_cell_positions():
			if game.grid.is_inside(tile.row, tile.column):
				occupied_by_current.add((tile.row, tile.column))

		empty_cells = []
		hole_cells = []
		for row in range(game.grid.num_rows):
			for col in range(game.grid.num_cols):
				if game.grid.grid[row][col] == 0 and (row, col) not in occupied_by_current:
					empty_cells.append((row, col))
					# Hole direction follows gravity: normal uses cells above, inverted uses cells below.
					if gravity_step >= 0:
						for above_row in range(0, row):
							if game.grid.grid[above_row][col] != 0:
								hole_cells.append((row, col))
								break
					else:
						for below_row in range(row + 1, game.grid.num_rows):
							if game.grid.grid[below_row][col] != 0:
								hole_cells.append((row, col))
								break

		if not empty_cells:
			return False

		fill_count = min(random.randint(self.min_fill, self.max_fill), len(empty_cells))

		# Prefer real holes first; if none exist, use all empty cells.
		target_cells = hole_cells if hole_cells else empty_cells

		# Fill from the gravity destination side first.
		cells_by_row = {}
		for row, col in target_cells:
			if row not in cells_by_row:
				cells_by_row[row] = []
			cells_by_row[row].append((row, col))

		ordered_cells = []
		row_order = sorted(cells_by_row.keys(), reverse=(gravity_step >= 0))
		for row in row_order:
			row_cells = cells_by_row[row]
			random.shuffle(row_cells)
			ordered_cells.extend(row_cells)

		chosen = ordered_cells[:fill_count]

		for row, col in chosen:
			game.grid.grid[row][col] = random.randint(1, 7)

		rows_cleared = game.grid.clear_full_rows(gravity_step=gravity_step)
		if rows_cleared > 0:
			# Keep scoring behavior identical to normal line clears.
			game.update_score(rows_cleared, 0)

		game.lock_flash_effect.trigger(chosen, color=(200, 160, 255), flashes=2, duration_ms=220)
		game.magic_wand_effect.trigger(chosen)
		if rows_cleared > 0:
			game.last_event_text = (
				f"Magic Wand filled {fill_count} cell{'s' if fill_count > 1 else ''} and cleared "
				f"{rows_cleared} row{'s' if rows_cleared > 1 else ''}!"
			)
		else:
			game.last_event_text = f"Magic Wand filled {fill_count} cell{'s' if fill_count > 1 else ''}!"
		game.last_event_timer = 90
		self.deactivate(game)
		return True

	def deactivate(self, game):
		self.is_active = False
		game.has_magic_wand = False
