import pygame
import os

# SFX volume control
current_volume = 0.70

# Path to sound effect files
SFX_DIR = os.path.join(os.path.dirname(__file__), "sounds", "sfx")

# Dictionary to store loaded sounds for quick access
loaded_sounds = {}

# Game sound effect names mapping to filenames
# You can easily add or modify these filenames to match your audio files
GAME_SOUNDS = {
	"hard_drop": "hardrop.mp3",
	"block_turn": "blockturn.mp3",
	"mole_event": "moleevent.mp3",
	"inversion": "inversion.mp3",
	"bomb": "bomb.mp3",
	"magic_wand": "sauva.mp3",
	"line_clear": "clear.mp3",
	"game_over": "gameover.mp3",
}


def initialize():
	"""Initialize the SFX system."""
	global current_volume
	if pygame.mixer.get_init() is None:
		try:
			pygame.mixer.init()
		except pygame.error:
			return
	set_volume(current_volume)


def set_volume(volume):
	"""
	Set the SFX volume (0.0 to 1.0).
	
	Args:
		volume (float): Volume level between 0.0 (silent) and 1.0 (max)
	"""
	global current_volume
	current_volume = max(0.0, min(1.0, volume))
	# Update volume of all loaded sounds
	for sound in loaded_sounds.values():
		try:
			sound.set_volume(current_volume)
		except pygame.error:
			pass


def get_volume():
	"""Get the current SFX volume."""
	return current_volume


def load_sound(filename):
	"""
	Load a sound file into memory for quick playback.
	
	Args:
		filename (str): Name of the sound file in the sounds/sfx directory
	
	Returns:
		pygame.mixer.Sound: The loaded sound object, or None if loading failed
	"""
	if filename in loaded_sounds:
		return loaded_sounds[filename]
	
	try:
		sound_path = os.path.join(SFX_DIR, filename)
		if os.path.exists(sound_path):
			sound = pygame.mixer.Sound(sound_path)
			sound.set_volume(current_volume)
			loaded_sounds[filename] = sound
			return sound
		else:
			print(f"Warning: Sound file not found: {sound_path}")
			return None
	except pygame.error as e:
		print(f"Error loading sound {filename}: {e}")
		return None


def play(filename):
	"""
	Play a sound effect.
	
	Args:
		filename (str): Name of the sound file in the sounds/sfx directory
	
	Returns:
		pygame.mixer.Channel: The channel the sound is playing on, or None if playback failed
	"""
	sound = load_sound(filename)
	if sound:
		try:
			return sound.play()
		except pygame.error as e:
			print(f"Error playing sound {filename}: {e}")
			return None
	return None


def play_at_volume(filename, volume):
	"""
	Play a sound effect at a specific volume.
	
	Args:
		filename (str): Name of the sound file in the sounds/sfx directory
		volume (float): Volume level between 0.0 (silent) and 1.0 (max)
	
	Returns:
		pygame.mixer.Channel: The channel the sound is playing on, or None if playback failed
	"""
	old_volume = current_volume
	set_volume(volume)
	channel = play(filename)
	set_volume(old_volume)
	return channel


def stop_all():
	"""Stop all sound effects."""
	try:
		pygame.mixer.stop()
	except pygame.error:
		pass


def unload_all():
	"""Unload all cached sounds from memory."""
	global loaded_sounds
	loaded_sounds.clear()


def unload_sound(filename):
	"""
	Unload a specific sound from cache.
	
	Args:
		filename (str): Name of the sound file to unload
	"""
	if filename in loaded_sounds:
		del loaded_sounds[filename]


# ============================================================================
# GAME SOUND EFFECT FUNCTIONS - Easy to use directly from game code
# ============================================================================

def play_hard_drop():
	"""Play the hard drop sound effect."""
	return play(GAME_SOUNDS["hard_drop"])


def play_block_turn():
	"""Play the block rotation sound effect."""
	return play(GAME_SOUNDS["block_turn"])


def play_mole_event():
	"""Play the mole event sound effect."""
	return play(GAME_SOUNDS["mole_event"])


def play_inversion():
	"""Play the inversion ability sound effect."""
	return play(GAME_SOUNDS["inversion"])


def play_bomb():
	"""Play the bomb ability sound effect."""
	return play(GAME_SOUNDS["bomb"])


def play_magic_wand():
	"""Play the magic wand ability sound effect."""
	return play(GAME_SOUNDS["magic_wand"])


def play_line_clear():
	"""Play the line clear sound effect."""
	return play(GAME_SOUNDS["line_clear"])


def play_game_over():
	"""Play the game over sound effect."""
	return play(GAME_SOUNDS["game_over"])


def play_game_sound(sound_name):
	"""
	Play a game sound by its name key.
	
	Args:
		sound_name (str): Key from GAME_SOUNDS dictionary (e.g., 'hard_drop', 'bomb', 'magic_wand')
	
	Returns:
		pygame.mixer.Channel: The channel the sound is playing on, or None if not found
	
	Example:
		play_game_sound('hard_drop')
		play_game_sound('bomb')
	"""
	if sound_name in GAME_SOUNDS:
		return play(GAME_SOUNDS[sound_name])
	else:
		print(f"Warning: Game sound '{sound_name}' not found in GAME_SOUNDS")
		return None
