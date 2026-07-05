import sys
import math
import random

import pygame

import settings
import ai
import menu
from settings import (
    LOGICAL_WIDTH, LOGICAL_HEIGHT,
    light_grey, dim_grey, accent_colour, flash_colour,
    pitch_green, pitch_line, net_colour,
    WIN_SCORE, MAX_BALL_SPEED, MIN_BALL_SPEED_X,
    MAX_ANGLE_INFLUENCE, MAX_SPIN_INFLUENCE, TRAIL_LENGTH,
    HIT_FLASH_FRAMES, SHAKE_FRAMES, SHAKE_STRENGTH,
    NET_DEPTH, PENALTY_BOX_W, PENALTY_BOX_H, PADDLE_SPEED,
    game_font, game_font2, small_font,
    play_sound,
)

pygame.display.set_caption("Pong by MoMo")
clock = pygame.time.Clock()


window_scale = 1.0


game_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

player = pygame.Rect(LOGICAL_WIDTH - 20, LOGICAL_HEIGHT / 2 - 70, 10, 140)
opponent = pygame.Rect(10, LOGICAL_HEIGHT / 2 - 70, 10, 140)
ball = pygame.Rect(LOGICAL_WIDTH / 2 - 15, LOGICAL_HEIGHT / 2 - 15, 30, 30)


def new_match_state(opponent_is_ai):
    now = pygame.time.get_ticks()
    return {
        "player_score": 0,
        "opponent_score": 0,
        "ball_speed_x": 7 * random.choice((-1, 1)),
        "ball_speed_y": 7 * random.choice((-1, 1)),
        "player_up": False,
        "player_down": False,
        "opponent_up": False,
        "opponent_down": False,
        "serving": True,
        "serve_start_time": now,
        "ball_trail": [],
        "game_over": False,
        "winner": None,
        "paused": False,
        "last_speed_bump": now,
        "muted": False,
        "opponent_is_ai": opponent_is_ai,
        "ai_target_offset": 0,
        "ai_last_retarget": now,
        "player_flash": 0,
        "opponent_flash": 0,
        "shake_timer": 0,
        "ball_rotation": 0,
    }


def reset_positions():
    ball.center = (LOGICAL_WIDTH / 2, LOGICAL_HEIGHT / 2)
    player.centery = LOGICAL_HEIGHT / 2
    opponent.centery = LOGICAL_HEIGHT / 2


def start_serve(state):
    state["serving"] = True
    state["serve_start_time"] = pygame.time.get_ticks()
    state["last_speed_bump"] = pygame.time.get_ticks()
    ball.center = (LOGICAL_WIDTH / 2, LOGICAL_HEIGHT / 2)
    state["ball_trail"].clear()


def update_serve_countdown(state):
    elapsed_ms = pygame.time.get_ticks() - state["serve_start_time"]
    seconds_left = 3 - elapsed_ms // 1000

    if seconds_left <= 0:
        state["serving"] = False
        state["ball_speed_x"] = 7 * random.choice((-1, 1))
        state["ball_speed_y"] = 7 * random.choice((-1, 1))
        return None
    return seconds_left


def ball_animation(state):
    ball.x += state["ball_speed_x"]
    ball.y += state["ball_speed_y"]
    state["ball_rotation"] = (state["ball_rotation"] + state["ball_speed_x"] * 3) % 360


    state["ball_trail"].append(ball.center)
    if len(state["ball_trail"]) > TRAIL_LENGTH:
        state["ball_trail"].pop(0)

    if ball.top <= 0 or ball.bottom >= LOGICAL_HEIGHT:
        state["ball_speed_y"] *= -1
        ball.top = max(ball.top, 0)
        ball.bottom = min(ball.bottom, LOGICAL_HEIGHT)
        play_sound("wall", state)

    if ball.left <= 0:
        play_sound("score", state)
        state["player_score"] += 1
        state["shake_timer"] = SHAKE_FRAMES
        check_win(state)
        if not state["game_over"]:
            start_serve(state)

    if ball.right >= LOGICAL_WIDTH:
        play_sound("score", state)
        state["opponent_score"] += 1
        state["shake_timer"] = SHAKE_FRAMES
        check_win(state)
        if not state["game_over"]:
            start_serve(state)

    hit_player = ball.colliderect(player)
    hit_opponent = ball.colliderect(opponent)
    if hit_player or hit_opponent:
        if hit_player:
            apply_paddle_hit(state, player, state["player_up"], state["player_down"])
            ball.right = player.left
            state["player_flash"] = HIT_FLASH_FRAMES
        else:
            apply_paddle_hit(state, opponent, state["opponent_up"], state["opponent_down"])
            ball.left = opponent.right
            state["opponent_flash"] = HIT_FLASH_FRAMES
        play_sound("paddle", state)


    now = pygame.time.get_ticks()
    if now - state["last_speed_bump"] >= 6000:
        state["last_speed_bump"] = now
        state["ball_speed_x"] = _bump(state["ball_speed_x"])
        state["ball_speed_y"] = _bump(state["ball_speed_y"])


