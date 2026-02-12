import pygame, sys
from colors import Colors
from game import Game
from blocks import *

screen = pygame.display.set_mode((500, 620))
pygame.display.set_caption("Tetris Overwhelmed")

clock = pygame.time.Clock()

game = Game()

GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 200)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				game.move_left()
			if event.key == pygame.K_RIGHT:
				game.move_right()
			if event.key == pygame.K_DOWN:
				game.move_down()
			if event.key == pygame.K_UP:
				game.rotate()
		if event.type == GAME_UPDATE:
			game.move_down()

	screen.fill(Colors.dark_blue)
	game.draw(screen)
	pygame.display.update()
	clock.tick(60)