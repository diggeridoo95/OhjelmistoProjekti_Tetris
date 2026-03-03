import pygame, sys
import time
from colors import Colors
from game import Game
from blocks import *
from startgame import StartScreen
pygame.init()


title_font = pygame.font.Font(None, 40)
score_surface = title_font.render("Score", True, Colors.white)
next_surface = title_font.render("Next", True, Colors.white)
ability_surface = title_font.render("Ability", True, Colors.white)
score_rect = pygame.Rect(320, 55, 170, 60)
next_rect = pygame.Rect(315, 185, 170, 180)
ability_rect = pygame.Rect(315, 405, 170, 180)
game_over_surface = title_font.render("Game Over!", True, Colors.white)

screen = pygame.display.set_mode((500, 640))
pygame.display.set_caption("Tetris Overwhelmed")

clock = pygame.time.Clock()

# Initialize start screen
start_screen = StartScreen(500, 640)
game = None
game_started = False

GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 200)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		
		if not game_started:
			# Handle start screen events
			start_screen.handle_event(event)
			if start_screen.game_started:
				game_started = True
				game = Game()
		else:
			# Handle game events
			if event.type == pygame.KEYDOWN:
				if game.game_over == True:
					game.game_over = False
					game.reset()
				if event.key == pygame.K_LEFT and game.game_over == False:
					game.move_left()
				if event.key == pygame.K_RIGHT and game.game_over == False:
					game.move_right()
				if event.key == pygame.K_DOWN and game.game_over == False:
					game.move_down()
				if event.key == pygame.K_UP and game.game_over == False:
					game.rotate()
				if event.key == pygame.K_SPACE and game.game_over == False:
					game.hard_drop()
			if event.type == GAME_UPDATE and game.game_over == False:
				game.move_down()
			

	if not game_started:
		# Draw start screen
		start_screen.draw(screen)
	else:
		# Draw game
		score_value_surface = title_font.render(str(game.score), True, Colors.white)

		screen.fill(Colors.dark_blue)
		screen.blit(score_surface, (365, 20, 50, 50))
		screen.blit(next_surface, (375, 150, 50, 50))
		screen.blit(ability_surface, (360, 375, 50, 50))
		if game.game_over == True:
			screen.blit(game_over_surface, (320, 600, 170, 60))
			
		pygame.draw.rect(screen, Colors.light_blue, score_rect, 0, 10)
		screen.blit(score_value_surface, score_value_surface.get_rect(centerx = score_rect.centerx, 
		                                                                  centery = score_rect.centery))
		pygame.draw.rect(screen, Colors.light_blue, next_rect, 0, 10)
		pygame.draw.rect(screen, Colors.light_blue, ability_rect, 0, 10)

		
		    


		game.draw(screen)
	pygame.display.update()
	clock.tick(60)