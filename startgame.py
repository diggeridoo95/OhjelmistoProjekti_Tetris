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
		self.menu_options = ["Play", "Controls", "Quit"]
		self.selected_index = 0  # Currently selected menu option

	def set_background_image(self, image):
		self.background_image = image
	
	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			# Navigate menu with arrow keys
			if event.key == pygame.K_UP:
				self.selected_index = (self.selected_index - 1) % len(self.menu_options)
			elif event.key == pygame.K_DOWN:
				self.selected_index = (self.selected_index + 1) % len(self.menu_options)
			# Press Enter to select option
			elif event.key == pygame.K_RETURN:
				if self.selected_index == 0:  # Play selected
					self.game_started = True
				elif self.selected_index == 1:  # Controls selected
					# TODO: Open controls screen (not implemented yet)
					pass
				elif self.selected_index == 2:  # Quit selected
					pygame.quit()
					sys.exit()
	
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
		menu_start_y = self.screen_height // 2
		option_spacing = max(60, self.screen_width // 12)
		pad = max(20, self.screen_width // 40)
		
		# First pass: calculate menu bounds
		menu_rects = []
		for i, option in enumerate(self.menu_options):
			y_pos = menu_start_y + (i * option_spacing)
			option_surface = menu_option_font.render(option, True, Colors.white)
			option_rect = option_surface.get_rect(center=(self.screen_width // 2, y_pos))
			menu_rects.append(option_rect)
		
		# Calculate the bounding box for all menu items and draw semi-transparent background
		menu_box = None
		if menu_rects:
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