def apply_paddle_hit(state, paddle, moving_up, moving_down):
    direction = 1 if state["ball_speed_x"] < 0 else -1
    new_speed_x = abs(state["ball_speed_x"]) * 1.05
    new_speed_x = max(MIN_BALL_SPEED_X, min(new_speed_x, MAX_BALL_SPEED))
    state["ball_speed_x"] = direction * new_speed_x

    offset = (ball.centery - paddle.centery) / (paddle.height / 2)
    offset = max(-1.0, min(1.0, offset))
    angle_influence = offset * MAX_ANGLE_INFLUENCE

    spin_influence = 0
    if moving_up:
        spin_influence = -MAX_SPIN_INFLUENCE
    elif moving_down:
        spin_influence = MAX_SPIN_INFLUENCE

    state["ball_speed_y"] += angle_influence + spin_influence
    state["ball_speed_y"] = max(-MAX_BALL_SPEED, min(MAX_BALL_SPEED, state["ball_speed_y"]))

    if abs(state["ball_speed_y"]) < 2:
        state["ball_speed_y"] = 2 if state["ball_speed_y"] >= 0 else -2


def _bump(speed):
    if speed > 0:
        return min(speed + 1, MAX_BALL_SPEED)
    return max(speed - 1, -MAX_BALL_SPEED)


def check_win(state):
    if state["player_score"] >= WIN_SCORE:
        state["game_over"] = True
        state["winner"] = "Player"
    elif state["opponent_score"] >= WIN_SCORE:
        state["game_over"] = True
        state["winner"] = "Opponent"


def player_animation(state):
    if state["player_up"]:
        player.y -= PADDLE_SPEED
    if state["player_down"]:
        player.y += PADDLE_SPEED
    player.top = max(player.top, 0)
    player.bottom = min(player.bottom, LOGICAL_HEIGHT)


def opponent_animation(state):
    if state["opponent_is_ai"]:
        ai.ai_control(state, ball, opponent, LOGICAL_HEIGHT)
    else:
        if state["opponent_up"]:
            opponent.y -= PADDLE_SPEED
        if state["opponent_down"]:
            opponent.y += PADDLE_SPEED
    opponent.top = max(opponent.top, 0)
    opponent.bottom = min(opponent.bottom, LOGICAL_HEIGHT)


def draw_soccer_ball(surface, rect, rotation_deg):
    center = rect.center
    radius = rect.width / 2

    pygame.draw.ellipse(surface, (245, 245, 245), rect)
    pygame.draw.ellipse(surface, (40, 40, 40), rect, 1)

    def pentagon(cx, cy, size, angle_offset):
        pts = []
        for i in range(5):
            a = math.radians(angle_offset + i * 72 - 90)
            pts.append((cx + size * math.cos(a), cy + size * math.sin(a)))
        return pts

    pygame.draw.polygon(surface, (25, 25, 25), pentagon(center[0], center[1], radius * 0.4, rotation_deg))

    for i in range(5):
        a = math.radians(rotation_deg + i * 72 + 36 - 90)
        px = center[0] + radius * 0.8 * math.cos(a)
        py = center[1] + radius * 0.8 * math.sin(a)
        pygame.draw.polygon(surface, (25, 25, 25), pentagon(px, py, radius * 0.24, rotation_deg + i * 72))


def draw_net_strip(surface, x0, x1):
    clip_rect = pygame.Rect(x0, 0, x1 - x0, LOGICAL_HEIGHT)
    previous_clip = surface.get_clip()
    surface.set_clip(clip_rect)
    spacing = 18
    for offset in range(-LOGICAL_HEIGHT, (x1 - x0) + LOGICAL_HEIGHT, spacing):
        pygame.draw.line(surface, net_colour, (x0 + offset, 0), (x0 + offset - LOGICAL_HEIGHT, LOGICAL_HEIGHT), 1)
        pygame.draw.line(surface, net_colour, (x0 + offset, 0), (x0 + offset + LOGICAL_HEIGHT, LOGICAL_HEIGHT), 1)
    surface.set_clip(previous_clip)

    pygame.draw.rect(surface, pitch_line, (x0, 0, 3, LOGICAL_HEIGHT))
    pygame.draw.rect(surface, pitch_line, (x1 - 3, 0, 3, LOGICAL_HEIGHT))


