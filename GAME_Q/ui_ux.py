"""UI/UX configuration, theme state, audio, animation helpers, coordinates, particles, and status helpers."""

import math
import array
import pygame
import pygame.font

from logic import QuoridorLogic


CELL = 50
GAP = 15
MARGIN = 20
BOARD_SIZE = 9 * CELL + 8 * GAP
WIN_SIZE = BOARD_SIZE + 2 * MARGIN
UI_AREA_HEIGHT = 140
FPS = 60

pygame.init()
pygame.font.init()
try:
    pygame.mixer.init(frequency=22000, size=-16, channels=1)
    AUDIO_READY = True
except pygame.error:
    AUDIO_READY = False

FONT = pygame.font.SysFont("Arial", 22, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 18)
TITLE_FONT = pygame.font.SysFont("Arial", 34, bold=True)
BIG_FONT = pygame.font.SysFont("Arial", 50, bold=True)
CARD_TITLE_FONT = pygame.font.SysFont("Arial", 24, bold=True)
CARD_LABEL_FONT = pygame.font.SysFont("Arial", 16, bold=True)
TEXT_COLOR = (255, 255, 255)

THEMES = {
    "Classic": {
        'bg': (20, 22, 28),
        'board': (62, 68, 84),
        'board_hover': (78, 86, 104),
        'move_hint': (102, 142, 120),
        'wall': (220, 172, 60),
        'wall_glow': (255, 214, 120),
        'button': (56, 60, 74),
        'button_hover': (88, 96, 118),
        'button_glow': (120, 145, 210),
        'goal_top': (95, 40, 40),
        'goal_bottom': (34, 54, 98),
        'panel': (40, 42, 52),
        'panel_border': (180, 180, 180),
        'menu_ring': (90, 115, 180),
        'menu_card': (38, 42, 56),
        'menu_card_hover': (52, 58, 78),
        'theme_chip_border': (180, 190, 210),
        'particles': [(255, 226, 148), (255, 147, 95), (126, 211, 255), (255, 255, 255), (255, 92, 92)],
    },
    "Neon": {
        'bg': (10, 12, 20),
        'board': (28, 39, 62),
        'board_hover': (40, 63, 98),
        'move_hint': (70, 220, 165),
        'wall': (255, 77, 152),
        'wall_glow': (255, 155, 205),
        'button': (24, 31, 52),
        'button_hover': (39, 52, 83),
        'button_glow': (78, 222, 240),
        'goal_top': (102, 20, 58),
        'goal_bottom': (0, 80, 98),
        'panel': (20, 26, 44),
        'panel_border': (135, 245, 255),
        'menu_ring': (42, 195, 220),
        'menu_card': (20, 28, 50),
        'menu_card_hover': (32, 42, 70),
        'theme_chip_border': (135, 245, 255),
        'particles': [(255, 93, 177), (84, 255, 233), (255, 255, 255), (148, 116, 255), (110, 255, 150)],
    },
    "Royal": {
        'bg': (18, 14, 28),
        'board': (68, 54, 96),
        'board_hover': (92, 72, 125),
        'move_hint': (180, 154, 92),
        'wall': (196, 146, 44),
        'wall_glow': (255, 210, 110),
        'button': (56, 44, 82),
        'button_hover': (83, 67, 116),
        'button_glow': (230, 180, 72),
        'goal_top': (92, 34, 54),
        'goal_bottom': (44, 40, 115),
        'panel': (42, 32, 62),
        'panel_border': (225, 196, 120),
        'menu_ring': (180, 145, 82),
        'menu_card': (45, 34, 68),
        'menu_card_hover': (67, 48, 96),
        'theme_chip_border': (225, 196, 120),
        'particles': [(255, 224, 136), (230, 177, 76), (245, 245, 255), (176, 155, 255), (255, 116, 142)],
    },
}

ACTIVE_THEME = "Classic"
BG_COLOR = (0, 0, 0)
BOARD_COLOR = (0, 0, 0)
BOARD_HOVER_COLOR = (0, 0, 0)
MOVE_HINT_COLOR = (0, 0, 0)
WALL_COLOR = (0, 0, 0)
WALL_GLOW_COLOR = (0, 0, 0)
BUTTON_COLOR = (0, 0, 0)
BUTTON_HOVER = (0, 0, 0)
BUTTON_GLOW = (0, 0, 0)
GOAL_TOP_COLOR = (0, 0, 0)
GOAL_BOTTOM_COLOR = (0, 0, 0)
PANEL_COLOR = (0, 0, 0)
PANEL_BORDER = (0, 0, 0)
MENU_RING_COLOR = (0, 0, 0)
MENU_CARD_COLOR = (0, 0, 0)
MENU_CARD_HOVER = (0, 0, 0)
THEME_CHIP_BORDER = (0, 0, 0)
PARTICLE_COLORS = []

