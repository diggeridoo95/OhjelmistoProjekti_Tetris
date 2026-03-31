import pygame, sys, os
from colors import Colors
from game import Game
from blocks import *
from bomb_icon import draw_bomb_cell
from magic_wand_icon import draw_magic_wand_cell
from startgame import StartScreen
from pausemenu import PauseMenu
pygame.init()

INITIAL_WIDTH = 1000
INITIAL_HEIGHT = 720
GRID_COLS = 10
GRID_ROWS = 20
BASE_CELL = 30
MIN_CELL = 14
BASE_SIDE_MIN = 170

screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Tetris Overwhelmed")

clock = pygame.time.Clock()

# Initialize start screen
start_screen = StartScreen(INITIAL_WIDTH, INITIAL_HEIGHT)
game = None
game_started = False
game_paused = False
pause_menu = None
background_image = None

background_path = os.path.join(os.path.dirname(__file__), "pictures", "background.png")
if os.path.exists(background_path):
	try:
		background_image = pygame.image.load(background_path).convert()
		start_screen.set_background_image(background_image)
	except pygame.error:
		background_image = None


def make_font(base_size, ui_scale, min_size=16):
	return pygame.font.Font(None, max(min_size, int(base_size * ui_scale)))


def clamp(value, low, high):
	return max(low, min(high, value))


def get_layout(width, height):
	margin = max(8, int(min(width, height) * 0.012))
	side_min = max(BASE_SIDE_MIN, int(width * 0.15))

	max_cell_w = (width - (2 * side_min) - (4 * margin)) // GRID_COLS
	max_cell_h = (height - (2 * margin)) // GRID_ROWS
	cell_size = max(MIN_CELL, min(max_cell_w, max_cell_h))

	grid_w = GRID_COLS * cell_size
	grid_h = GRID_ROWS * cell_size
	grid_x = (width - grid_w) // 2
	grid_y = height - grid_h - margin

	left_space = grid_x
	right_space = width - (grid_x + grid_w)
	left_panel_w = max(120, left_space - (2 * margin))
	right_panel_w = max(120, right_space - (2 * margin))
	left_panel_x = margin
	right_panel_x = width - right_panel_w - margin

	ui_scale = max(0.65, cell_size / BASE_CELL)

	return {
		"margin": margin,
		"ui_scale": ui_scale,
		"cell_size": cell_size,
		"grid_x": grid_x,
		"grid_y": grid_y,
		"grid_w": grid_w,
		"grid_h": grid_h,
		"left_panel_x": left_panel_x,
		"left_panel_w": left_panel_w,
		"right_panel_x": right_panel_x,
		"right_panel_w": right_panel_w,
	}

