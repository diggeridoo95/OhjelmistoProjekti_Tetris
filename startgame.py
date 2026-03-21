import pygame
from colors import Colors

class StartScreen:
	def __init__(self, screen_width, screen_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.title_font = pygame.font.Font(None, 50)
		self.button_font = pygame.font.Font(None, 40)
		self.game_started = False
		self.background_image = None

	def set_background_image(self, image):
		self.background_image = image
	
	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				self.game_started = True
	
	def draw(self, screen):
		self.screen_width, self.screen_height = screen.get_size()
		title_font = pygame.font.Font(None, max(50, self.screen_width // 14))
		button_font = pygame.font.Font(None, max(34, self.screen_width // 22))

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
		
		# Start button text
		start_surface = button_font.render("Press SPACE to Start", True, Colors.white)
		start_rect = start_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
		
		# Draw a contrast panel around the start prompt.
		pad = max(14, self.screen_width // 45)
		box_rect = pygame.Rect(start_rect.x - pad, start_rect.y - pad, start_rect.width + 2 * pad, start_rect.height + 2 * pad)
		pygame.draw.rect(screen, Colors.dark_blue, box_rect, 0, 10)
		pygame.draw.rect(screen, Colors.light_blue, box_rect, max(2, self.screen_width // 500), 10)
		screen.blit(start_surface, start_rect)
