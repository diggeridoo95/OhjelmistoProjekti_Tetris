import random

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
            
            fill_value = random.randint(1,7)
            new_row = [fill_value for j in range(cols)]
            hole_count = min(self.holes_per_row, cols -1)
            for hole_col in random.sample(range(cols), k=hole_count):
                new_row[hole_col] = 0
            game.grid.grid[rows -1] = new_row

class MoleEvent(LevelEvent):
    """Randomly removes 1-3 occupied cells from the locked grid"""

    def __init__(self, trigger_chance=0.02, min_digs=1, max_digs=3): #Setting trigger chance and amount of holes dug (1-3)
        self.trigger_chance = trigger_chance                        #trigger mechanism to be changed later and to have cooldowns
        self.min_digs = min_digs
        self.max_digs = max_digs
    
    def on_tick(self, game):
        if game.game_over or game.is_level_transitioning():   #Cant trigger if game is over or transitioning between levels
            return
        
        #Random decimal between 0 and 1, if above trigger chance, do not trigger
        if random.random() > self.trigger_chance:
            return
        
        filled_cells = []       #Collect all occupied cells in the grid
        for row in range(game.grid.num_rows):
            for col in range(game.grid.num_cols):
                if game.grid.grid[row][col] != 0:   #if cell value is not 0, added to list of filled cells
                    filled_cells.append((row, col))

        if not filled_cells:        #cant trigger if no valid cells
            return
        
        dig_count = random.randint(self.min_digs, self.max_digs)  #random amount of hole between min and max
        dig_count = min(dig_count, len(filled_cells))           #cant dig more than valid cells

        chosen_cells = random.sample(filled_cells, dig_count)    #select cells to dig from valid cells

        for row, col in chosen_cells:
            game.grid.grid[row][col] = 0
        
        #optional status text support
        game.last_event_text = f"Mole dug {dig_count} hole{'s' if dig_count > 1 else ''}!"
        game.last_event_timer = 90