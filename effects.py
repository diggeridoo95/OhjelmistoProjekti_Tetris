import pygame
from colors import Colors

class SpeedLines:
    def __init__(self, duration_ms=180):
        self.duration_ms = duration_ms
        self.active_until = 0
        self.effect_data = None

    def trigger(self, tiles, drop_d, max_drop_d, gravity_step, color=None):
        if not tiles or drop_d <= 0:
            self.clear()
            return
        
        min_col = min(tile.column for tile in tiles)
        max_col = max(tile.column for tile in tiles)
        min_row = min(tile.row for tile in tiles)
        max_row = max(tile.row for tile in tiles)
        width = max_col-min_col +1

        clamped_max_drop = max(1, max_drop_d)
        distance_ratio = min(1.0, drop_d / clamped_max_drop)
        # lyhyet pudotukset lyhyempiä ja pidemmät pitempiä
        length = distance_ratio ** 1.7

        self.effect_data = {
            "min_col":min_col,
            "min_row": min_row,
            "max_row": max_row,
            "width": width,
            "line_count": max(1, width+2),
            "length": length,
            "gravity_step": gravity_step,
            "color": color if color is not None else Colors.white,
        }
        self.active_until = pygame.time.get_ticks() + self.duration_ms
    
    def clear(self):
        self.active_until = 0
        self.effect_data = None

    def draw(self, screen, cell_size, offset_x, offset_y):
        if self.effect_data is None:
            return
        
        now = pygame.time.get_ticks()
        if now >= self.active_until:
            self.clear()
            return
        
        remaining = (self.active_until - now) / self.duration_ms
        data = self.effect_data
        min_length_px = 0.35 * cell_size
        max_length_px = 3.0 * cell_size
        line_length = min_length_px + (max_length_px - min_length_px) * data["length"]
        line_count = data["line_count"]
        span_width_px = data["width"] * cell_size
        gap_px = max(2, int(round(cell_size * 0.25)))

        if data["gravity_step"] >= 0:
            top_y = offset_y + data["min_row"] *cell_size
            line_bottom_y = top_y - gap_px
            line_top_y = line_bottom_y - line_length
        else:
            bottom_y = offset_y + (data["max_row"] + 1) * cell_size
            line_top_y = bottom_y + gap_px
            line_bottom_y = line_top_y + line_length
        thickness = max(2, int(round(cell_size*0.05)))

        color = data["color"]
        fade_intensity = 0.35 +(0.65*remaining)
        line_color =tuple(int(channel*fade_intensity)  for channel in color)

        for i in range(line_count):
            t = (i + 0.5) / line_count
            x = int(round(offset_x + data["min_col"]* cell_size +(t * span_width_px)))
            pygame.draw.line(
                screen, 
                line_color, 
                (x, line_bottom_y),
                (x, line_top_y),
                thickness
            )

class CellFlashEffect:
    def __init__(self, duration_ms = 150, flashes = 3):
        self.default_duration_ms = max(60, duration_ms)
        self.default_flashes = max(1, flashes)
        self.active_until = 0
        self.started_at = 0
        self.duration_ms = self.default_duration_ms
        self.flashes = self.default_flashes
        self.flash_cells = []
        self.flash_color = Colors.white

    def trigger(self, cells, color=None, flashes=None, duration_ms=None):
        norm = []
        for cell in cells:
            if hasattr(cell, "row") and hasattr(cell, "column"):
                row, col = cell.row, cell.column
            else:
                row, col = cell
            norm.append((int(row), int(col)))

        if not norm:
            self.clear()
            return
        
        self.flash_cells = list(dict.fromkeys(norm))
        
        if flashes is not None:
            self.flashes = max(1, flashes)
        else:
            self.flashes = self.default_flashes
        
        if duration_ms is not None:
            self.duration_ms = max(60, duration_ms)
        else: self.duration_ms = self.default_duration_ms

        if color is not None:
            self.flash_color = color
        else:
            self.flash_color = Colors.white

        self.started_at = pygame.time.get_ticks()
        self.active_until = self.started_at + self.duration_ms

    def clear(self):
        self.active_until = 0
        self.started_at = 0
        self.flash_cells = []

    def remap_vertical_flip(self, row_count):
        if not self.flash_cells:
            return

        max_row = row_count - 1
        new_cells = []

        for row, col in self.flash_cells:
            new_row = max_row - row
            new_cells.append((new_row, col))

        self.flash_cells = new_cells

    def draw(self, screen, cell_size, offset_x, offset_y):
        if not self.flash_cells:
            return

        now = pygame.time.get_ticks()

        if now >= self.active_until:
            self.clear()
            return

        elapsed = now - self.started_at

        phase_count = self.flashes * 2
        phase_duration = max(1, self.duration_ms / phase_count)

        phase_index = int(elapsed / phase_duration)

        if phase_index % 2 == 0:
            visible = True
        else:
            visible = False

        if not visible:
            return

        for row, col in self.flash_cells:
            x = offset_x + col * cell_size
            y = offset_y + row * cell_size

            tile_rect = pygame.Rect(
                x,
                y,
                cell_size - 1,
                cell_size - 1
            )

            pygame.draw.rect(screen, self.flash_color, tile_rect)

