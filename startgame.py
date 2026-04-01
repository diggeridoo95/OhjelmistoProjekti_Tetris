import pygame
import sys
from colors import Colors

class StartScreen:
	def __init__(self, screen_width, screen_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.title_font = pygame.font.Font(None, 50)
		self.button_font = pygame.font.Font(None, 40)
		self.game_started = False
		self.background_image = None
		
		# Menu selection system
		self.menu_options = ["Play", "Options", "Controls", "Quit"]
		self.selected_index = 0  # Currently selected menu option

		# Options menu state
		self.options_open = False
		self.options_items = ["Display", "Music", "SFX", "Back"]
		self.options_selected_index = 0
		self.controls_open = False
		self.is_fullscreen = False
		self.music_volume = 0.10
		self.sfx_volume = 0.10
		self.volume_step = 0.10

	def set_background_image(self, image):
		self.background_image = image

	def _adjust_volume(self, current_value, direction):
		new_value = max(0.0, min(1.0, current_value + (direction * self.volume_step)))
		if abs(new_value - current_value) > 0.0001:
			return round(new_value, 2), True
		return current_value, False

	def _update_selected_option(self, direction):
		self.options_selected_index = (self.options_selected_index + direction) % len(self.options_items)

	def _apply_option_value_change(self, direction, action):
		if self.options_selected_index == 0:
			self.is_fullscreen = not self.is_fullscreen
			action["fullscreen"] = self.is_fullscreen
		elif self.options_selected_index == 1:
			self.music_volume, changed = self._adjust_volume(self.music_volume, direction)
			if changed:
				action["music_volume"] = self.music_volume
		elif self.options_selected_index == 2:
			self.sfx_volume, changed = self._adjust_volume(self.sfx_volume, direction)
			if changed:
				action["sfx_volume"] = self.sfx_volume

	def _activate_current_option(self, action):
		if self.options_selected_index == 0:
			self.is_fullscreen = not self.is_fullscreen
			action["fullscreen"] = self.is_fullscreen
		elif self.options_selected_index == 3:
			self.options_open = False

	def _draw_overlay_base(self, screen, panel_width, panel_height):
		panel_rect = pygame.Rect(
			(self.screen_width - panel_width) // 2,
			(self.screen_height - panel_height) // 2,
			panel_width,
			panel_height,
		)

		dim_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
		dim_surface.fill((0, 0, 0, 190))
		screen.blit(dim_surface, (0, 0))

		pygame.draw.rect(screen, (246, 249, 255), panel_rect, 0, 12)
		pygame.draw.rect(screen, Colors.light_blue, panel_rect, max(2, self.screen_width // 500), 12)
		return panel_rect

	def _draw_options_overlay(self, screen, option_font):
		panel_width = max(340, self.screen_width // 2)
		panel_height = max(340, self.screen_height // 2)
		panel_rect = self._draw_overlay_base(screen, panel_width, panel_height)

		header_surface = option_font.render("Options", True, Colors.dark_blue)
		header_rect = header_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + max(30, panel_height // 10)))
		screen.blit(header_surface, header_rect)

		option_spacing = max(44, panel_height // 6)
		start_y = header_rect.bottom + max(22, panel_height // 14)

		for i, item in enumerate(self.options_items):
			if item == "Display":
				value_text = "Fullscreen" if self.is_fullscreen else "Windowed"
			elif item == "Music":
				value_text = f"{int(self.music_volume * 100)}%"
			elif item == "SFX":
				value_text = f"{int(self.sfx_volume * 100)}%"
			else:
				value_text = ""

			text = f"{item}: {value_text}" if value_text else item
			y_pos = start_y + (i * option_spacing)

			text_color = Colors.white if i == self.options_selected_index else Colors.light_blue2
			if i == self.options_selected_index:
				highlight_rect = pygame.Rect(panel_rect.x + 18, y_pos - 20, panel_rect.width - 36, 40)
				highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
				pygame.draw.rect(highlight_surface, (44, 44, 127, 120), highlight_surface.get_rect(), border_radius=10)
				screen.blit(highlight_surface, (highlight_rect.x, highlight_rect.y))

			shadow_surface = option_font.render(text, True, Colors.dark_grey)
			shadow_rect = shadow_surface.get_rect(center=(panel_rect.centerx + 2, y_pos + 2))
			screen.blit(shadow_surface, shadow_rect)

			option_surface = option_font.render(text, True, text_color)
			option_rect = option_surface.get_rect(center=(panel_rect.centerx, y_pos))
			screen.blit(option_surface, option_rect)

		help_font = pygame.font.Font(None, max(20, self.screen_width // 45))
		help_surface = help_font.render("Left/Right: Change   Enter: Select   Esc: Back", True, Colors.dark_blue)
		help_rect = help_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom - max(28, panel_height // 12)))
		screen.blit(help_surface, help_rect)

	def _draw_controls_overlay(self, screen, option_font):
		panel_width = max(420, self.screen_width // 2)
		panel_height = max(420, int(self.screen_height * 0.65))
		panel_rect = self._draw_overlay_base(screen, panel_width, panel_height)

		header_surface = option_font.render("Controls", True, Colors.dark_blue)
		header_rect = header_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + max(32, panel_height // 12)))
		screen.blit(header_surface, header_rect)

		line_font = pygame.font.Font(None, max(24, self.screen_width // 40))
		controls_rows = [
			("Left / Right", "Move"),
			("Up", "Rotate"),
			("Down", "Soft Drop"),
			("Space", "Hard Drop"),
			("A", "Bomb Ability"),
			("S", "Magic Wand"),
			("P", "Pause"),
		]

		line_start_y = header_rect.bottom + max(24, panel_height // 14)
		line_spacing = max(36, panel_height // 11)
		left_x = panel_rect.x + 40
		right_x = panel_rect.right - 40

		for index, (control_text, action_text) in enumerate(controls_rows):
			y_pos = line_start_y + (index * line_spacing)

			control_surface = line_font.render(control_text, True, (18, 28, 78))
			control_rect = control_surface.get_rect(midleft=(left_x, y_pos))
			screen.blit(control_surface, control_rect)

			action_surface = line_font.render(action_text, True, (18, 28, 78))
			action_rect = action_surface.get_rect(midright=(right_x, y_pos))
			screen.blit(action_surface, action_rect)

		help_font = pygame.font.Font(None, max(22, self.screen_width // 45))
		help_surface = help_font.render("Enter / Esc: Back", True, Colors.dark_blue)
		help_rect = help_surface.get_rect(center=(panel_rect.centerx, panel_rect.bottom - max(30, panel_height // 12)))
		screen.blit(help_surface, help_rect)
	
	def handle_event(self, event):
		action = {}
		if event.type == pygame.KEYDOWN:
			if self.controls_open:
				if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
					self.controls_open = False
			elif self.options_open:
				if event.key == pygame.K_UP:
					self._update_selected_option(-1)
				elif event.key == pygame.K_DOWN:
					self._update_selected_option(1)
				elif event.key == pygame.K_LEFT:
					self._apply_option_value_change(-1, action)
				elif event.key == pygame.K_RIGHT:
					self._apply_option_value_change(1, action)
				elif event.key == pygame.K_RETURN:
					self._activate_current_option(action)
				elif event.key == pygame.K_ESCAPE:
					self.options_open = False
			else:
				# Navigate main menu with arrow keys
				if event.key == pygame.K_UP:
					self.selected_index = (self.selected_index - 1) % len(self.menu_options)
				elif event.key == pygame.K_DOWN:
					self.selected_index = (self.selected_index + 1) % len(self.menu_options)
				# Press Enter to select option
				elif event.key == pygame.K_RETURN:
					if self.selected_index == 0:  # Play selected
						self.game_started = True
					elif self.selected_index == 1:  # Options selected
						self.options_open = True
						self.controls_open = False
						self.options_selected_index = 0
					elif self.selected_index == 2:  # Controls selected
						self.controls_open = True
						self.options_open = False
					elif self.selected_index == 3:  # Quit selected
						pygame.quit()
						sys.exit()
		return action
	
	def draw(self, screen):
		self.screen_width, self.screen_height = screen.get_size()
		title_font = pygame.font.Font(None, max(50, self.screen_width // 14))
		button_font = pygame.font.Font(None, max(34, self.screen_width // 22))
		option_font = pygame.font.Font(None, max(28, self.screen_width // 25))
		menu_option_font = pygame.font.Font(None, max(32, self.screen_width // 28))

		if self.background_image is not None:
			scaled_background = pygame.transform.smoothscale(self.background_image, (self.screen_width, self.screen_height))
			screen.blit(scaled_background, (0, 0))
		else:
			screen.fill(Colors.dark_blue)
		
		# Title
		title_shadow_surface = title_font.render("TETRIS OVERWHELMED", True, Colors.dark_grey)
		title_shadow_rect = title_shadow_surface.get_rect(center=(self.screen_width // 2 + 2, self.screen_height // 4 + 2))
		screen.blit(title_shadow_surface, title_shadow_rect)
		title_surface = title_font.render("TETRIS OVERWHELMED", True, Colors.white)
		title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 4))
		screen.blit(title_surface, title_rect)
		
		# Draw menu options
		title_y = self.screen_height // 4
		menu_start_y = title_y + max(96, self.screen_height // 8)
		menu_bottom_margin = max(56, self.screen_height // 12)
		available_height = max(120, self.screen_height - menu_start_y - menu_bottom_margin)
		if len(self.menu_options) > 1:
			option_count = len(self.menu_options)
			min_spacing = menu_option_font.get_height() + max(8, self.screen_height // 80)
			target_spacing = max(min_spacing, int(self.screen_height * 0.09))
			max_spacing_to_fit = available_height // (option_count - 1)
			option_spacing = max(min_spacing, min(target_spacing, max_spacing_to_fit))

			last_item_y = menu_start_y + ((option_count - 1) * option_spacing)
			max_last_item_y = self.screen_height - menu_bottom_margin
			if last_item_y > max_last_item_y:
				menu_start_y -= (last_item_y - max_last_item_y)
		else:
			option_spacing = 0
		pad = max(20, self.screen_width // 40)
		overlay_active = self.options_open or self.controls_open
		
		# First pass: calculate menu bounds
		menu_rects = []
		for i, option in enumerate(self.menu_options):
			y_pos = menu_start_y + (i * option_spacing)
			option_surface = menu_option_font.render(option, True, Colors.white)
			option_rect = option_surface.get_rect(center=(self.screen_width // 2, y_pos))
			menu_rects.append(option_rect)
		
		# Calculate the bounding box for all menu items and draw semi-transparent background
		menu_box = None
		if menu_rects and not overlay_active:
			min_left = min(rect.left for rect in menu_rects) - pad
			max_right = max(rect.right for rect in menu_rects) + pad
			min_top = menu_rects[0].top - pad
			max_bottom = menu_rects[-1].bottom + pad
			
			menu_box = pygame.Rect(min_left, min_top, max_right - min_left, max_bottom - min_top)
			
			# Draw semi-transparent white background box
			menu_box_surface = pygame.Surface((menu_box.width, menu_box.height), pygame.SRCALPHA)
			pygame.draw.rect(menu_box_surface, (255, 255, 255, 100), menu_box_surface.get_rect(), border_radius=10)
			screen.blit(menu_box_surface, (menu_box.x, menu_box.y))
			
			# Draw border
			pygame.draw.rect(screen, Colors.light_blue, menu_box, max(2, self.screen_width // 500), 10)
		
		# Second pass: draw options with glow on selected
		if not overlay_active:
			for i, option in enumerate(self.menu_options):
				y_pos = menu_start_y + (i * option_spacing)
				
				# Highlight selected option with glow
				if i == self.selected_index:
					# Draw shadow effect (like title)
					option_shadow_surface = menu_option_font.render(option, True, Colors.dark_grey)
					option_shadow_rect = option_shadow_surface.get_rect(center=(self.screen_width // 2 + 2, y_pos + 2))
					screen.blit(option_shadow_surface, option_shadow_rect)
					
					# Draw main text (like title)
					option_surface = menu_option_font.render(option, True, Colors.white)
					option_rect = option_surface.get_rect(center=(self.screen_width // 2, y_pos))
					
					# Draw glow effect behind the selected item
					glow_radius = max(15, int(pad * 1.5))
					glow_surface = pygame.Surface((option_rect.width + glow_radius * 2, option_rect.height + glow_radius * 2), pygame.SRCALPHA)
					pygame.draw.circle(glow_surface, (100, 200, 255, 80), (glow_surface.get_width() // 2, glow_surface.get_height() // 2), glow_radius)
					screen.blit(glow_surface, (option_rect.x - glow_radius, option_rect.y - glow_radius))
					
					# Draw highlight box that fills the full width of the menu box
					if menu_box:
						highlight_box = pygame.Rect(menu_box.x + 4, option_rect.y - pad // 2, menu_box.width - 8, option_rect.height + pad)
						highlight_surface = pygame.Surface((highlight_box.width, highlight_box.height), pygame.SRCALPHA)
						pygame.draw.rect(highlight_surface, (255, 255, 255, 150), highlight_surface.get_rect(), border_radius=10)
						screen.blit(highlight_surface, (highlight_box.x, highlight_box.y))
					
					screen.blit(option_surface, option_rect)
				else:
					# Non-selected option with shadow effect (like title)
					option_shadow_surface = menu_option_font.render(option, True, Colors.dark_grey)
					option_shadow_rect = option_shadow_surface.get_rect(center=(self.screen_width // 2 + 2, y_pos + 2))
					screen.blit(option_shadow_surface, option_shadow_rect)
					
					option_surface = menu_option_font.render(option, True, Colors.light_blue2)
					option_rect = option_surface.get_rect(center=(self.screen_width // 2, y_pos))
					screen.blit(option_surface, option_rect)

		if self.options_open:
			self._draw_options_overlay(screen, option_font)
		elif self.controls_open:
			self._draw_controls_overlay(screen, option_font)
