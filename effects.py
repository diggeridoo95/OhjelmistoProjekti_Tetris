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


class MagicWandEffect:
    def __init__(self, duration_ms=420):
        self.duration_ms = max(120, duration_ms)
        self.started_at = 0
        self.active_until = 0
        self.cells = []

    def trigger(self, cells):
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

        self.cells = list(dict.fromkeys(norm))
        self.started_at = pygame.time.get_ticks()
        self.active_until = self.started_at + self.duration_ms

    def clear(self):
        self.started_at = 0
        self.active_until = 0
        self.cells = []

    def draw(self, screen, cell_size, offset_x, offset_y):
        if not self.cells:
            return

        now = pygame.time.get_ticks()
        if now >= self.active_until:
            self.clear()
            return

        progress = (now - self.started_at) / self.duration_ms
        progress = max(0.0, min(1.0, progress))

        # Two expanding rings plus a center glow for a wand-like burst.
        ring1 = max(2, int(round(cell_size * (0.18 + 0.42 * progress))))
        ring2 = max(2, int(round(cell_size * (0.08 + 0.62 * progress))))
        inner = max(1, int(round(cell_size * (0.1 + 0.2 * (1.0 - progress)))))
        thickness = max(1, int(round(cell_size * 0.08)))

        fade = 1.0 - progress
        ring_color = (
            int(220 * fade),
            int(170 * fade),
            int(255 * fade),
        )
        glow_color = (
            int(255 * fade),
            int(230 * fade),
            int(255 * fade),
        )

        for row, col in self.cells:
            cx = offset_x + col * cell_size + (cell_size // 2)
            cy = offset_y + row * cell_size + (cell_size // 2)

            pygame.draw.circle(screen, ring_color, (cx, cy), ring1, thickness)
            pygame.draw.circle(screen, ring_color, (cx, cy), ring2, thickness)
            pygame.draw.circle(screen, glow_color, (cx, cy), inner)

class MolePopEffect:
    def __init__(self, duration_ms=600):
        self.duration_ms = max(200, duration_ms)
        self.pops = []

    def trigger(self, cells):
        now = pygame.time.get_ticks()

        for cell in cells:
            if hasattr(cell, "row") and hasattr(cell, "column"):
                row, col = cell.row, cell.column
            else:
                row, col = cell

            self.pops.append({
                "row": int(row),
                "col": int(col),
                "start": now,
            })

    def clear(self):
        self.pops = []

    def draw(self, screen, cell_size, offset_x, offset_y):
        if not self.pops:
            return

        now = pygame.time.get_ticks()
        active_pops = []

        for pop in self.pops:
            elapsed = now - pop["start"]
            if elapsed >= self.duration_ms:
                continue

            active_pops.append(pop)

            progress = elapsed / self.duration_ms

            # Rise -> short hold -> sink
            if progress < 0.4:
                visible_amount = progress / 0.4
            elif progress < 0.7:
                visible_amount = 1.0
            else:
                visible_amount = max(0.0, 1.0 - ((progress - 0.7) / 0.3))

            row = pop["row"]
            col = pop["col"]

            x = offset_x + col * cell_size
            y = offset_y + row * cell_size

            # Small hole near bottom of the target cell
            hole_w = int(cell_size * 0.58)
            hole_h = max(4, int(cell_size * 0.16))
            hole_x = x + (cell_size - hole_w) // 2
            hole_y = y + int(cell_size * 0.72)

            pygame.draw.ellipse(
                screen,
                (30, 20, 10),
                (hole_x, hole_y, hole_w, hole_h)
            )

            # Mole body rises from the hole
            mole_w = int(cell_size * 0.56)
            max_mole_h = int(cell_size * 0.65)
            mole_h = max(1, int(max_mole_h * visible_amount))

            mole_x = x + (cell_size - mole_w) // 2
            mole_y = hole_y - mole_h + 2

            # Body
            pygame.draw.rect(
                screen,
                (125, 88, 55),
                (mole_x, mole_y, mole_w, mole_h)
            )

            # Head top
            head_h = max(2, int(mole_h * 0.35))
            pygame.draw.rect(
                screen,
                (145, 104, 68),
                (mole_x + 2, mole_y, max(2, mole_w - 4), head_h)
            )

            # Eyes
            if mole_h > 6:
                eye_size = max(1, cell_size // 12)
                eye_y = mole_y + max(1, head_h // 2)
                pygame.draw.rect(screen, (0, 0, 0), (mole_x + 4, eye_y, eye_size, eye_size))
                pygame.draw.rect(screen, (0, 0, 0), (mole_x + mole_w - 4 - eye_size, eye_y, eye_size, eye_size))

            # Nose
            if mole_h > 8:
                nose_w = max(2, cell_size // 8)
                nose_h = max(2, cell_size // 10)
                nose_x = mole_x + (mole_w - nose_w) // 2
                nose_y = mole_y + head_h + 1
                pygame.draw.rect(screen, (220, 120, 140), (nose_x, nose_y, nose_w, nose_h))

        self.pops = active_pops