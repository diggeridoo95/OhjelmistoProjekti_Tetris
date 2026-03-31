import pygame
from colors import Colors


class PauseMenu:
    def __init__(self):
        self.options = ["Continue", "Exit to Main Menu"]
        self.selected_index = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.options)
            return None

        if event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.options)
            return None

        if event.key == pygame.K_p:
            return "continue"

        if event.key == pygame.K_RETURN:
            if self.selected_index == 0:
                return "continue"
            return "main_menu"

        return None

    def draw(self, screen):
        width, height = screen.get_size()

        title_font = pygame.font.Font(None, max(40, width // 20))
        option_font = pygame.font.Font(None, max(30, width // 28))

        panel_w = max(280, width // 3)
        panel_h = max(190, height // 3)
        panel_x = (width - panel_w) // 2
        panel_y = (height - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        dim_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 120))
        screen.blit(dim_surface, (0, 0))

        panel_surface = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 100), panel_surface.get_rect(), border_radius=14)
        screen.blit(panel_surface, (panel_x, panel_y))
        pygame.draw.rect(screen, Colors.light_blue, panel_rect, max(2, width // 500), 14)

        title_shadow = title_font.render("PAUSED", True, Colors.dark_grey)
        title_shadow_rect = title_shadow.get_rect(center=(panel_rect.centerx + 2, panel_rect.y + 36 + 2))
        screen.blit(title_shadow, title_shadow_rect)

        title_surface = title_font.render("PAUSED", True, Colors.white)
        title_rect = title_surface.get_rect(center=(panel_rect.centerx, panel_rect.y + 36))
        screen.blit(title_surface, title_rect)

        option_spacing = max(42, panel_h // 4)
        option_start_y = panel_rect.y + 88

        for i, option in enumerate(self.options):
            y_pos = option_start_y + i * option_spacing

            option_shadow = option_font.render(option, True, Colors.dark_grey)
            option_shadow_rect = option_shadow.get_rect(center=(panel_rect.centerx + 2, y_pos + 2))
            screen.blit(option_shadow, option_shadow_rect)

            option_text = option_font.render(option, True, Colors.white if i == self.selected_index else Colors.light_blue2)
            option_rect = option_text.get_rect(center=(panel_rect.centerx, y_pos))

            if i == self.selected_index:
                highlight_rect = pygame.Rect(panel_rect.x + 6, option_rect.y - 8, panel_rect.width - 12, option_rect.height + 16)
                highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(highlight_surface, (255, 255, 255, 150), highlight_surface.get_rect(), border_radius=10)
                screen.blit(highlight_surface, (highlight_rect.x, highlight_rect.y))

            screen.blit(option_text, option_rect)
