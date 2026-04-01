import pygame
import os

# Music volume control
current_volume = 0.10

# Path to music files
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "sounds", "music")


def initialize():
	"""Initialize the music system."""
	global current_volume
	pygame.mixer.music.set_volume(current_volume)


def set_volume(volume):
	"""
	Set the music volume (0.0 to 1.0).
	
	Args:
		volume (float): Volume level between 0.0 (silent) and 1.0 (max)
	"""
	global current_volume
	current_volume = max(0.0, min(1.0, volume))
	try:
		pygame.mixer.music.set_volume(current_volume)
	except pygame.error:
		pass


def get_volume():
	"""Get the current music volume."""
	return current_volume


def play(filename, loops=0):
	"""
	Play a music file.
	
	Args:
		filename (str): Name of the music file in the sounds/music directory
		loops (int): Number of times to loop (-1 for infinite loop, 0 for play once)
	"""
	try:
		music_path = os.path.join(MUSIC_DIR, filename)
		if os.path.exists(music_path):
			pygame.mixer.music.load(music_path)
			pygame.mixer.music.play(loops)
		else:
			print(f"Warning: Music file not found: {music_path}")
	except pygame.error as e:
		print(f"Error playing music {filename}: {e}")


def play_background(filename):
	"""
	Play background music on loop.
	
	Args:
		filename (str): Name of the music file in the sounds/music directory
	"""
	play(filename, loops=-1)


def stop():
	"""Stop the currently playing music."""
	try:
		pygame.mixer.music.stop()
	except pygame.error:
		pass


def pause():
	"""Pause the current music."""
	try:
		pygame.mixer.music.pause()
	except pygame.error:
		pass


def unpause():
	"""Resume paused music."""
	try:
		pygame.mixer.music.unpause()
	except pygame.error:
		pass


def is_playing():
	"""Check if music is currently playing."""
	try:
		return pygame.mixer.music.get_busy()
	except pygame.error:
		return False