BUTTON_TEXT = (240, 240, 240)
MESSAGE_INFO = (220, 220, 220)
MESSAGE_SUCCESS = (100, 230, 130)
MESSAGE_ERROR = (255, 125, 125)
INVALID_PREVIEW_COLOR = (220, 70, 70, 150)
VALID_PREVIEW_COLOR = (70, 200, 100, 150)
P_COLORS = [(255, 74, 74), (72, 128, 255)]
MODE_OPTIONS = [
    {"key": "hvh", "name": "Human vs Human", "subtitle": "Ready now", "available": True},
    {"key": "hvai", "name": "Human vs AI", "subtitle": "Ready now", "available": True},
    {"key": "aivai", "name": "AI vs AI", "subtitle": "Coming soon", "available": False},
]
AI_LEVEL_OPTIONS = [
    {
        "key": "easy",
        "name": "Easy",
        "subtitle": "Simple AI"
    },
    {
        "key": "medium",
        "name": "Medium",
        "subtitle": "Balanced AI"
    },
    {
        "key": "hard",
        "name": "Hard",
        "subtitle": "Strong AI"
    },
]
MODE_LABELS = {item['key']: item['name'] for item in MODE_OPTIONS}

screen = pygame.display.set_mode((WIN_SIZE, WIN_SIZE + UI_AREA_HEIGHT))
pygame.display.set_caption("Quoridor AI Project")
clock = pygame.time.Clock()

NEW_GAME_BTN = pygame.Rect(WIN_SIZE - 120, WIN_SIZE + 15, 100, 34)
MENU_BTN = pygame.Rect(WIN_SIZE - 120, WIN_SIZE + 55, 100, 34)

ACTION_MOVE_BTN = pygame.Rect(WIN_SIZE - 330, WIN_SIZE + 15, 100, 34)
ACTION_WALL_BTN = pygame.Rect(WIN_SIZE - 330, WIN_SIZE + 55, 100, 34)

UNDO_BTN = pygame.Rect(WIN_SIZE - 225, WIN_SIZE + 15, 100, 34)
REDO_BTN = pygame.Rect(WIN_SIZE - 225, WIN_SIZE + 55, 100, 34)

SAVE_BTN = pygame.Rect(WIN_SIZE - 225, WIN_SIZE + 95, 100, 34)


def apply_theme(theme_name):
    global ACTIVE_THEME, BG_COLOR, BOARD_COLOR, BOARD_HOVER_COLOR, MOVE_HINT_COLOR
    global WALL_COLOR, WALL_GLOW_COLOR, BUTTON_COLOR, BUTTON_HOVER, BUTTON_GLOW
    global GOAL_TOP_COLOR, GOAL_BOTTOM_COLOR, PANEL_COLOR, PANEL_BORDER
    global MENU_RING_COLOR, MENU_CARD_COLOR, MENU_CARD_HOVER, THEME_CHIP_BORDER
    global PARTICLE_COLORS

    ACTIVE_THEME = theme_name
    palette = THEMES[theme_name]
    BG_COLOR = palette['bg']
    BOARD_COLOR = palette['board']
    BOARD_HOVER_COLOR = palette['board_hover']
    MOVE_HINT_COLOR = palette['move_hint']
    WALL_COLOR = palette['wall']
    WALL_GLOW_COLOR = palette['wall_glow']
    BUTTON_COLOR = palette['button']
    BUTTON_HOVER = palette['button_hover']
    BUTTON_GLOW = palette['button_glow']
    GOAL_TOP_COLOR = palette['goal_top']
    GOAL_BOTTOM_COLOR = palette['goal_bottom']
    PANEL_COLOR = palette['panel']
    PANEL_BORDER = palette['panel_border']
    MENU_RING_COLOR = palette['menu_ring']
    MENU_CARD_COLOR = palette['menu_card']
    MENU_CARD_HOVER = palette['menu_card_hover']
    THEME_CHIP_BORDER = palette['theme_chip_border']
    PARTICLE_COLORS = list(palette['particles'])


apply_theme(ACTIVE_THEME)


# --- Audio helpers ---
SOUNDS = {}
SOUND_ENABLED = AUDIO_READY


def _build_wave(freq=440, duration=0.09, volume=0.35, wave="sine", attack=0.01, decay=0.06):
    if not AUDIO_READY:
        return None
    sample_rate = 22050
    sample_count = max(1, int(sample_rate * duration))
    buf = array.array('h')
    for i in range(sample_count):
        t = i / sample_rate
        if wave == "square":
            raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        elif wave == "triangle":
            raw = (2 / math.pi) * math.asin(math.sin(2 * math.pi * freq * t))
        else:
            raw = math.sin(2 * math.pi * freq * t)

        if t < attack:
            env = t / max(attack, 1e-6)
        else:
            env = max(0.0, 1.0 - (t - attack) / max(decay, 1e-6))
        sample = int(max(-1.0, min(1.0, raw * env * volume)) * 32767)
        buf.append(sample)
    return pygame.mixer.Sound(buffer=buf.tobytes())


