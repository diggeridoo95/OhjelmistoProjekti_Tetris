import pygame


def draw_bomb_cell(screen, cell_rect):
    """Draw a small pixel-art style bomb inside one tetris cell rect."""
    x = cell_rect.x
    y = cell_rect.y
    size = min(cell_rect.width, cell_rect.height)

    unit = max(2, size // 9)

    # Bomb body (dark circle)
    body_radius = max(5, int(size * 0.40))
    body_center = (x + size // 2, y + int(size * 0.60))
    pygame.draw.circle(screen, (18, 18, 22), body_center, body_radius)
    pygame.draw.circle(screen, (60, 60, 72), body_center, body_radius, max(1, unit // 2))

    # Shine pixel
    shine_rect = pygame.Rect(
        body_center[0] - body_radius // 2,
        body_center[1] - body_radius // 2,
        max(2, unit),
        max(2, unit),
    )
    pygame.draw.rect(screen, (220, 220, 230), shine_rect)

    # Fuse (pixel line)
    fuse_start = (body_center[0], body_center[1] - body_radius)
    fuse_mid = (fuse_start[0] + max(2, unit), fuse_start[1] - max(2, unit))
    fuse_end = (fuse_mid[0] + max(2, unit), fuse_mid[1] - max(1, unit // 2))
    pygame.draw.line(screen, (130, 90, 40), fuse_start, fuse_mid, max(1, unit // 2))
    pygame.draw.line(screen, (130, 90, 40), fuse_mid, fuse_end, max(1, unit // 2))

    # Spark pixels
    spark = max(2, unit)
    sx, sy = fuse_end
    pygame.draw.rect(screen, (255, 208, 64), pygame.Rect(sx - spark // 2, sy - spark // 2, spark, spark))
    pygame.draw.rect(screen, (255, 120, 40), pygame.Rect(sx + spark // 2, sy - spark // 2, spark, spark))
    pygame.draw.rect(screen, (255, 244, 140), pygame.Rect(sx, sy - spark - 1, spark, spark))
