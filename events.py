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