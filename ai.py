import random
import pygame

import settings


def _predict_ball_y(ball, target_x, speed_x, speed_y, screen_height):
    if speed_x == 0:
        return ball.centery

    time_to_reach = abs(target_x - ball.centerx) / abs(speed_x)
    raw_y = ball.centery + speed_y * time_to_reach

    period = 2 * screen_height
    y_mod = raw_y % period
    if y_mod < 0:
        y_mod += period
    if y_mod > screen_height:
        y_mod = period - y_mod
    return y_mod


def ai_control(state, ball, opponent, screen_height):
    now = pygame.time.get_ticks()
    ball_incoming = state["ball_speed_x"] < 0

    if now - state["ai_last_retarget"] > settings.AI_RETARGET_MS:
        state["ai_target_offset"] = random.randint(
            -settings.AI_REACTION_ERROR, settings.AI_REACTION_ERROR
        )
        state["ai_last_retarget"] = now

    if ball_incoming:
        predicted_y = _predict_ball_y(
            ball, opponent.centerx, state["ball_speed_x"], state["ball_speed_y"], screen_height
        )
        target_y = predicted_y + state["ai_target_offset"]
    else:
        target_y = screen_height / 2

    if opponent.centery < target_y - 5:
        opponent.y += settings.PADDLE_SPEED
    elif opponent.centery > target_y + 5:
        opponent.y -= settings.PADDLE_SPEED