def init_sounds():
    if not AUDIO_READY:
        return
    SOUNDS.update({
        "click": _build_wave(540, 0.06, 0.2, "triangle", 0.004, 0.05),
        "start": _build_wave(660, 0.11, 0.2, "sine", 0.01, 0.10),
        "move": _build_wave(430, 0.08, 0.28, "triangle", 0.004, 0.07),
        "wall": _build_wave(260, 0.10, 0.2, "square", 0.004, 0.10),
        "error": _build_wave(180, 0.12, 0.2, "square", 0.004, 0.11),
        "win": _build_wave(880, 0.22, 0.32, "sine", 0.01, 0.20),
        "theme": _build_wave(720, 0.07, 0.24, "triangle", 0.004, 0.06),
        "toggle": _build_wave(510, 0.05, 0.23, "triangle", 0.002, 0.05),
    })


init_sounds()


def play_sound(name):
    if SOUND_ENABLED and AUDIO_READY:
        sound = SOUNDS.get(name)
        if sound is not None:
            sound.play()


# --- Animation helpers ---
def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


def ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def board_to_pixel_center(pos):
    row, col = pos
    cx = MARGIN + col * (CELL + GAP) + CELL // 2
    cy = MARGIN + row * (CELL + GAP) + CELL // 2
    return float(cx), float(cy)


def get_board_coords(px, py):
    x, y = px - MARGIN, py - MARGIN
    col = x // (CELL + GAP)
    row = y // (CELL + GAP)
    in_gap_x = (x % (CELL + GAP)) > CELL
    in_gap_y = (y % (CELL + GAP)) > CELL
    return int(row), int(col), in_gap_x, in_gap_y


def is_inside_board(px, py):
    return MARGIN <= px < MARGIN + BOARD_SIZE and MARGIN <= py < MARGIN + BOARD_SIZE


def get_hover_preview(game, mouse_pos, winner, action_mode):
    if winner or action_mode != "wall" or not is_inside_board(*mouse_pos):
        return None

    r, c, gx, gy = get_board_coords(*mouse_pos)
    if gx and gy:
        return None

    if gx and not gy:
        valid, _, final_r, final_c = game.validate_wall_placement(r, c, 'V')
        return {'orient': 'V', 'r': final_r, 'c': final_c, 'valid': valid}

    if not gx and gy:
        valid, _, final_r, final_c = game.validate_wall_placement(r, c, 'H')
        return {'orient': 'H', 'r': final_r, 'c': final_c, 'valid': valid}

    return None


def make_button_rect(base_rect, scale):
    w = int(base_rect.width * scale)
    h = int(base_rect.height * scale)
    return pygame.Rect(base_rect.centerx - w // 2, base_rect.centery - h // 2, w, h)


def draw_button(rect, text, mouse_pos, pulse_time=0.0, enabled=True, active=False):
    hovered = enabled and rect.collidepoint(mouse_pos)
    scale = 1.05 if hovered or active else 1.0
    if hovered:
        scale += 0.02 * math.sin(pulse_time * 7.5)
    elif active:
        scale += 0.01 * math.sin(pulse_time * 6.0)
    draw_rect = make_button_rect(rect, scale)

    if hovered or active:
        glow_alpha = 60 if hovered else 42
        glow = pygame.Surface((draw_rect.width + 18, draw_rect.height + 18), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*BUTTON_GLOW, glow_alpha), glow.get_rect(), border_radius=14)
        screen.blit(glow, (draw_rect.x - 9, draw_rect.y - 9))

    if enabled:
        if active:
            color = BUTTON_HOVER
            text_color = (255, 255, 255)
            border = BUTTON_GLOW
        else:
            color = BUTTON_HOVER if hovered else BUTTON_COLOR
            text_color = BUTTON_TEXT
            border = PANEL_BORDER
    else:
        color = tuple(max(10, c - 20) for c in BUTTON_COLOR)
        text_color = (165, 165, 165)
        border = (95, 95, 95)

    pygame.draw.rect(screen, color, draw_rect, border_radius=10)
    pygame.draw.rect(screen, border, draw_rect, 2, border_radius=10)
    txt = SMALL_FONT.render(text, True, text_color)
    screen.blit(txt, txt.get_rect(center=draw_rect.center))
    return draw_rect


def get_wall_rect(r, c, orient):
    if orient == 'H':
        return pygame.Rect(
            MARGIN + c * (CELL + GAP),
            MARGIN + r * (CELL + GAP) + CELL,
            CELL * 2 + GAP,
            GAP
        )
    return pygame.Rect(
        MARGIN + c * (CELL + GAP) + CELL,
        MARGIN + r * (CELL + GAP),
        GAP,
        CELL * 2 + GAP
    )