def draw_pitch(surface):
    surface.fill(pitch_green)

    draw_net_strip(surface, 0, NET_DEPTH)
    draw_net_strip(surface, LOGICAL_WIDTH - NET_DEPTH, LOGICAL_WIDTH)

    pygame.draw.line(surface, pitch_line, (LOGICAL_WIDTH / 2, 0), (LOGICAL_WIDTH / 2, LOGICAL_HEIGHT), 2)
    pygame.draw.circle(surface, pitch_line, (int(LOGICAL_WIDTH / 2), int(LOGICAL_HEIGHT / 2)), 70, 2)
    pygame.draw.circle(surface, pitch_line, (int(LOGICAL_WIDTH / 2), int(LOGICAL_HEIGHT / 2)), 4)

    left_box = pygame.Rect(NET_DEPTH, LOGICAL_HEIGHT / 2 - PENALTY_BOX_H / 2, PENALTY_BOX_W, PENALTY_BOX_H)
    right_box = pygame.Rect(LOGICAL_WIDTH - NET_DEPTH - PENALTY_BOX_W, LOGICAL_HEIGHT / 2 - PENALTY_BOX_H / 2,
                             PENALTY_BOX_W, PENALTY_BOX_H)
    pygame.draw.rect(surface, pitch_line, left_box, 2)
    pygame.draw.rect(surface, pitch_line, right_box, 2)

    pygame.draw.line(surface, pitch_line, (0, 2), (LOGICAL_WIDTH, 2), 3)
    pygame.draw.line(surface, pitch_line, (0, LOGICAL_HEIGHT - 2), (LOGICAL_WIDTH, LOGICAL_HEIGHT - 2), 3)


def draw_ball_trail(surface, state):
    count = len(state["ball_trail"])
    for i, pos in enumerate(state["ball_trail"]):
        fade = (i + 1) / max(count, 1)
        radius = int(15 * fade)
        colour = tuple(int(c * fade) for c in light_grey)
        if radius > 0:
            pygame.draw.circle(surface, colour, pos, radius)


def draw_paddles(surface, state):
    player_colour = flash_colour if state["player_flash"] > 0 else accent_colour
    opponent_colour = flash_colour if state["opponent_flash"] > 0 else accent_colour
    pygame.draw.rect(surface, player_colour, player)
    pygame.draw.rect(surface, opponent_colour, opponent)
    if state["player_flash"] > 0:
        state["player_flash"] -= 1
    if state["opponent_flash"] > 0:
        state["opponent_flash"] -= 1


def draw_dashboard(surface, state):
    width, _ = surface.get_size()
    centre = width / 2
    p_score = game_font.render(f"{state['player_score']}", True, pitch_line)
    o_score = game_font.render(f"{state['opponent_score']}", True, pitch_line)
    surface.blit(p_score, (centre + 40, 20))
    surface.blit(o_score, (centre - 50, 20))

    if state["muted"]:
        mute_icon = small_font.render("muted", True, dim_grey)
        surface.blit(mute_icon, (width - 80, 15))


def draw_countdown(surface, seconds_left):
    width, height = surface.get_size()
    text = game_font2.render(str(seconds_left), True, (255, 0, 0))
    rect = text.get_rect(center=(width / 2, height / 2 - 60))
    surface.blit(text, rect)


def draw_game_over(surface, state):
    width, height = surface.get_size()
    text = game_font2.render(f"{state['winner']} wins!", True, (255, 0, 0))
    rect = text.get_rect(center=(width / 2, height / 2 - 40))
    surface.blit(text, rect)

    sub = small_font.render("R: Rematch      Esc: Menu", True, light_grey)
    sub_rect = sub.get_rect(center=(width / 2, height / 2 + 20))
    surface.blit(sub, sub_rect)


def draw_paused(surface, state):
    width, height = surface.get_size()
    text = game_font2.render("PAUSED", True, light_grey)
    rect = text.get_rect(center=(width / 2, height / 2 - 40))
    surface.blit(text, rect)

    sub = small_font.render("P: Resume      Esc: Menu", True, dim_grey)
    sub_rect = sub.get_rect(center=(width / 2, height / 2 + 20))
    surface.blit(sub, sub_rect)


