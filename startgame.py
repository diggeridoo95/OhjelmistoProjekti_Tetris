import pygame
from colors import Colors

class StartScreen:
	def __init__(self, screen_width, screen_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.title_font = pygame.font.Font(None, 50)
		self.button_font = pygame.font.Font(None, 40)
		self.game_started = False
	
	def handle_event(self, event):
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				self.game_started = True
	
	def draw(self, screen):
		screen.fill(Colors.dark_blue)
		
		# Title
		title_surface = self.title_font.render("TETRIS OWERWHELMED", True, Colors.cyan)
		title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
		screen.blit(title_surface, title_rect)
		
		# Start button text
		start_surface = self.button_font.render("Press SPACE to Start", True, Colors.white)
		start_rect = start_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
		screen.blit(start_surface, start_rect)
		
		# Draw a box around it
		box_rect = pygame.Rect(start_rect.x - 20, start_rect.y - 20, start_rect.width + 40, start_rect.height + 40)
		pygame.draw.rect(screen, Colors.light_blue, box_rect, 3, 10)