def reset_game():
    game = QuoridorLogic()
    return game, None, "Game reset", MESSAGE_INFO


def set_status(message, color, now):
    return {
        'message': message,
        'color': color,
        'time': now,
    }


def current_status_alpha(status_state, now):
    age = now - status_state['time']
    fade_in = min(1.0, age / 0.18)
    if age < 2.3:
        return fade_in
    fade_out = max(0.25, 1.0 - (age - 2.3) / 1.0)
    return min(fade_in, fade_out)


def sync_pawn_visuals(game):
    return [board_to_pixel_center(p['pos']) for p in game.players]


def begin_pawn_animation(game, pawn_visuals, move_animations, player_idx, start_pos, duration=0.22):
    target = board_to_pixel_center(game.players[player_idx]['pos'])
    pawn_visuals[player_idx] = start_pos
    move_animations[player_idx] = {
        'start': start_pos,
        'target': target,
        'duration': duration,
        'progress': 0.0,
    }


def update_pawn_animations(pawn_visuals, move_animations, dt):
    for i, anim in enumerate(move_animations):
        if not anim:
            continue
        anim['progress'] += dt / anim['duration']
        t = min(1.0, anim['progress'])
        eased = ease_out_cubic(t)
        pawn_visuals[i] = (
            lerp(anim['start'][0], anim['target'][0], eased),
            lerp(anim['start'][1], anim['target'][1], eased),
        )
        if anim['progress'] >= 1.0:
            pawn_visuals[i] = anim['target']
            move_animations[i] = None


def update_wall_animations(wall_animations, dt):
    alive = []
    for anim in wall_animations:
        anim['progress'] += dt / anim['duration']
        if anim['progress'] < 1.0:
            alive.append(anim)
    return alive


def spawn_particles(particles, x, y, count, colors, speed_range=(40, 180), life_range=(0.35, 0.9), size_range=(2, 5), gravity=120, spread=math.tau):
    for i in range(count):
        angle = (spread / max(1, count)) * i + (0.35 * math.sin(i * 13.17))
        speed = lerp(speed_range[0], speed_range[1], 0.5 + 0.5 * math.sin(i * 7.1 + x * 0.01))
        life = lerp(life_range[0], life_range[1], 0.5 + 0.5 * math.cos(i * 5.3 + y * 0.02))
        size = int(round(lerp(size_range[0], size_range[1], 0.5 + 0.5 * math.sin(i * 3.7))))
        color = colors[i % len(colors)]
        particles.append({
            'x': float(x),
            'y': float(y),
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed - speed * 0.18,
            'life': life,
            'max_life': life,
            'size': max(1, size),
            'color': color,
            'gravity': gravity,
        })


def update_particles(particles, dt):
    alive = []
    for p in particles:
        p['life'] -= dt
        if p['life'] <= 0:
            continue
        p['vy'] += p['gravity'] * dt
        p['x'] += p['vx'] * dt
        p['y'] += p['vy'] * dt
        alive.append(p)
    return alive


def draw_particles(particles):
    for p in particles:
        alpha = int(255 * max(0.0, p['life'] / p['max_life']))
        size = max(1, int(p['size'] * (0.65 + 0.35 * p['life'] / p['max_life'])))
        surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*p['color'], alpha), (size * 2, size * 2), size)
        screen.blit(surf, (p['x'] - size * 2, p['y'] - size * 2))


def seed_menu_particles():
    particles = []
    for i in range(28):
        x = 40 + (i * 37) % max(60, WIN_SIZE - 80)
        y = 50 + (i * 71) % max(60, WIN_SIZE + UI_AREA_HEIGHT - 100)
        particles.append({
            'x': float(x),
            'y': float(y),
            'vx': -12 + (i % 5) * 6,
            'vy': -8 - (i % 4) * 4,
            'life': 9999.0,
            'max_life': 9999.0,
            'size': 2 + (i % 3),
            'color': PARTICLE_COLORS[i % len(PARTICLE_COLORS)],
            'gravity': 0,
        })
    return particles


def update_menu_particles(particles, dt):
    for i, p in enumerate(particles):
        p['x'] += p['vx'] * dt
        p['y'] += (14 + (i % 3) * 6) * dt
        p['x'] += math.sin(p['y'] * 0.03 + i) * 10 * dt
        if p['y'] > WIN_SIZE + UI_AREA_HEIGHT + 10:
            p['y'] = -10
            p['x'] = 30 + ((i * 83) % max(60, WIN_SIZE - 60))
            p['color'] = PARTICLE_COLORS[i % len(PARTICLE_COLORS)]