GAME_UPDATE = pygame.USEREVENT
TIMER_UPDATE = pygame.USEREVENT + 1
LEVEL_TRANSITION_UPDATE = pygame.USEREVENT + 2
pygame.time.set_timer(GAME_UPDATE, 200)
pygame.time.set_timer(TIMER_UPDATE, 1000)
pygame.time.set_timer(LEVEL_TRANSITION_UPDATE, 100)

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
				game_paused = False
				pause_menu = PauseMenu()
				pygame.time.set_timer(GAME_UPDATE, game.get_drop_interval())

		else:
			# Handle game events
			if game_paused:
				action = pause_menu.handle_event(event)
				if action == "continue":
					game_paused = False
				elif action == "main_menu":
					game_started = False
					start_screen.game_started = False
					game = None
					pause_menu = None
					game_paused = False
				continue

			if event.type == pygame.KEYDOWN:
				if game.game_over == True:
					# Return to main menu only when Enter is pressed.
					if event.key == pygame.K_RETURN:
						game_started = False
						start_screen.game_started = False
						game = None
						pause_menu = None
						game_paused = False
					continue
				if event.key == pygame.K_p and game.game_over == False:
					game_paused = True
					if pause_menu is None:
						pause_menu = PauseMenu()
					continue
				if event.key == pygame.K_LEFT and game.game_over == False and game.is_level_transitioning() == False:
					game.move_left()
				if event.key == pygame.K_RIGHT and game.game_over == False and game.is_level_transitioning() == False:
					game.move_right()
				if event.key == pygame.K_DOWN and game.game_over == False and game.is_level_transitioning() == False:
					game.move_down()
				if event.key == pygame.K_UP and game.game_over == False and game.is_level_transitioning() == False:
					game.rotate()
				if event.key == pygame.K_SPACE and game.game_over == False and game.is_level_transitioning() == False:
					game.hard_drop()
				if event.key == pygame.K_a and game.game_over == False and game.is_level_transitioning() == False:
					game.use_bomb_ability()
				if event.key == pygame.K_s and game.game_over == False and game.is_level_transitioning() == False:
					game.use_magic_wand_ability()

				
				if event.key == pygame.K_q:		#debug key to give player all abilities for testing
					game.has_bomb = True
					game.has_magic_wand = True


			if event.type == GAME_UPDATE and game.game_over == False and game.is_level_transitioning() == False and game_paused == False:
				game.move_down()
				game.update_level_events() 	#Update events on each game tick
			if event.type == TIMER_UPDATE and game.game_over == False and game.is_level_transitioning() == False and game_paused == False:
				game.countdown()
			if event.type == LEVEL_TRANSITION_UPDATE and game.game_over == False and game_paused == False:
				game.update_level_transition(100)
			
			if game.consume_speed_change_flag():
				pygame.time.set_timer(GAME_UPDATE, game.get_drop_interval())
			

	if not game_started:
		# Draw start screen
		start_screen.draw(screen)
	else:
		# Draw game
		window_w, window_h = screen.get_size()
		layout = get_layout(window_w, window_h)
		ui_scale = layout["ui_scale"]

		title_font = make_font(40, ui_scale, 20)
		small_font = make_font(24, ui_scale, 14)
		event_font = make_font(32, ui_scale, 18)
		transition_font = make_font(72, ui_scale, 24)

		score_surface = title_font.render("Score", True, Colors.white)
		next_surface = title_font.render("Next", True, Colors.white)
		ability_surface = title_font.render("Ability", True, Colors.white)
		level_surface = title_font.render("Level", True, Colors.white)
		goal_surface = title_font.render("Goal", True, Colors.white)
		time_text_surface = title_font.render("Time", True, Colors.white)
		game_over_surface = title_font.render("Game Over!", True, Colors.white)
		you_won_surface = title_font.render("You Won!", True, Colors.white)

		score_value_surface = title_font.render(str(game.score), True, Colors.white)
		level_value_surface = title_font.render(game.get_level_text(), True, Colors.white)
		goal_value_surface = title_font.render(game.get_level_goal_text(), True, Colors.white)
		time_surface = title_font.render(game.get_time_text(), True, Colors.white)

		panel_box_size = min(layout["right_panel_w"], max(120, int(180 * ui_scale)))
		panel_box_x = layout["right_panel_x"] + (layout["right_panel_w"] - panel_box_size) // 2
		left_value_box_w = min(layout["left_panel_w"], max(120, int(180 * ui_scale)))
		left_value_box_h = max(40, int(56 * ui_scale))
		left_value_box_x = layout["left_panel_x"] + (layout["left_panel_w"] - left_value_box_w) // 2
		left_label_gap = max(16, int(24 * ui_scale))
		left_section_gap = max(26, int(34 * ui_scale))
		left_first_box_y = int(175 * ui_scale)
		goal_box_y = left_first_box_y + left_value_box_h + left_section_gap + left_label_gap
		time_box_y = goal_box_y + left_value_box_h + left_section_gap + left_label_gap

		score_rect = pygame.Rect(
			panel_box_x,
			int(55 * ui_scale),
			panel_box_size,
			max(40, int(60 * ui_scale)),
		)
		next_rect = pygame.Rect(
			panel_box_x,
			int(185 * ui_scale),
			panel_box_size,
			panel_box_size,
		)
		ability_rect = pygame.Rect(
			panel_box_x,
			int(405 * ui_scale),
			panel_box_size,
			panel_box_size,
		)
		level_value_rect = pygame.Rect(
			left_value_box_x,
			left_first_box_y,
			left_value_box_w,
			left_value_box_h,
		)
		goal_value_rect = pygame.Rect(
			left_value_box_x,
			goal_box_y,
			left_value_box_w,
			left_value_box_h,
		)
		time_value_rect = pygame.Rect(
			left_value_box_x,
			time_box_y,
			left_value_box_w,
			left_value_box_h,
		)

		game.set_cell_size(layout["cell_size"])
		game.set_layout(layout["grid_x"], layout["grid_y"], next_rect)

		if background_image is not None:
			scaled_background = pygame.transform.smoothscale(background_image, (window_w, window_h))
			screen.blit(scaled_background, (0, 0))
		else:
			screen.fill(Colors.dark_blue)

		# Solid base under the playfield keeps grid gaps from showing the wallpaper.
		playfield_padding = max(3, int(5 * ui_scale))
		playfield_bg_rect = pygame.Rect(
			layout["grid_x"] - playfield_padding,
			layout["grid_y"] - playfield_padding,
			layout["grid_w"] + (2 * playfield_padding),
			layout["grid_h"] + (2 * playfield_padding),
		)
		pygame.draw.rect(screen, Colors.dark_grey, playfield_bg_rect, 0, max(6, int(10 * ui_scale)))
		pygame.draw.rect(screen, Colors.light_blue, playfield_bg_rect, max(1, int(2 * ui_scale)), max(6, int(10 * ui_scale)))

		score_shadow = title_font.render("Score", True, Colors.dark_grey)
		screen.blit(score_shadow, score_shadow.get_rect(center=(score_rect.centerx + 2, int(30 * ui_scale) + 2)))
		screen.blit(score_surface, score_surface.get_rect(center=(score_rect.centerx, int(30 * ui_scale))))

		next_shadow = title_font.render("Next", True, Colors.dark_grey)
		screen.blit(next_shadow, next_shadow.get_rect(center=(next_rect.centerx + 2, int(160 * ui_scale) + 2)))
		screen.blit(next_surface, next_surface.get_rect(center=(next_rect.centerx, int(160 * ui_scale))))

		ability_shadow = title_font.render("Ability", True, Colors.dark_grey)
		screen.blit(ability_shadow, ability_shadow.get_rect(center=(ability_rect.centerx + 2, int(385 * ui_scale) + 2)))
		screen.blit(ability_surface, ability_surface.get_rect(center=(ability_rect.centerx, int(385 * ui_scale))))

		level_shadow = title_font.render("Level", True, Colors.dark_grey)
		screen.blit(level_shadow, level_shadow.get_rect(center=(level_value_rect.centerx + 2, level_value_rect.top - left_label_gap + 2)))
		screen.blit(level_surface, level_surface.get_rect(center=(level_value_rect.centerx, level_value_rect.top - left_label_gap)))

		goal_shadow = title_font.render("Goal", True, Colors.dark_grey)
		screen.blit(goal_shadow, goal_shadow.get_rect(center=(goal_value_rect.centerx + 2, goal_value_rect.top - left_label_gap + 2)))
		screen.blit(goal_surface, goal_surface.get_rect(center=(goal_value_rect.centerx, goal_value_rect.top - left_label_gap)))

		time_shadow = title_font.render("Time", True, Colors.dark_grey)
		screen.blit(time_shadow, time_shadow.get_rect(center=(time_value_rect.centerx + 2, time_value_rect.top - left_label_gap + 2)))
		screen.blit(time_text_surface, time_text_surface.get_rect(center=(time_value_rect.centerx, time_value_rect.top - left_label_gap)))

		pygame.draw.rect(screen, Colors.dark_grey, score_rect, 0, max(6, int(10 * ui_scale)))
		screen.blit(score_value_surface, score_value_surface.get_rect(centerx = score_rect.centerx, 
		                                                                  centery = score_rect.centery))
		pygame.draw.rect(screen, Colors.dark_grey, next_rect, 0, max(6, int(10 * ui_scale)))
		pygame.draw.rect(screen, Colors.dark_grey, ability_rect, 0, max(6, int(10 * ui_scale)))
		pygame.draw.rect(screen, Colors.dark_grey, level_value_rect, 0, max(6, int(10 * ui_scale)))
		screen.blit(level_value_surface, level_value_surface.get_rect(center=level_value_rect.center))
		pygame.draw.rect(screen, Colors.dark_grey, goal_value_rect, 0, max(6, int(10 * ui_scale)))
		screen.blit(goal_value_surface, goal_value_surface.get_rect(center=goal_value_rect.center))
		pygame.draw.rect(screen, Colors.dark_grey, time_value_rect, 0, max(6, int(10 * ui_scale)))
		screen.blit(time_surface, time_surface.get_rect(center=time_value_rect.center))
		
		# Display ability status
		icon_drawers = []
		if game.has_bomb:
			icon_drawers.append(draw_bomb_cell)
		if game.has_magic_wand:
			icon_drawers.append(draw_magic_wand_cell)

		if icon_drawers:
			icon_count = len(icon_drawers)
			gap = max(8, int(ability_rect.width * 0.08))
			icon_size = min(
				ability_rect.height - max(10, int(ability_rect.height * 0.18)),
				(ability_rect.width - (icon_count - 1) * gap - max(10, int(ability_rect.width * 0.12))) // icon_count,
			)
			icon_size = max(16, icon_size)

			total_width = icon_count * icon_size + (icon_count - 1) * gap
			start_x = ability_rect.x + (ability_rect.width - total_width) // 2
			icon_y = ability_rect.y + (ability_rect.height - icon_size) // 2

			for i, draw_icon in enumerate(icon_drawers):
				icon_x = start_x + i * (icon_size + gap)
				icon_rect = pygame.Rect(icon_x, icon_y, icon_size, icon_size)
				draw_icon(screen, icon_rect)
		else:
			ability_value_surface = small_font.render("No Ability", True, Colors.white)
			screen.blit(
				ability_value_surface,
				ability_value_surface.get_rect(centerx=ability_rect.centerx, centery=ability_rect.centery),
			)

		game.draw(screen, hide_blocks=game_paused)

		#Display Event text if activated
		if game.last_event_timer > 0 and game.last_event_text:
			event_surface = event_font.render(game.last_event_text, True, Colors.white)

			event_bg = pygame.Rect(0, int(680 * ui_scale), max(220, int(320 * ui_scale)), max(28, int(45 * ui_scale)))
			event_bg.centerx = layout["left_panel_x"] + (layout["left_panel_w"] // 2)

			pygame.draw.rect(screen, Colors.light_blue, event_bg, 0, max(8, int(12 * ui_scale)))
			screen.blit(event_surface, event_surface.get_rect(center=event_bg.center))

		overlay_bg = pygame.Rect(
			int(70 * ui_scale),
			int(265 * ui_scale),
			max(220, int(360 * ui_scale)),
			max(60, int(100 * ui_scale)),
		)
		overlay_bg.centerx = layout["grid_x"] + (layout["grid_w"] // 2)

		# TASONVAIHTO JA GAME OVER/YOU WIN RUUTU ULKONÄKÖ
		if game.game_over == True or game.is_level_transitioning():
			dim_surface = pygame.Surface((window_w, window_h), pygame.SRCALPHA)
			dim_surface.fill((0, 0, 0, 120))
			screen.blit(dim_surface, (0,0))

			overlay_surface = pygame.Surface((overlay_bg.width, overlay_bg.height), pygame.SRCALPHA)
			pygame.draw.rect(overlay_surface, (255, 255, 255,100), overlay_surface.get_rect(), border_radius=14)
			screen.blit(overlay_surface, (overlay_bg.x, overlay_bg.y))
			pygame.draw.rect(screen, Colors.light_blue, overlay_bg, max (2, int(3 * ui_scale)),14)

			if game.game_over == True:
				if game.game_won:
					overlay_text_surface = you_won_surface
					shadow_text = "You Won!"
				else:
					overlay_text_surface = game_over_surface
					shadow_text = "Game Over!"
				shadow_surface = title_font.render(shadow_text, True, Colors.dark_grey)
				screen.blit(shadow_surface, shadow_surface.get_rect(center=(overlay_bg.centerx + 2, overlay_bg.centery +2)))
				screen.blit(overlay_text_surface, overlay_text_surface.get_rect(center=overlay_bg.center))
			elif game.is_level_transitioning():
				transition_text = game.get_transition_text()
				overlay_text_surface = transition_font.render(game.get_transition_text(), True, Colors.white)
				shadow_surface = transition_font.render(game.get_transition_text(), True, Colors.dark_grey)
				screen.blit(shadow_surface, shadow_surface.get_rect(center=(overlay_bg.centerx + 2, overlay_bg.centery +2)))
				screen.blit(overlay_text_surface, overlay_text_surface.get_rect(center=overlay_bg.center))

		if game_paused and pause_menu is not None:
			pause_menu.draw(screen)

	pygame.display.update()
	clock.tick(60)