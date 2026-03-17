from grid import Grid
from blocks import *
from abilities import BombAbility
from levels import get_levels
import random
import pygame


class Game:
	def __init__(self):
		self.grid = Grid()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
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
		self.last_event_text = ""
		self.last_event_timer = 0
		
		
		# Ability system
		self.bomb_ability = BombAbility()
		self.bomb_active = False  # Flag indicating bomb is active for next block
		self.has_bomb = False  # Flag indicating player owns bomb ability
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

		self.current_level_index = level_index
		self.current_level = self.levels[self.current_level_index]
		self.level_start_score = self.score
		self.time_left = self.current_level.time_limit_seconds
		self.drop_interval_ms = self.current_level.drop_interval_ms
		self.speed_changed = True

		self.grid.reset()
		self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
		self.current_block = self.spawn_current_block(self.get_random_block())
		self.next_block = self.get_next_block()

		self.has_bomb = preserved_has_bomb
		self.bomb_active = preserved_bomb_active

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

	def spawn_current_block(self, block):
		block.move(-1, 0)
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
				if self.grid.is_inside(bomb_pos.row, bomb_pos.column):
					self.grid.bomb_explosion(bomb_pos.row, bomb_pos.column)
			self.has_bomb = False
			self.bomb_active = False
		else:
			# Normal block locking
			for position in tiles:
				if self.grid.is_inside(position.row, position.column):
					self.grid.grid[position.row][position.column] = self.current_block.id
		
		# Set position for potential bomb explosion tracking
		if tiles:
			self.last_block_position = tiles[0]
		
		self.current_block = self.spawn_current_block(self.next_block)
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
			if tile.column < 0 or tile.column >= self.grid.num_cols:
				return False
			if tile.row >= self.grid.num_rows:
				return False
		return True
	
	def draw(self, screen):
		self.grid.draw(screen)
		if self.game_over == False:
			self.draw_current_block_clipped(screen, 11, 11)

		if self.next_block.id == 3:
			self.next_block.draw(screen, 250, 260)
		elif self.next_block.id == 4:
			self.next_block.draw(screen, 250, 245)
		elif self.next_block.id == 8:  # BombBlock
			self.next_block.draw(screen, 295, 290)
		else:
			self.next_block.draw(screen, 265, 240)

	def draw_current_block_clipped(self, screen, offset_x, offset_y):
		for tile in self.current_block.get_cell_positions():
			if self.grid.is_inside(tile.row, tile.column):
				tile_rect = pygame.Rect(
					offset_x + tile.column * self.current_block.cell_size,
					offset_y + tile.row * self.current_block.cell_size,
					self.current_block.cell_size - 1,
					self.current_block.cell_size - 1,
				)
				pygame.draw.rect(screen, self.current_block.colors[self.current_block.id], tile_rect)

	def countdown(self):
		if self.game_over or self.is_level_transitioning():
			return
		if self.time_left > 0:
			self.time_left -= 1
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
		return f"Level {self.current_level.number}"

	def get_level_goal_text(self):
		return f"{self.get_level_score()}/{self.current_level.target_score}"

	def get_transition_text(self):
		if self.is_level_transitioning() == False:
			return ""
		next_level_number = self.levels[self.pending_level_index].number
		return f"Level {next_level_number}"