def handle_events(state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, "playing"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return True, "menu"

            if event.key == pygame.K_r and state["game_over"]:
                reset_positions()
                new_state = new_match_state(state["opponent_is_ai"])
                state.clear()
                state.update(new_state)
                start_serve(state)

            if event.key == pygame.K_p and not state["game_over"]:
                state["paused"] = not state["paused"]

            if event.key == pygame.K_m:
                state["muted"] = not state["muted"]

            if not state["game_over"] and not state["paused"]:
                if state["opponent_is_ai"]:


                    if event.key == pygame.K_RIGHT:
                        state["player_up"] = True
                    if event.key == pygame.K_LEFT:
                        state["player_down"] = True
                else:
                    if event.key == pygame.K_UP:
                        state["player_up"] = True
                    if event.key == pygame.K_DOWN:
                        state["player_down"] = True
                    if event.key == pygame.K_w:
                        state["opponent_up"] = True
                    if event.key == pygame.K_s:
                        state["opponent_down"] = True

        if event.type == pygame.KEYUP:
            if state["opponent_is_ai"]:
                if event.key == pygame.K_RIGHT:
                    state["player_up"] = False
                if event.key == pygame.K_LEFT:
                    state["player_down"] = False
            else:
                if event.key == pygame.K_UP:
                    state["player_up"] = False
                if event.key == pygame.K_DOWN:
                    state["player_down"] = False
                if event.key == pygame.K_w:
                    state["opponent_up"] = False
                if event.key == pygame.K_s:
                    state["opponent_down"] = False

    return True, "playing"


def set_window_for_mode(vertical):
    global window_scale

    info = pygame.display.Info()
    max_w = int(info.current_w * 0.9)
    max_h = int(info.current_h * 0.9)

    logical_w, logical_h = (LOGICAL_HEIGHT, LOGICAL_WIDTH) if vertical else (LOGICAL_WIDTH, LOGICAL_HEIGHT)


    window_scale = min(max_w / logical_w, max_h / logical_h, 1.0)

    win_w = int(logical_w * window_scale)
    win_h = int(logical_h * window_scale)
    return pygame.display.set_mode((win_w, win_h))


def pong1():
    app_state = "menu"
    selected_ai = True
    state = None
    running = True

    screen = set_window_for_mode(False)

    while running:
        if app_state == "menu":
            running, selected_ai, next_state, start_game = menu.handle_menu_events(selected_ai)
            menu.draw_menu(screen, selected_ai)
            if start_game:
                screen = set_window_for_mode(selected_ai)
                reset_positions()
                state = new_match_state(selected_ai)
                start_serve(state)
            app_state = next_state

        elif app_state == "rules":
            running, app_state = menu.handle_rules_events()
            menu.draw_rules(screen)

        elif app_state == "playing":
            running, next_state = handle_events(state)
            if next_state == "menu":
                screen = set_window_for_mode(False)
            app_state = next_state
            if app_state != "playing":
                pygame.display.update()
                clock.tick(60)
                continue

            draw_pitch(game_surface)
            draw_paddles(game_surface, state)

            if not state["game_over"] and not state["paused"]:
                if state["serving"]:
                    seconds_left = update_serve_countdown(state)
                    player_animation(state)
                    opponent_animation(state)
                    draw_ball_trail(game_surface, state)
                    draw_soccer_ball(game_surface, ball, state["ball_rotation"])
                else:
                    seconds_left = None
                    player_animation(state)
                    opponent_animation(state)
                    ball_animation(state)
                    draw_ball_trail(game_surface, state)
                    draw_soccer_ball(game_surface, ball, state["ball_rotation"])
            else:
                seconds_left = None
                draw_ball_trail(game_surface, state)
                draw_soccer_ball(game_surface, ball, state["ball_rotation"])


            offset = (0, 0)
            if state["shake_timer"] > 0:
                strength = int(SHAKE_STRENGTH * (state["shake_timer"] / SHAKE_FRAMES))
                offset = (random.randint(-strength, strength), random.randint(-strength, strength))
                state["shake_timer"] -= 1

            screen.fill(pitch_green)
            if state["opponent_is_ai"]:


                frame = pygame.transform.rotate(game_surface, -90)
            else:
                frame = game_surface


            if window_scale != 1.0:
                frame = pygame.transform.smoothscale(frame, screen.get_size())
                offset = (int(offset[0] * window_scale), int(offset[1] * window_scale))

            screen.blit(frame, offset)


            draw_dashboard(screen, state)
            if state["serving"] and seconds_left is not None:
                draw_countdown(screen, seconds_left)
            if state["paused"]:
                draw_paused(screen, state)
            elif state["game_over"]:
                draw_game_over(screen, state)

        pygame.display.update()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    pong1()