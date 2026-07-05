import math
import pygame

import settings
from settings import (
    bg_colour, light_grey, dim_grey, accent_colour, flash_colour,
    pitch_green, pitch_line,
    menu_title_font, menu_font, small_font, rules_font,
    WIN_SCORE,
)


def _draw_menu_ball(surface, center, radius):
    rect = pygame.Rect(0, 0, radius * 2, radius * 2)
    rect.center = center
    pygame.draw.ellipse(surface, (245, 245, 245), rect)
    pygame.draw.ellipse(surface, (30, 30, 30), rect, 2)

    def pentagon(cx, cy, size, angle_offset):
        pts = []
        for i in range(5):
            a = math.radians(angle_offset + i * 72 - 90)
            pts.append((cx + size * math.cos(a), cy + size * math.sin(a)))
        return pts

    pygame.draw.polygon(surface, (25, 25, 25), pentagon(center[0], center[1], radius * 0.4, 0))
    for i in range(5):
        a = math.radians(i * 72 + 36 - 90)
        px = center[0] + radius * 0.8 * math.cos(a)
        py = center[1] + radius * 0.8 * math.sin(a)
        pygame.draw.polygon(surface, (25, 25, 25), pentagon(px, py, radius * 0.24, i * 72))


def _draw_pitch_backdrop(surface):
    width, height = surface.get_size()
    surface.fill(pitch_green)


    stripe_w = 46
    for i, x in enumerate(range(0, width, stripe_w)):
        if i % 2 == 0:
            pygame.draw.rect(surface, (34, 118, 62), (x, 0, stripe_w, height))

    pygame.draw.line(surface, pitch_line, (width / 2, 0), (width / 2, height), 2)
    pygame.draw.circle(surface, pitch_line, (int(width / 2), int(height / 2)), 80, 2)

    box_w, box_h = 130, 300
    pygame.draw.rect(surface, pitch_line, (10, height / 2 - box_h / 2, box_w, box_h), 2)
    pygame.draw.rect(surface, pitch_line, (width - 10 - box_w, height / 2 - box_h / 2, box_w, box_h), 2)

    pygame.draw.line(surface, pitch_line, (0, 2), (width, 2), 3)
    pygame.draw.line(surface, pitch_line, (0, height - 2), (width, height - 2), 3)


    dim = pygame.Surface((width, height))
    dim.set_alpha(160)
    dim.fill(bg_colour)
    surface.blit(dim, (0, 0))


def draw_menu(screen, selected_ai):
    _draw_pitch_backdrop(screen)
    width, height = screen.get_size()

    _draw_menu_ball(screen, (width / 2 - 170, 130), 34)
    _draw_menu_ball(screen, (width / 2 + 170, 130), 34)

    title = menu_title_font.render("PONG", True, accent_colour)
    title_rect = title.get_rect(center=(width / 2, 130))
    screen.blit(title, title_rect)

    options = [
        ("1", "Player vs AI  (vertical pitch)", selected_ai is True),
        ("2", "Player vs Player  (horizontal pitch)", selected_ai is False),
    ]
    y = 280
    for key, label, is_selected in options:
        colour = flash_colour if is_selected else light_grey
        line = menu_font.render(f"[{key}]  {label}", True, colour)
        rect = line.get_rect(center=(width / 2, y))
        screen.blit(line, rect)
        y += 55

    hint = small_font.render("Enter: Start      H: How to Play      Esc: Quit", True, light_grey)
    hint_rect = hint.get_rect(center=(width / 2, height - 60))
    screen.blit(hint, hint_rect)


def draw_rules(screen):
    width, height = screen.get_size()
    screen.fill(bg_colour)

    title = menu_font.render("How to Play", True, accent_colour)
    title_rect = title.get_rect(center=(width / 2, 60))
    screen.blit(title, title_rect)

    lines = [
        f"First to {WIN_SCORE} points wins the match.",
        "",
        "Player vs AI (vertical pitch):",
        "   Your paddle: LEFT / RIGHT arrow keys",
        "",
        "Player vs Player (horizontal pitch):",
        "   Right paddle: UP / DOWN arrow keys",
        "   Left paddle:  W / S keys",
        "",
        "Where the ball hits your paddle changes its angle --",
        "hitting it near the edge sends it off sharper.",
        "A paddle that's moving when it makes contact adds a",
        "little extra steer in that direction, so a moving hit",
        "plays differently than a stationary one.",
        "",
        "The ball gradually speeds up the longer a rally lasts.",
        "",
        "P: Pause        M: Mute        Esc: Back to menu",
    ]
    y = 120
    for line in lines:
        rendered = rules_font.render(line, True, light_grey)
        rect = rendered.get_rect(center=(width / 2, y))
        screen.blit(rendered, rect)
        y += 30

    hint = small_font.render("Press any key to go back", True, dim_grey)
    hint_rect = hint.get_rect(center=(width / 2, height - 40))
    screen.blit(hint, hint_rect)


def handle_menu_events(selected_ai):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, selected_ai, "menu", False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False, selected_ai, "menu", False
            if event.key == pygame.K_1:
                selected_ai = True
            if event.key == pygame.K_2:
                selected_ai = False
            if event.key == pygame.K_h:
                return True, selected_ai, "rules", False
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return True, selected_ai, "playing", True
    return True, selected_ai, "menu", False


def handle_rules_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, "rules"
        if event.type == pygame.KEYDOWN:
            return True, "menu"
    return True, "rules"