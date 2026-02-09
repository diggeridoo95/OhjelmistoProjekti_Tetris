import pygame, sys
from colors import Colors
from game import Game

screen = pygame.display.set_mode((500, 620))
pygame.display.set_caption("Tetris Overwhelmed")

clock = pygame.time.Clock()

game = Game()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	screen.fill(Colors.dark_blue)
	game.draw(screen)
	pygame.display.update()
	clock.tick(60)