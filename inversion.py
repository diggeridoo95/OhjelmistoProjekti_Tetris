class InversionController:
    """Handles timed inverted-gravity event and full-grid vertical flipping."""

    def __init__(self, interval_seconds=10, lock_target=3):
        self.interval_seconds = interval_seconds
        self.lock_target = lock_target
        self.inverted_gravity = False
        self.seconds_until_trigger = interval_seconds
        self.blocks_remaining = 0
        self.pending_activation = False

    def reset_state(self):
        self.inverted_gravity = False
        self.seconds_until_trigger = self.interval_seconds
        self.blocks_remaining = 0
        self.pending_activation = False

    def get_gravity_step(self):
        return -1 if self.inverted_gravity else 1

    def flip_grid_vertically(self, grid):
        flipped_grid = [[0 for _ in range(grid.num_cols)] for _ in range(grid.num_rows)]
        for row in range(grid.num_rows):
            for col in range(grid.num_cols):
                flipped_row = grid.num_rows - 1 - row
                flipped_grid[flipped_row][col] = grid.grid[row][col]
        grid.grid = flipped_grid

    def activate(self, grid):
        if self.inverted_gravity:
            return
        self.inverted_gravity = True
        self.blocks_remaining = self.lock_target
        self.flip_grid_vertically(grid)

    def deactivate(self, grid):
        if not self.inverted_gravity:
            return
        self.inverted_gravity = False
        self.blocks_remaining = 0
        self.seconds_until_trigger = self.interval_seconds
        self.flip_grid_vertically(grid)

    def update_timer(self):
        if self.inverted_gravity or self.pending_activation:
            return
        self.seconds_until_trigger -= 1
        if self.seconds_until_trigger <= 0:
            # Delay actual inversion until next block spawn.
            self.pending_activation = True

    def on_block_locked(self, grid):
        if not self.inverted_gravity:
            return False
        self.blocks_remaining -= 1
        if self.blocks_remaining <= 0:
            self.deactivate(grid)
            return True
        return False

    
    def apply_pending_activation(self, grid):
        if not self.pending_activation:
            return False
        self.pending_activation = False
        self.activate(grid)
        return True

    def spawn_block(self, block, grid):
        if self.inverted_gravity:
            cells = block.get_cell_positions()
            max_row = max(cell.row for cell in cells)
            shift_rows = (grid.num_rows - 1) - max_row
            block.move(shift_rows, 0)
        else:
            block.move(-1, 0)
        return block

