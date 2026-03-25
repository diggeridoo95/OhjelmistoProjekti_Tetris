from grid import Grid
from blocks import *
from abilities import BombAbility, MagicWandAbility
from levels import get_levels
from inversion import InversionController
from bomb_icon import draw_bomb_cell
from effects import SpeedLines, CellFlashEffect, MagicWandEffect, MolePopEffect, BombExplosionEffect, InversionFlashEffect
import random
import pygame


class Game:
	def __init__(self):
		self.grid = Grid()
		self.grid_offset_x = 11
		self.grid_offset_y = 11
		self.next_preview_rect = pygame.Rect(315, 185, 170, 180)
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		
		# pelikentän peilauksen määritykset 
		#JOS HALUAT TESTATA ILMAN PEILAUSTA, ASETU TÄMÄN ARVOKSI 999
		self.inversion = InversionController(interval_seconds=10, lock_target=3) 
		
		self.current_block = self.spawn_current_block(self.get_random_block())
		self.next_block = self.get_random_block()
		self.game_over = False
		self.game_won = False
		self.score = 0
		self.levels = get_levels()
		self.current_level_index = 0
		self.current_level = self.levels[0]
		self.level_start_score = 0
		self.time_left = self.current_level.time_limit_seconds
		self.drop_interval_ms = self.current_level.drop_interval_ms
		self.speed_changed = False
		self.level_transition_duration_ms = 1800
		self.level_transition_ms_left = 0
		self.pending_level_index = None
		self.invisible_until_ms = 0
		self.last_event_text = ""
		self.last_event_timer = 0
		self.hard_drop_lines = SpeedLines()
		self.lock_flash_effect = CellFlashEffect()
		self.row_clear_flash_effect = CellFlashEffect(duration_ms=320, flashes=2)
		self.magic_wand_effect = MagicWandEffect()
		self.mole_pop_effect = MolePopEffect()
		self.bomb_explosion_effect = BombExplosionEffect()
		self.inversion_flash_effect = InversionFlashEffect()
		
		
		# Ability system
		self.bomb_ability = BombAbility()
		self.magic_wand_ability = MagicWandAbility()
		self.bomb_active = False  # Flag indicating bomb is active for next block
		self.has_bomb = False  # Flag indicating player owns bomb ability
		self.has_magic_wand = False  # Flag indicating player owns magic wand ability
		self.last_block_position = None  # Track position of last locked block for bomb explosion

		#self.apply_level(1)  # Start at level 2 for testing purposes
							#Can be adjusted for further testing

	def get_level_score(self):
		return max(0, self.score - self.level_start_score)

	def is_level_transitioning(self):
		return self.pending_level_index is not None

	def start_level_transition(self, next_level_index):
		self.pending_level_index = next_level_index
		self.level_transition_ms_left = self.level_transition_duration_ms

	def apply_level(self, level_index):
		# Preserve unused abilities when moving to next level.
		preserved_has_bomb = self.has_bomb
		preserved_bomb_active = self.bomb_active
		preserved_has_magic_wand = self.has_magic_wand

		self.current_level_index = level_index
		self.current_level = self.levels[self.current_level_index]
		self.level_start_score = self.score
		self.time_left = self.current_level.time_limit_seconds
		self.drop_interval_ms = self.current_level.drop_interval_ms
		self.speed_changed = True
		
		# Reset inversion event state when level changes
		self.inversion.reset_state()

		self.grid.reset()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.spawn_current_block(self.get_random_block())
		self.next_block = self.get_next_block()

		self.has_bomb = preserved_has_bomb
		self.bomb_active = preserved_bomb_active
		self.has_magic_wand = preserved_has_magic_wand

		for event in self.current_level.events:
			event.on_level_start(self)

	def update_level_events(self):		#Update active level events

		if self.game_over or self.is_level_transitioning():
			return
		
		for event in self.current_level.events: 		#Call on_tick for events that have it
			if hasattr(event, "on_tick"):
				event.on_tick(self)
		
		if self.last_event_timer > 0:
			self.last_event_timer -= 1
		elif self.last_event_timer < 0:		#Safety check to prevent negative timer values
			self.last_event_timer = 0

	def update_level_transition(self, elapsed_ms):
		if self.is_level_transitioning() == False or self.game_over:
			return

		self.level_transition_ms_left -= elapsed_ms
		if self.level_transition_ms_left <= 0:
			next_level_index = self.pending_level_index
			self.pending_level_index = None
			self.level_transition_ms_left = 0
			self.apply_level(next_level_index)

	def try_advance_level(self):
		if self.game_over or self.is_level_transitioning():
			return False
		
		if self.time_left > 0:
			return False

		if self.get_level_score() < self.current_level.target_score:
			return False

		if self.current_level_index >= len(self.levels) - 1:
			self.game_won = True
			self.game_over = True
			return True

		self.start_level_transition(self.current_level_index + 1)
		return True

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
		self.try_advance_level()
	
	def get_random_block(self):
		if len(self.blocks) == 0:
			self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		block = random.choice(self.blocks)
		self.blocks.remove(block)
		return block

	# ===== Inverted Gravity Event Delegation =====
	def get_gravity_step(self):
		"""Returns gravity direction from inversion controller."""
		return self.inversion.get_gravity_step()

	def update_inversion_event_timer(self):
		"""Updates inversion event timer; inversion is applied at next spawn."""
		self.inversion.update_timer()

	def spawn_current_block(self, block):
		"""Spawns a block using inversion-aware spawn rules."""
		if self.inversion.apply_pending_activation(self.grid):
			self.lock_flash_effect.remap_vertical_flip(self.grid.num_rows)
			self.bomb_explosion_effect.remap_vertical_flip(self.grid.num_rows)
			self.inversion_flash_effect.trigger()
		return self.inversion.spawn_block(block, self.grid)
	
	def move_left(self):
		self.current_block.move(0, -1)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(0, 1)
	def move_right(self):
		self.current_block.move(0, 1)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(0, -1)
	
	def move_down(self):
		"""Drop block one step (direction depends on gravity)"""
		step = self.get_gravity_step()  # +1 normal, -1 inverted
		self.current_block.move(step, 0)
		if self.block_inside() == False or self.block_fits() == False:
			self.current_block.move(-step, 0)  # Undo move and lock
			self.lock_block()

	def hard_drop(self):
		"""Instantly drop block to bottom (respects gravity direction)"""
		step = self.get_gravity_step()  # +1 normal, -1 inverted
		drop_distance = 0
		while self.block_inside() and self.block_fits():
			self.current_block.move(step, 0)
			if not self.block_inside() or not self.block_fits():
				self.current_block.move(-step, 0)  # Move back one step
				break
			drop_distance += 1

		if drop_distance > 0:
			self.hard_drop_lines.trigger(
				self.current_block.get_cell_positions(),
				drop_distance,
				self.grid.num_rows,
				step,
				self.current_block.colors[self.current_block.id],
			)
		self.lock_block()

		
		self.update_score(0, 2)

	def lock_block(self):
		tiles = self.current_block.get_cell_positions()
		flash_cells = []
		
		# Check if current block is a bomb block - if so, trigger explosion
		if self.current_block.id == 8:  # BombBlock has id 8
			# Get the center position of the bomb (should be single cell)
			if tiles:
				bomb_pos = tiles[0]
				if self.grid.is_inside(bomb_pos.row, bomb_pos.column):
					affected_cells = self.grid.bomb_explosion(
					    bomb_pos.row,
					    bomb_pos.column,
					    gravity_step=self.get_gravity_step(),
					)
					self.bomb_explosion_effect.trigger(affected_cells)
			self.has_bomb = False
			self.bomb_active = False
		else:
			# Normal block locking
			for position in tiles:
				if self.grid.is_inside(position.row, position.column):
					flash_cells.append((position.row, position.column))
					self.grid.grid[position.row][position.column] = self.current_block.id

			if flash_cells:
				self.lock_flash_effect.trigger(flash_cells)#tähän voi määrittää halutessaan eri ajan, värin, keston yms.
		
		# Set position for potential bomb explosion tracking
		if tiles:
			self.last_block_position = tiles[0]

		
		full_rows = self.grid.get_full_rows()

		if full_rows:
			row_flash_cells = [
				(row, col)
				for row in full_rows
				for col in range(self.grid.num_cols)
			]

			self.row_clear_flash_effect.trigger(
				row_flash_cells,
				color=(255, 240, 120),
				flashes=3,
				duration_ms=340,
			)
		

		rows_cleared = self.grid.clear_full_rows(gravity_step=self.get_gravity_step())

		if rows_cleared > 0:

			#self.lock_flash_effect.clear() #jos ei haluta välähdystä silloin, kun rivi poistuu
			self.update_score(rows_cleared, 0)
			# Grant bomb ability on Tetris (4 row clear)
			if rows_cleared == 1 or rows_cleared == 2 or rows_cleared == 3 or rows_cleared == 4:
				self.has_bomb = True
			# Grant magic wand on 3-line clear
			if rows_cleared == 3:
				self.has_magic_wand = True

		# Let inversion controller track lock count and auto-disable event
		if self.inversion.on_block_locked(self.grid):
			self.lock_flash_effect.remap_vertical_flip(self.grid.num_rows)
			self.bomb_explosion_effect.remap_vertical_flip(self.grid.num_rows)
			self.inversion_flash_effect.trigger()  # Flash when inversion deactivates

		self.current_block = self.spawn_current_block(self.next_block)
		self.next_block = self.get_next_block()
		
		if self.block_fits() == False:
			self.game_over = True
	
	def get_next_block(self):
		"""Get a regular random next block. Bomb is injected explicitly when ability is used."""
		return self.get_random_block()
	
	def use_bomb_ability(self):
		"""Activate bomb and replace the currently queued next block with one bomb block."""
		if self.has_bomb and not self.bomb_active:
			self.bomb_ability.activate(self)
			self.next_block = BombBlock()
			return True
		return False

	def use_magic_wand_ability(self):
		"""Use magic wand ability immediately."""
		if not self.has_magic_wand:
			return False
		return self.magic_wand_ability.activate(self)
	
	def reset(self):
		self.grid.reset()
		# Reset inversion state before spawning the first block.
		self.inversion.reset_state()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.spawn_current_block(self.get_random_block())
		self.next_block = self.get_random_block()
		self.game_over = False
		self.game_won = False
		self.score = 0
		self.current_level_index = 0
		self.current_level = self.levels[0]
		self.level_start_score = 0
		self.time_left = self.current_level.time_limit_seconds
		self.drop_interval_ms = self.current_level.drop_interval_ms
		self.speed_changed = True
		self.pending_level_index = None
		self.level_transition_ms_left = 0
		self.invisible_until_ms = 0
		self.bomb_active = False
		self.has_bomb = False
		self.has_magic_wand = False
		self.last_block_position = None		
		self.hard_drop_lines.clear()
		self.lock_flash_effect.clear()
		self.row_clear_flash_effect.clear()
		self.magic_wand_effect.clear()
		self.bomb_explosion_effect.clear()

	def trigger_invisibility(self, duration_ms=1000):
		self.invisible_until_ms = pygame.time.get_ticks() + max(0, duration_ms)

	def is_invisible_active(self):
		return pygame.time.get_ticks() < self.invisible_until_ms


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
		"""Check if block is within grid bounds. In inverted mode, top boundary becomes bottom."""
		tiles = self.current_block.get_cell_positions()
		for tile in tiles:
			if tile.column < 0 or tile.column >= self.grid.num_cols:
				return False
			# Inverted: blocks can't go above row 0 (spawn area flipped)
			if self.inversion.inverted_gravity and tile.row < 0:
				return False
			if tile.row >= self.grid.num_rows:
				return False
		return True
	
	def draw(self, screen, hide_blocks=False):
		invisible = self.is_invisible_active()
		self.grid.draw(screen, self.grid_offset_x, self.grid_offset_y, hide_filled_blocks=hide_blocks)

		if not hide_blocks:
			self.bomb_explosion_effect.draw(screen, self.grid.cell_size, self.grid_offset_x, self.grid_offset_y, hide_blocks=invisible)
			self.lock_flash_effect.draw(screen, self.grid.cell_size, self.grid_offset_x, self.grid_offset_y)
		self.row_clear_flash_effect.draw(screen, self.grid.cell_size, self.grid_offset_x, self.grid_offset_y)
		self.magic_wand_effect.draw(screen, self.grid.cell_size, self.grid_offset_x, self.grid_offset_y)
		self.mole_pop_effect.draw(screen, self.grid.cell_size, self.grid_offset_x, self.grid_offset_y)
		if not invisible:
			self.hard_drop_lines.draw(screen, self.grid.cell_size, self.grid_offset_x, self.grid_offset_y)
			self.inversion_flash_effect.draw(screen, screen.get_width(), screen.get_height())
		if self.game_over == False and not invisible:
			self.draw_current_block_clipped(screen, self.grid_offset_x, self.grid_offset_y)

			self.draw_next_block_preview(screen)

			if self.is_invisible_active():
				self.draw_invisibility_overlay(screen)

	def draw_next_block_preview(self, screen):
		tiles = self.next_block.get_cell_positions()
		if not tiles:
			return

		min_col = min(tile.column for tile in tiles)
		max_col = max(tile.column for tile in tiles)
		min_row = min(tile.row for tile in tiles)
		max_row = max(tile.row for tile in tiles)

		tile_size = self.next_block.cell_size
		shape_width = (max_col - min_col + 1) * tile_size
		shape_height = (max_row - min_row + 1) * tile_size

		offset_x = self.next_preview_rect.x + (self.next_preview_rect.width - shape_width) // 2 - (min_col * tile_size)
		offset_y = self.next_preview_rect.y + (self.next_preview_rect.height - shape_height) // 2 - (min_row * tile_size)
		self.next_block.draw(screen, offset_x, offset_y)

	def set_layout(self, grid_x, grid_y, next_preview_rect):
		self.grid_offset_x = grid_x
		self.grid_offset_y = grid_y
		self.next_preview_rect = next_preview_rect

	def set_cell_size(self, cell_size):
		self.grid.cell_size = cell_size
		self.current_block.cell_size = cell_size
		self.next_block.cell_size = cell_size

	def draw_current_block_clipped(self, screen, offset_x, offset_y):
		for tile in self.current_block.get_cell_positions():
			if self.grid.is_inside(tile.row, tile.column):
				tile_rect = pygame.Rect(
					offset_x + tile.column * self.current_block.cell_size,
					offset_y + tile.row * self.current_block.cell_size,
					self.current_block.cell_size - 1,
					self.current_block.cell_size - 1,
				)
				if self.current_block.id == 8:
					draw_bomb_cell(screen, tile_rect)
				else:
					pygame.draw.rect(screen, self.current_block.colors[self.current_block.id], tile_rect)

	def countdown(self):
		"""Update game timer and check for random inverted gravity event"""
		if self.game_over or self.is_level_transitioning():
			return
		if self.time_left > 0:
			self.time_left -= 1
		# Check 40-second inverted gravity event timer
		self.update_inversion_event_timer()
		if self.time_left <= 0:
			self.time_left = 0
			if self.try_advance_level() == False:
				self.game_over = True

	def get_time_text(self):
		mins, secs = divmod(self.time_left, 60)
		return f"{mins:02d}:{secs:02d}"
	
	def get_drop_interval(self):
		return self.drop_interval_ms

	def consume_speed_change_flag(self):
		changed = self.speed_changed
		self.speed_changed = False
		return changed

	def get_level_text(self):
		#return f"Level {self.current_level.number}"
		return str(self.current_level.number)

	def get_level_goal_text(self):
		return f"{self.get_level_score()}/{self.current_level.target_score}"

	def get_transition_text(self):
		if self.is_level_transitioning() == False:
			return ""
		next_level_number = self.levels[self.pending_level_index].number
		return f"Level {next_level_number}"


