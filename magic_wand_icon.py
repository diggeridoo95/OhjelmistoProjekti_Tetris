import pygame


def draw_magic_wand_cell(screen, cell_rect):
    """Draw a small magic-wand icon inside a tetris cell rect."""
    x = cell_rect.x
    y = cell_rect.y
    size = min(cell_rect.width, cell_rect.height)

    # Diagonal wand body
    start = (x + int(size * 0.22), y + int(size * 0.80))
    end = (x + int(size * 0.78), y + int(size * 0.26))
    body_width = max(2, size // 10)

    pygame.draw.line(screen, (222, 180, 95), start, end, body_width)
    pygame.draw.line(screen, (138, 102, 56), start, end, max(1, body_width // 2))

    # Tip gem
    tip_radius = max(2, size // 8)
    tip = end
    pygame.draw.circle(screen, (235, 170, 255), tip, tip_radius)
    pygame.draw.circle(screen, (255, 230, 255), tip, max(1, tip_radius // 2))

    # Simple sparkle near tip
    sparkle_len = max(2, size // 7)
    sx, sy = tip
    pygame.draw.line(screen, (255, 240, 180), (sx - sparkle_len, sy), (sx + sparkle_len, sy), max(1, body_width // 2))
    pygame.draw.line(screen, (255, 240, 180), (sx, sy - sparkle_len), (sx, sy + sparkle_len), max(1, body_width // 2))
