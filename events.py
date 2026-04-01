import random
import pygame

class LevelEvent:
    """Hook for optional level-specific mechanics."""
    def on_level_start(self, game):
        pass

class GarbageRows(LevelEvent):
    """Adds removable garbage rows when a level begins."""

    def __init__(self, row_count: int, holes_per_row: int = 4):
        self.row_count = max(0, row_count)
        self.holes_per_row = max(1, holes_per_row)
    
    def on_level_start(self, game):
        if self.row_count <= 0:
            return
        
        rows = game.grid.num_rows
        cols = game.grid.num_cols

        for i in range(self.row_count):

            for row in range(0, rows -1):
                game.grid.grid[row] = game.grid.grid[row +1][:]

            new_row = []
            for j in range(cols):
                available_colors = set(range(1, 8))
                if j > 0:
                    available_colors.discard(new_row[j-1])

                if rows - 2 >= 0:
                    cell_above = game.grid.grid[rows - 2][j]
                    if cell_above != 0:
                        available_colors.discard(cell_above)

                if available_colors:
                    new_row.append(random.choice(list(available_colors)))
                else:
                    # Fallback if no colors available
                    new_row.append(random.randint(1, 7))
            hole_count = min(self.holes_per_row, cols -1)
            for hole_col in random.sample(range(cols), k=hole_count):
                new_row[hole_col] = 0
            game.grid.grid[rows -1] = new_row

class MoleEvent(LevelEvent):
    """Randomly removes 1-3 occupied cells from the locked grid"""

    def __init__(self, trigger_chance=0.35, min_digs=1, max_digs=3,
                 check_interval_ms=4000,        #How often to check for triggering the event (ms)
                 cooldown_ms=10000,      #Cooldown period after triggering (ms)
                 min_filled_cells=8     #minimum number of filled cells required to trigger
                 ):
        self.trigger_chance = trigger_chance                        #trigger mechanism to be changed later and to have cooldowns
        self.min_digs = min_digs
        self.max_digs = max_digs
        self.check_interval_ms = check_interval_ms
        self.cooldown_ms = cooldown_ms
        self.min_filled_cells = min_filled_cells

        self.next_check_ms = 0
        self.cooldown_until_ms = 0

        self.pending_removals = []   #List of cells to remove after pop effect completes
        self.remove_delay_ms = 120   #Delay for actual removal to wait for animation to play

    def on_level_start(self, game):
        now = pygame.time.get_ticks()
        self.next_check_ms = now + self.check_interval_ms
        self.cooldown_until_ms = 0
        

    def on_tick(self, game):
        if game.game_over or game.is_level_transitioning():   #Cant trigger if game is over or transitioning between levels
            return
        
        if game.is_global_event_cooldown_active():   # Global event cooldown check
            return
        
        now = pygame.time.get_ticks()

        remaining = []
        for removal in self.pending_removals:
            if now >= removal['remove_at']:
                row = removal['row']
                col = removal['col']

                if game.grid.is_inside(row, col):
                    game.grid.grid[row][col] = 0

            else:
                remaining.append(removal)

        self.pending_removals = remaining

        if now < self.cooldown_until_ms:     #Check if we're still in cooldown period
            return

        if now < self.next_check_ms:     #Check if it's time to check for triggering the event
            return
        
        self.next_check_ms = now + self.check_interval_ms   #Schedule next check

        if random.random() > self.trigger_chance:       #roll for trigger
            return
        
        
        filled_cells = []       #Collect all occupied cells in the grid
        for row in range(game.grid.num_rows):
            for col in range(game.grid.num_cols):
                if game.grid.grid[row][col] != 0:   #if cell value is not 0, added to list of filled cells
                    filled_cells.append((row, col))

        bottom_row = game.grid.num_rows -1
        second_bottom_row = game.grid.num_rows -2

        filled_cells = [
            (row, col)
            for row, col in filled_cells
            if row not in (bottom_row, second_bottom_row)   #protect bottom 2 rows from digging
        ]

        if len(filled_cells) < self.min_filled_cells:        #cant trigger if not enough valid cells
            return
        
        if not filled_cells:    #safety check
            return
        
        dig_count = random.randint(self.min_digs, self.max_digs)  #random amount of hole between min and max
        dig_count = min(dig_count, len(filled_cells))           #cant dig more than valid cells

        chosen_cells = random.sample(filled_cells, dig_count)    #select cells to dig from valid cells

        game.mole_pop_effect.trigger(chosen_cells)   #trigger pop effect on dug cells

        for row, col in chosen_cells:
            self.pending_removals.append({
                'row': row,
                'col': col,
                'remove_at': now + self.remove_delay_ms
            })

        def start_global_event_cooldown(self, durations_ms=None):
            if durations_ms is None:
                durations_ms = self.current_level.global_event_cooldown_ms
            self.global_event_cooldown_until_ms = pygame.time.get_ticks() + durations_ms
        
        
        #optional status text support
        game.last_event_text = f"Mole dug {dig_count} hole{'s' if dig_count > 1 else ''}!"
        game.last_event_timer = 90

        self.cooldown_until_ms = now + self.cooldown_ms   #enter cooldown after triggering


class InvisibilityEvent(LevelEvent):
    """Randomly hides all blocks for a short duration."""

    PRE_FLASH_COUNT = 3
    PRE_FLASH_DURATION_MS = 1300

    def __init__(self, trigger_chance, duration_ms):
        self.trigger_chance = trigger_chance
        self.duration_ms = max(200, duration_ms)

    def on_tick(self, game):
        if game.game_over or game.is_level_transitioning():
            return
        
        if game.is_global_event_cooldown_active():  # Global event cooldown check
            return

        # Do not re-trigger while current invisibility is still active.
        if game.is_invisible_active():
            return

        if random.random() > self.trigger_chance:
            return

        # Collect locked cells and current falling block cells for pre-flash effect.
        flash_cells = game.get_invisibility_flash_cells()
        
        # Trigger invisibility with flash effect
        game.trigger_invisibility(self.duration_ms)
        def start_global_event_cooldown(self, durations_ms=None):
            if durations_ms is None:
                durations_ms = self.current_level.global_event_cooldown_ms
            self.global_event_cooldown_until_ms = pygame.time.get_ticks() + durations_ms
        # Flash locked cells 3 times before invisibility starts.
        game.trigger_invisibility(self.duration_ms, delay_ms=self.PRE_FLASH_DURATION_MS)
        if flash_cells:
            game.invisibility_preflash_effect.trigger(
                flash_cells,
                color=(200, 200, 255),
                flashes=self.PRE_FLASH_COUNT,
                duration_ms=self.PRE_FLASH_DURATION_MS,
            )
        game.last_event_text = "Invisibility!"
        game.last_event_timer = 90