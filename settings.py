import os
import pygame
from pygame import mixer


pygame.init()


LOGICAL_WIDTH = 1220
LOGICAL_HEIGHT = 620
pygame.display.set_mode((LOGICAL_WIDTH, LOGICAL_HEIGHT))


BALL_SIZE = 34


bg_colour = pygame.Color('grey12')
light_grey = (200, 200, 200)
dim_grey = (110, 110, 110)


player_colour = (66, 165, 245)
opponent_colour = (255, 176, 32)
flash_colour = (255, 255, 255)
accent_colour = (185, 40, 40)

pitch_green = (30, 110, 58)
pitch_line = (230, 230, 230)
net_colour = (210, 210, 210)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_image(filename):
    path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(path):
        try:
            return pygame.image.load(path)
        except pygame.error as e:
            print(f"Couldn't load {path}: {e}")
    return None


PITCH_IMAGE = None
_pitch_raw = _load_image("pitch.png")
if _pitch_raw is not None:


    _landscape_pitch = pygame.transform.rotate(_pitch_raw.convert(), 90)
    PITCH_IMAGE = pygame.transform.smoothscale(_landscape_pitch, (LOGICAL_WIDTH, LOGICAL_HEIGHT))


BALL_IMAGE = None


WIN_SCORE = 11
MAX_BALL_SPEED = 12
MIN_BALL_SPEED_X = 6
MAX_ANGLE_INFLUENCE = 3
MAX_SPIN_INFLUENCE = 5
TRAIL_LENGTH = 10

HIT_FLASH_FRAMES = 8
SHAKE_FRAMES = 10
SHAKE_STRENGTH = 6

NET_DEPTH = 26
PENALTY_BOX_W = 150
PENALTY_BOX_H = 340

AI_REACTION_ERROR = 12
AI_RETARGET_MS = 500

PADDLE_SPEED = 11


game_font = pygame.font.Font('freesansbold.ttf', 18)
game_font2 = pygame.font.Font('freesansbold.ttf', 54)
small_font = pygame.font.Font('freesansbold.ttf', 22)
menu_title_font = pygame.font.Font('freesansbold.ttf', 64)
menu_font = pygame.font.Font('freesansbold.ttf', 30)
rules_font = pygame.font.Font('freesansbold.ttf', 22)


sounds = {}
for _name, _path in (
    ("wall", "pong wall noises.wav"),
    ("score", "pong scoring noise.wav"),
    ("paddle", "pong paddle noise.wav"),
):
    try:
        sounds[_name] = mixer.Sound(_path)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Couldn't load {_path}: {e}")
        sounds[_name] = None


def play_sound(name, state):
    if not state["muted"] and sounds.get(name):
        sounds[name].play()