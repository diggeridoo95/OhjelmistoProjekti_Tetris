import pygame
from colors import Colors

class Grid:
    def __init__(self):
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 30
        self.grid = [[0 for j in range(self.num_cols)] for i in range(self.num_rows)]
        self.colors = Colors.get_cell_colors()
        
    def print_grid(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                print(self.grid[row][column], end=" ")
            print()

    def get_cell_colors(self):
        
        dark_grey = (40, 40, 40)
        green = (0, 255, 0)
        red = (255, 0, 0)
        orange = (255, 165, 0)
        yellow = (255, 255, 0)
        purple = (128, 0, 128)
        cyan = (0, 255, 255)
        blue = (0, 0, 255)

        return [dark_grey, green, red, orange, yellow, purple, cyan, blue]
    
    def is_inside(self, row, column):
        if row >= 0 and row < self.num_rows and column >= 0 and column < self.num_cols:
            return True
        else:
            return False
    
    def is_empty(self, row, column):
        if row < 0:
            return True
        if row >= self.num_rows or column < 0 or column >= self.num_cols:
            return False
        if self.grid[row][column] == 0:
            return True
        return False
    
    def is_row_full(self, row):
        for column in range(self.num_cols):
            if self.grid[row][column] == 0:
                return False
        return True
    
    def clear_row(self, row):
        for column in range(self.num_cols):
            self.grid[row][column] = 0

    def move_row_down(self, row, num_rows):
        for column in range(self.num_cols):
            self.grid[row+num_rows][column] = self.grid[row][column]
            self.grid[row][column] = 0

    def clear_full_rows(self):
        completed = 0
        for row in range(self.num_rows-1, 0, -1):
            if self.is_row_full(row):
                self.clear_row(row)
                completed += 1
            elif completed > 0:
                self.move_row_down(row, completed)
        return completed
    
    def reset(self):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                self.grid[row][column] = 0
    
    def bomb_explosion(self, center_row, center_col):
        """
        Trigger bomb explosion at the given position.
        Removes blocks in a bomb-like pattern (circular/cross pattern).
        
        Args:
            center_row: Row position of explosion center
            center_col: Column position of explosion center
        """
        # Define bomb explosion pattern (relative positions from center)
        explosion_pattern = [
            (0, 0),      # center
            (-1, 0), (1, 0), (0, -1), (0, 1),      # adjacent cells (cross)
            (-1, -1), (-1, 1), (1, -1), (1, 1),    # diagonals
            (-2, 0), (2, 0), (0, -2), (0, 2),      # extended cross
        ]
        
        # Remove blocks in explosion area
        for row_offset, col_offset in explosion_pattern:
            target_row = center_row + row_offset
            target_col = center_col + col_offset
            
            if self.is_inside(target_row, target_col):
                self.grid[target_row][target_col] = 0
        
        # Apply gravity and clear completed rows
        self.clear_full_rows()
        
    def draw(self, screen, offset_x=11, offset_y=11):
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                cell_value = self.grid[row][column]
                cell_rect = pygame.Rect(column*self.cell_size + offset_x, row*self.cell_size + offset_y, 
                                        self.cell_size-1, self.cell_size-1)
                pygame.draw.rect(screen, self.colors[cell_value], cell_rect)