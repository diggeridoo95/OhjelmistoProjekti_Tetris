import pygame
import math
import os
import random
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

    def is_active(self):
        return self.active_until > 0 and pygame.time.get_ticks() < self.active_until

    def is_visible_now(self):
        if not self.flash_cells:
            return False

        now = pygame.time.get_ticks()
        if now >= self.active_until:
            self.clear()
            return False

        elapsed = now - self.started_at
        phase_count = self.flashes * 2
        phase_duration = max(1, self.duration_ms / phase_count)
        phase_index = int(elapsed / phase_duration)
        return phase_index % 2 == 0

    def remap_vertical_flip(self, row_count):
        if not self.flash_cells:
            return

        max_row = row_count - 1
        new_cells = []

        for row, col in self.flash_cells:
            new_row = max_row - row
            new_cells.append((new_row, col))

        self.flash_cells = new_cells

    def draw(self, screen, cell_size, offset_x, offset_y, visible_override=None):
        if visible_override is None:
            visible_now = self.is_visible_now()
        else:
            visible_now = bool(visible_override)

        if not visible_now:
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
    def __init__(self, duration_ms=620):
        self.duration_ms = max(120, duration_ms)
        self.started_at = 0
        self.active_until = 0
        self.cells = []

    def _draw_wand(self, screen, x, y, size, angle, alpha):
        shaft_len = max(14, int(size * 0.72))
        shaft_w = max(2, int(size * 0.12))

        dx = math.cos(angle)
        dy = math.sin(angle)
        sx = int(round(x - dx * shaft_len * 0.5))
        sy = int(round(y - dy * shaft_len * 0.5))
        ex = int(round(x + dx * shaft_len * 0.5))
        ey = int(round(y + dy * shaft_len * 0.5))

        shaft_color = (
            int(225 * alpha),
            int(182 * alpha),
            int(95 * alpha),
        )
        edge_color = (
            int(130 * alpha),
            int(95 * alpha),
            int(55 * alpha),
        )

        pygame.draw.line(screen, shaft_color, (sx, sy), (ex, ey), shaft_w)
        pygame.draw.line(screen, edge_color, (sx, sy), (ex, ey), max(1, shaft_w // 2))

        tip_r = max(2, int(size * 0.12))
        pygame.draw.circle(
            screen,
            (int(245 * alpha), int(180 * alpha), int(255 * alpha)),
            (ex, ey),
            tip_r,
        )
        pygame.draw.circle(
            screen,
            (int(255 * alpha), int(240 * alpha), int(255 * alpha)),
            (ex, ey),
            max(1, tip_r // 2),
        )

        sparkle_r = max(5, int(size * 0.18))
        sparkle_w = max(1, int(size * 0.04))
        pygame.draw.line(
            screen,
            (int(255 * alpha), int(244 * alpha), int(184 * alpha)),
            (ex - sparkle_r, ey),
            (ex + sparkle_r, ey),
            sparkle_w,
        )
        pygame.draw.line(
            screen,
            (int(255 * alpha), int(244 * alpha), int(184 * alpha)),
            (ex, ey - sparkle_r),
            (ex, ey + sparkle_r),
            sparkle_w,
        )

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
        fade = 1.0 - progress

        pulse = 0.5 + 0.5 * math.sin(progress * math.pi * 8.0)

        centers = [
            (
                offset_x + col * cell_size + (cell_size // 2),
                offset_y + row * cell_size + (cell_size // 2),
            )
            for row, col in self.cells
        ]
        if not centers:
            return

        avg_cx = sum(p[0] for p in centers) / len(centers)
        avg_cy = sum(p[1] for p in centers) / len(centers)
        min_x = min(p[0] for p in centers)
        max_x = max(p[0] for p in centers)
        min_y = min(p[1] for p in centers)
        max_y = max(p[1] for p in centers)

        cast_span = max(max_x - min_x, max_y - min_y)
        wand_orbit = max(18, int(cast_span * 0.25 + cell_size * (1.2 - 0.25 * progress)))
        wand_theta = (-math.pi * 0.65) + (progress * math.pi * 2.2)
        wand_x = int(round(avg_cx + math.cos(wand_theta) * wand_orbit))
        wand_y = int(round(avg_cy + math.sin(wand_theta) * wand_orbit))

        # Single cast sparkle cluster near the large wand tip.
        for i in range(7):
            spark_angle = wand_theta + i * (math.pi * 2 / 7) + (progress * math.pi * 1.2)
            spark_dist = max(6, int(cell_size * (0.10 + 0.07 * i)))
            sx = int(round(wand_x + math.cos(spark_angle) * spark_dist))
            sy = int(round(wand_y + math.sin(spark_angle) * spark_dist))
            sparkle_r = max(1, int(cell_size * 0.05))
            sparkle_fade = fade * (0.55 + 0.45 * (1.0 - i / 7.0))
            pygame.draw.circle(
                screen,
                (
                    int(225 * sparkle_fade),
                    int(188 * sparkle_fade),
                    int(255 * sparkle_fade),
                ),
                (sx, sy),
                sparkle_r,
            )

        # Expanding rings and a pulsing center glow.
        ring1 = max(2, int(round(cell_size * (0.18 + 0.44 * progress))))
        ring2 = max(2, int(round(cell_size * (0.08 + 0.68 * progress))))
        inner = max(1, int(round(cell_size * (0.09 + (0.16 * fade) + (0.06 * pulse)))))
        thickness = max(1, int(round(cell_size * 0.08)))

        ring_color = (
            int(225 * fade),
            int(172 * fade),
            int(255 * fade),
        )
        glow_color = (
            int(255 * fade),
            int((220 + 35 * pulse) * fade),
            int(255 * fade),
        )
        sparkle_color = (
            int(255 * fade),
            int((190 + 50 * pulse) * fade),
            int(255 * fade),
        )

        for row, col in self.cells:
            cx = offset_x + col * cell_size + (cell_size // 2)
            cy = offset_y + row * cell_size + (cell_size // 2)

            pygame.draw.circle(screen, ring_color, (cx, cy), ring1, thickness)
            pygame.draw.circle(screen, ring_color, (cx, cy), ring2, thickness)
            pygame.draw.circle(screen, glow_color, (cx, cy), inner)

            # Rotating sparkle particles around each affected cell.
            base_radius = max(3, int(round(cell_size * (0.18 + 0.34 * progress))))
            spark_radius = max(1, int(round(cell_size * 0.06)))
            rotation = progress * math.pi * 4.0
            for i in range(4):
                angle = rotation + i * (math.pi / 2)
                sx = int(round(cx + math.cos(angle) * base_radius))
                sy = int(round(cy + math.sin(angle) * base_radius))
                pygame.draw.circle(screen, sparkle_color, (sx, sy), spark_radius)

        wand_size = max(28, int(cell_size * (1.55 + min(0.45, cast_span / max(1, cell_size * 10)))))
        wand_angle = wand_theta + (math.pi * 0.35 * math.sin(progress * math.pi * 6.0))
        self._draw_wand(screen, wand_x, wand_y, wand_size, wand_angle, fade)

class MolePopEffect:
    def __init__(self, duration_ms=1200):
        self.duration_ms = max(400, duration_ms)
        self.pops = []

        base_dir = os.path.dirname(__file__)
        mole_face_path = os.path.join(base_dir, "pictures", "mole_face.png")
        self.mole_face = pygame.image.load(mole_face_path).convert_alpha()

        # Timing split for slower movement
        self.rise_portion = 0.42
        self.hold_portion = 0.28
        self.sink_portion = 0.30

    def _ease_out_cubic(self, t):
        t = max(0.0, min(1.0, t))
        return 1.0 - ((1.0 - t) ** 3)

    def _ease_in_cubic(self, t):
        t = max(0.0, min(1.0, t))
        return t ** 3

    def _emit_dirt_particles(self, pop, now, amount=3):
        for _ in range(amount):
            side = random.choice([-1, 1])

            pop["particles"].append({
                "spawn": now + random.randint(0, 30),
                "life": random.randint(260, 520),
                "x_offset": random.uniform(-0.12, 0.12),
                "y_offset": random.uniform(-0.05, 0.06),
                "vx": random.uniform(1.0, 3.0) * side,
                "vy": random.uniform(-3.8, -1.0),
                "gravity": random.uniform(0.12, 0.18),
                "radius": random.uniform(0.07, 0.15),
                 "color": random.choice([
                    (92, 69, 40),
                    (110, 82, 48),
                    (125, 94, 58),
                    (72, 52, 29),
                ]),
            })

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
                "particles": [],
                "last_emit": now,
            })

    def clear(self):
        self.pops = []

    def _get_visible_amount(self, progress):
        rise_end = self.rise_portion
        hold_end = rise_end + self.hold_portion

        if progress < rise_end:
            t = progress / rise_end
            return self._ease_out_cubic(t)
        elif progress < hold_end:
            return 1.0
        else:
            t = (progress - hold_end) / self.sink_portion
            return max(0.0, 1.0 - self._ease_in_cubic(t))
        
    def _get_paw_visibility(self, progress):
        rise_end = self.rise_portion
        hold_end = rise_end + self.hold_portion

        # Show paws only near the peak of the animation
        paw_start = rise_end * 0.72

        if progress < paw_start:
            return 0.0
        elif progress < rise_end:
            t = (progress - paw_start) / max(0.001, rise_end - paw_start)
            return self._ease_out_cubic(t)
        elif progress < hold_end:
            return 1.0
        else:
            sink_t = (progress - hold_end) / max(0.001, self.sink_portion)
            return max(0.0, 1.0 - min(1.0, sink_t * 6.0))
        
    def _draw_paws(self, screen, mound_x, mound_y, mound_w, mound_h, hole_y, cell_size, visibility):
        if visibility <= 0.0:
            return

        paw_color = (132, 96, 62)
        claw_color = (92, 72, 52)

        scale = max(0.75, visibility)

        paw_w = max(7, int(cell_size * 0.17 * scale))
        paw_h = max(10, int(cell_size * 0.24 * scale))

        # Place paws near the top edge of the mound, left and right of center.
        center_x = mound_x + mound_w // 2
        paw_y = hole_y + int(cell_size * 0.13)

        offset = int(cell_size * 0.10)

        left_paw_rect = pygame.Rect(
            center_x - offset - paw_w,
            paw_y,
            paw_w,
            paw_h
        )
        right_paw_rect = pygame.Rect(
            center_x + offset,
            paw_y,
            paw_w,
            paw_h
        )

        outline_color = (0, 0, 0)
        outline_width = max(1, int(cell_size * 0.04))

        # Fill
        pygame.draw.ellipse(screen, paw_color, left_paw_rect)
        pygame.draw.ellipse(screen, paw_color, right_paw_rect)

        # Outline
        pygame.draw.ellipse(screen, outline_color, left_paw_rect, outline_width)
        pygame.draw.ellipse(screen, outline_color, right_paw_rect, outline_width)




    def _draw_particles(self, screen, pop, now, cell_size, x, y, hole_x, hole_y, hole_w, hole_h):
        alive_particles = []

        for particle in pop["particles"]:
            age = now - particle["spawn"]
            if age < 0 or age > particle["life"]:
                continue

            alive_particles.append(particle)

            t = age / 18.0  # roughly frame-ish scaling
            fade = 1.0 - (age / particle["life"])

            px = (
                hole_x + (hole_w // 2)
                + particle["x_offset"] * cell_size
                + particle["vx"] * t
            )
            py = (
                hole_y + (hole_h // 2)
                + particle["y_offset"] * cell_size
                + particle["vy"] * t
                + particle["gravity"] * (t ** 2)
            )

            radius = max(1, int(cell_size * particle["radius"] * fade))
            color = tuple(max(0, min(255, int(c * fade))) for c in particle["color"])

            pygame.draw.circle(screen, color, (int(px), int(py)), radius)
        pop["particles"] = alive_particles

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
            visible_amount = self._get_visible_amount(progress)
            paw_visibility = self._get_paw_visibility(progress)

            # Keep spraying dirt briefly while the mole is digging upward
            spray_until = 0.6  # portion of total animation
            emit_interval = 50 # milliseconds between small bursts

            if progress < spray_until:
                while now - pop["last_emit"] >= emit_interval:
                    pop["last_emit"] += emit_interval
                    self._emit_dirt_particles(pop, pop["last_emit"], amount=random.randint(3, 5))

            row = pop["row"]
            col = pop["col"]

            x = offset_x + col * cell_size
            y = offset_y + row * cell_size

            # Hole near bottom of cell
            hole_w = int(cell_size * 0.90)
            hole_h = max(4, int(cell_size * 0.30))
            hole_x = x + (cell_size - hole_w) // 2
            hole_y = y + int(cell_size * 0.55)

            # Dirt mound
            mound_w = int(hole_w * 1.35)
            mound_h = int(hole_h * 2.40)
            mound_x = hole_x - (mound_w - hole_w) // 2
            mound_y = hole_y - int(hole_h * 0.65)

            pygame.draw.ellipse(
                screen,
                (95, 72, 42),
                (mound_x, mound_y, mound_w, mound_h)
            )


            # Hole base
            pygame.draw.ellipse(
                screen,
                (25, 18, 10),
                (hole_x, hole_y, hole_w, hole_h)
            )

            pygame.draw.ellipse(
                screen,
                (55, 40, 22),
                (hole_x + 2, hole_y + 1, max(2, hole_w - 4), max(2, hole_h - 2))
            )

            # Mole body
            mole_w = int(cell_size * 0.72)
            max_mole_h = int(cell_size * 0.88)
            mole_h = max(1, int(max_mole_h * visible_amount))

            # Start slightly lower for a "digging up" feel
            mole_x = x + (cell_size - mole_w) // 2
            mole_y = hole_y - mole_h + 4

            body_color = (120, 88, 55)
            head_color = (145, 104, 68)

            head_w = mole_w
            head_h = max(6, int(mole_h * 0.42))

            body_top = mole_y + head_h // 2
            body_h = max(1, hole_y - body_top + hole_h // 2)

            if body_h > 0:
                pygame.draw.rect(
                    screen,
                    body_color,
                    (mole_x, body_top, head_w, body_h)
                )

            head_extra = int(head_h * 0.35)
            head_rect = pygame.Rect(
                mole_x,
                mole_y,
                head_w,
                head_h + head_extra
            )
            pygame.draw.ellipse(screen, head_color, head_rect)

            # Gentle bob while visible
            bob = int(math.sin(progress * math.pi * 5.0) * max(1, cell_size * 0.03))
            draw_face_y = mole_y + bob

            if mole_h > 10:
                face_w = int(head_w * 1.9)
                face_h = int((head_h + head_extra) * 2.0)

                face_img = pygame.transform.scale(self.mole_face, (face_w, face_h))
                face_x = mole_x + (head_w - face_w) // 2
                face_y = draw_face_y - int((head_h + head_extra) * 0.4)

                screen.blit(face_img, (face_x, face_y))

            self._draw_paws(
                screen,
                mound_x,
                mound_y,
                mound_w,
                mound_h,
                hole_y,
                cell_size,
                paw_visibility
            )

            # Dirt particles
            self._draw_particles(screen, pop, now, cell_size, x, y, hole_x, hole_y, hole_w, hole_h)

        self.pops = active_pops


class BombExplosionEffect:
    def __init__(self, duration_ms=260):
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

    def remap_vertical_flip(self, row_count):
        if not self.cells:
            return

        max_row = row_count - 1
        remapped = []
        for row, col in self.cells:
            remapped.append((max_row - row, col))
        self.cells = remapped

    def draw(self, screen, cell_size, offset_x, offset_y, hide_blocks=False):
        if not self.cells:
            return

        now = pygame.time.get_ticks()
        if now >= self.active_until:
            self.clear()
            return

        progress = (now - self.started_at) / self.duration_ms
        progress = max(0.0, min(1.0, progress))
        fade = 1.0 - progress

        ring_color = (
            int(255 * fade),
            int(180 * fade),
            int(70 * fade),
        )
        core_color = (
            int(255 * fade),
            int(240 * fade),
            int(120 * fade),
        )

        for row, col in self.cells:
            cx = offset_x + col * cell_size + (cell_size // 2)
            cy = offset_y + row * cell_size + (cell_size // 2)

            base_radius = max(2, int(round(cell_size * 0.18)))
            ring_radius = base_radius + int(round(cell_size * 0.7 * progress))
            core_radius = max(1, int(round(cell_size * 0.2 * fade)))
            thickness = max(1, int(round(cell_size * 0.1)))

            pygame.draw.circle(screen, ring_color, (cx, cy), ring_radius, thickness)
            if not hide_blocks:
                pygame.draw.circle(screen, core_color, (cx, cy), core_radius)


class InversionFlashEffect:
    def __init__(self, duration_ms=300):
        self.duration_ms = max(120, duration_ms)
        self.started_at = 0
        self.active_until = 0

    def trigger(self):
        self.started_at = pygame.time.get_ticks()
        self.active_until = self.started_at + self.duration_ms

    def clear(self):
        self.started_at = 0
        self.active_until = 0

    def draw(self, screen, screen_width, screen_height):
        if self.active_until == 0:
            return

        now = pygame.time.get_ticks()
        if now >= self.active_until:
            self.clear()
            return

        progress = (now - self.started_at) / self.duration_ms
        progress = max(0.0, min(1.0, progress))

        # Short full-screen flash to make gravity inversion state change obvious.
        pulse = 1.0 - abs(0.5 - progress) * 2.0
        alpha = int(110 * pulse)

        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((180, 235, 255, alpha))
        screen.blit(overlay, (0, 0))