"""Rendering layer: menu, board, pawns, walls, buttons, status bar, and winner overlay."""

import math
import os
import pygame

import ui_ux as ui


def draw_wall_preview(preview, anim_time):
    if not preview:
        return

    rect = ui.get_wall_rect(preview['r'], preview['c'], preview['orient'])
    pulse = 0.85 + 0.15 * (0.5 + 0.5 * math.sin(anim_time * 8.0))
    color = ui.VALID_PREVIEW_COLOR if preview['valid'] else ui.INVALID_PREVIEW_COLOR
    alpha = max(60, min(240, int(color[3] * pulse)))

    preview_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    preview_surface.fill((color[0], color[1], color[2], alpha))
    ui.screen.blit(preview_surface, rect.topleft)
    pygame.draw.rect(ui.screen, (240, 240, 240), rect, 1)


def draw_status_bar(game, winner, status_message, status_color, mouse_pos, pulse_time, status_alpha, selected_mode, action_mode):
    pygame.draw.line(ui.screen, (100, 100, 100), (0, ui.WIN_SIZE), (ui.WIN_SIZE, ui.WIN_SIZE), 2)

    turn_name = "RED (Goal Top)" if game.turn == 0 else "BLUE (Goal Bottom)"
    turn_color = (255, 100, 100) if game.turn == 0 else (100, 150, 255)
    if winner:
        turn_name = f"WINNER: {winner}"
        turn_color = ui.MESSAGE_SUCCESS

    txt_turn = ui.FONT.render(f"TURN: {turn_name}", True, turn_color)
    action_label = "Move" if action_mode == 'move' else "Wall"
    txt_walls = ui.SMALL_FONT.render(
        f"Walls - R: {game.players[0]['walls']} | B: {game.players[1]['walls']} ",
        True,
        (208, 208, 208)
    )
    txt_action = ui.SMALL_FONT.render(f"Action: {action_label}  (M / W)", True, (220, 220, 220))

    status_surface = ui.SMALL_FONT.render(status_message, True, status_color)
    status_surface.set_alpha(max(60, min(255, int(status_alpha * 255))))

    ui.screen.blit(txt_turn, (ui.MARGIN, ui.WIN_SIZE + 8))
    ui.screen.blit(txt_walls, (ui.MARGIN, ui.WIN_SIZE + 36))
    ui.screen.blit(txt_action, (ui.MARGIN, ui.WIN_SIZE + 62))
    ui.screen.blit(status_surface, (ui.MARGIN, ui.WIN_SIZE + 88))

    new_game_rect = ui.draw_button(ui.NEW_GAME_BTN, "New Game", mouse_pos, pulse_time)
    menu_rect = ui.draw_button(ui.MENU_BTN, "Main Menu", mouse_pos, pulse_time)
    move_rect = ui.draw_button(ui.ACTION_MOVE_BTN, "Move (M)", mouse_pos, pulse_time, active=action_mode == 'move')
    wall_rect = ui.draw_button(ui.ACTION_WALL_BTN, "Wall (W)", mouse_pos, pulse_time, active=action_mode == 'wall')

    # Render new buttons
    undo_rect = ui.draw_button(ui.UNDO_BTN, "Undo", mouse_pos, pulse_time, enabled=len(game.history) > 1 and not winner)
    redo_rect = ui.draw_button(ui.REDO_BTN, "Redo", mouse_pos, pulse_time, enabled=len(game.redo_stack) > 0 and not winner)
    # In your draw_status_bar function:
    save_rect = ui.draw_button(ui.SAVE_BTN, "Save", mouse_pos, pulse_time, enabled=not winner)
   
    return new_game_rect, menu_rect, move_rect, wall_rect, undo_rect, redo_rect, save_rect


def draw_winner_overlay(mouse_pos, winner, overlay_progress, pulse_time):
    alpha = int(190 * overlay_progress)
    overlay = pygame.Surface((ui.WIN_SIZE, ui.WIN_SIZE), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    ui.screen.blit(overlay, (0, 0))

    slide = int((1 - ui.ease_out_cubic(overlay_progress)) * 36)
    panel = pygame.Rect(ui.WIN_SIZE // 2 - 170, ui.WIN_SIZE // 2 - 125 + slide, 340, 250)
    pygame.draw.rect(ui.screen, ui.PANEL_COLOR, panel, border_radius=16)
    pygame.draw.rect(ui.screen, ui.PANEL_BORDER, panel, 2, border_radius=16)

    glow = pygame.Surface((panel.width + 30, panel.height + 30), pygame.SRCALPHA)
    pygame.draw.rect(glow, (255, 255, 255, int(35 * overlay_progress)), glow.get_rect(), border_radius=26)
    ui.screen.blit(glow, (panel.x - 15, panel.y - 15))

    for i in range(10):
        ray_angle = pulse_time * 0.6 + i * (math.tau / 10)
        ray_len = 95 + 18 * math.sin(pulse_time * 2.0 + i)
        x1 = panel.centerx + math.cos(ray_angle) * 28
        y1 = panel.centery + math.sin(ray_angle) * 28
        x2 = panel.centerx + math.cos(ray_angle) * ray_len
        y2 = panel.centery + math.sin(ray_angle) * ray_len
        pygame.draw.line(ui.screen, (255, 245, 200, int(38 * overlay_progress)), (x1, y1), (x2, y2), 2)

    title = ui.TITLE_FONT.render("Game Over", True, ui.TEXT_COLOR)
    winner_txt = ui.FONT.render(f"{winner} wins!", True, ui.MESSAGE_SUCCESS)
    ui.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 42)))
    ui.screen.blit(winner_txt, winner_txt.get_rect(center=(panel.centerx, panel.y + 80)))

    restart_btn = pygame.Rect(panel.x + 50, panel.y + 116, 240, 38)
    menu_btn = pygame.Rect(panel.x + 50, panel.y + 164, 240, 38)
    quit_btn = pygame.Rect(panel.x + 50, panel.y + 212, 240, 38)

    restart_rect = ui.draw_button(restart_btn, "Restart", mouse_pos, pulse_time)
    menu_rect = ui.draw_button(menu_btn, "Back to Start", mouse_pos, pulse_time)
    quit_rect = ui.draw_button(quit_btn, "Quit", mouse_pos, pulse_time)

    return restart_rect, menu_rect, quit_rect


def draw_mode_card(rect, mode_item, mouse_pos, selected, pulse_time):
    hovered = rect.collidepoint(mouse_pos)
    fill = ui.MENU_CARD_HOVER if hovered else ui.MENU_CARD_COLOR
    border = ui.PANEL_BORDER if selected else (120, 130, 150)
    if not mode_item['available']:
        fill = tuple(max(12, c - 10) for c in fill)
        border = (95, 95, 105)

    pygame.draw.rect(ui.screen, fill, rect, border_radius=14)
    pygame.draw.rect(ui.screen, border, rect, 2 if selected else 1, border_radius=14)

    if selected:
        glow = pygame.Surface((rect.width + 14, rect.height + 14), pygame.SRCALPHA)
        pygame.draw.rect(glow, (*ui.BUTTON_GLOW, 45), glow.get_rect(), border_radius=18)
        ui.screen.blit(glow, (rect.x - 7, rect.y - 7))

    badge_color = ui.MESSAGE_SUCCESS if mode_item['available'] else ui.MESSAGE_ERROR
    badge = ui.SMALL_FONT.render(mode_item['subtitle'], True, badge_color)
    title = ui.CARD_TITLE_FONT.render(mode_item['name'], True, ui.TEXT_COLOR if mode_item['available'] else (180, 180, 180))
    ui.screen.blit(title, (rect.x + 16, rect.y + 18))
    ui.screen.blit(badge, (rect.x + 16, rect.y + 58))

    helper = "Playable now" if mode_item['available'] else "Locked until AI is added"
    helper_txt = ui.SMALL_FONT.render(helper, True, (200, 200, 200) if mode_item['available'] else (150, 150, 150))
    ui.screen.blit(helper_txt, (rect.x + 16, rect.y + 92))
    return rect


def draw_theme_chip(rect, name, mouse_pos, selected):
    hovered = rect.collidepoint(mouse_pos)
    palette = ui.THEMES[name]
    fill = palette['menu_card_hover'] if hovered or selected else palette['menu_card']
    pygame.draw.rect(ui.screen, fill, rect, border_radius=12)
    pygame.draw.rect(ui.screen, palette['theme_chip_border'] if selected else (135, 135, 150), rect, 2 if selected else 1, border_radius=12)

    swatches = [palette['wall'], palette['move_hint'], palette['button_hover']]
    for i, color in enumerate(swatches):
        pygame.draw.circle(ui.screen, color, (rect.x + 20 + i * 18, rect.centery), 6)
    label = ui.CARD_LABEL_FONT.render(name, True, ui.TEXT_COLOR)
    ui.screen.blit(label, (rect.x + 54, rect.centery - 8))
    return rect


def draw_ai_level_chip(rect, level_item, mouse_pos, selected):
    hovered = rect.collidepoint(mouse_pos)

    fill = ui.MENU_CARD_HOVER if hovered or selected else ui.MENU_CARD_COLOR
    border = ui.PANEL_BORDER if selected else (135, 135, 150)

    pygame.draw.rect(ui.screen, fill, rect, border_radius=12)
    pygame.draw.rect(ui.screen, border, rect, 2 if selected else 1, border_radius=12)

    title = ui.CARD_LABEL_FONT.render(level_item["name"], True, ui.TEXT_COLOR)
    subtitle = ui.SMALL_FONT.render(level_item["subtitle"], True, (200, 200, 200))

    ui.screen.blit(title, (rect.x + 14, rect.y + 8))
    ui.screen.blit(subtitle, (rect.x + 14, rect.y + 25))

    return rect


def draw_menu(mouse_pos, pulse_time, menu_particles, selected_mode, selected_ai_level, menu_status, menu_color, status_alpha):
    ui.screen.fill(ui.BG_COLOR)
    ui.draw_particles(menu_particles)

    center = (ui.WIN_SIZE // 2, ui.WIN_SIZE // 2 - 50)
    for i, radius in enumerate([125, 188, 252]):
        ring_surface = pygame.Surface((ui.WIN_SIZE, ui.WIN_SIZE + ui.UI_AREA_HEIGHT), pygame.SRCALPHA)
        ring_alpha = 18 + int(14 * (0.5 + 0.5 * math.sin(pulse_time * 1.4 + i)))
        pygame.draw.circle(ring_surface, (*ui.MENU_RING_COLOR, ring_alpha), center, radius, 2)
        ui.screen.blit(ring_surface, (0, 0))

    title_y = 78 + int(4 * math.sin(pulse_time * 2.8))
    title = ui.BIG_FONT.render("Quoridor", True, ui.TEXT_COLOR)
    subtitle = ui.SMALL_FONT.render(
        "Cinematic UI, live wall preview, restart flow, sound FX, and theme selection",
        True,
        (220, 220, 220)
    )
    ui.screen.blit(title, title.get_rect(center=(ui.WIN_SIZE // 2, title_y)))
    ui.screen.blit(subtitle, subtitle.get_rect(center=(ui.WIN_SIZE // 2, 126)))

    section_1 = ui.CARD_LABEL_FONT.render("Choose Mode", True, (230, 230, 230))
    section_2 = ui.CARD_LABEL_FONT.render("Choose Theme", True, (230, 230, 230))
    ui.screen.blit(section_1, (58, 160))
    ui.screen.blit(section_2, (58, 355))

    mode_rects = {}
    mode_y = 188
    mode_w = 160
    gap = 14
    start_x = 58
    for idx, item in enumerate(ui.MODE_OPTIONS):
        rect = pygame.Rect(start_x + idx * (mode_w + gap), mode_y, mode_w, 128)
        mode_rects[item['key']] = draw_mode_card(rect, item, mouse_pos, selected_mode == item['key'], pulse_time)

    theme_rects = {}
    theme_names = list(ui.THEMES.keys())
    for idx, name in enumerate(theme_names):
        rect = pygame.Rect(58 + idx * 165, 380, 150, 46)
        theme_rects[name] = draw_theme_chip(rect, name, mouse_pos, ui.ACTIVE_THEME == name)

    # AI difficulty is shown ONLY for Human vs AI mode.
    ai_level_rects = {}
    show_ai_levels = selected_mode == "hvai"
    if show_ai_levels:
        section_3 = ui.CARD_LABEL_FONT.render("AI Difficulty", True, (230, 230, 230))
        ui.screen.blit(section_3, (58, 432))

        for idx, item in enumerate(ui.AI_LEVEL_OPTIONS):
            rect = pygame.Rect(58 + idx * 165, 455, 150, 46)
            ai_level_rects[item["key"]] = draw_ai_level_chip(
                rect,
                item,
                mouse_pos,
                selected_ai_level == item["key"]
            )

    # Move the buttons down only when AI difficulty is visible.
    if show_ai_levels:
        start_y, quit_y, load_y = 510, 562, 614
        info_y, status_y = 666, 728
    else:
        start_y, quit_y, load_y = 440, 495, 550
        info_y, status_y = 602, 696

    start_btn = pygame.Rect(ui.WIN_SIZE // 2 - 120, start_y, 240, 46)
    quit_btn = pygame.Rect(ui.WIN_SIZE // 2 - 120, quit_y, 240, 46)
    load_btn = pygame.Rect(ui.WIN_SIZE // 2 - 120, load_y, 240, 46)
    sound_btn = pygame.Rect(ui.WIN_SIZE - 182, 34, 124, 34)

    start_rect = ui.draw_button(
        start_btn,
        "Start Game",
        mouse_pos,
        pulse_time,
        enabled=(selected_mode in ['hvh', 'hvai'])
    )

    quit_rect = ui.draw_button(quit_btn, "Quit", mouse_pos, pulse_time)

    has_save = os.path.exists("savegame.json")
    load_rect = ui.draw_button(
        load_btn,
        "Load Game",
        mouse_pos,
        pulse_time,
        enabled=has_save
    )

    sound_text = "Sound: On" if ui.SOUND_ENABLED and ui.AUDIO_READY else ("Sound: Off" if ui.AUDIO_READY else "Sound: N/A")
    sound_rect = ui.draw_button(sound_btn, sound_text, mouse_pos, pulse_time, enabled=ui.AUDIO_READY)

    info_lines = [
        "• Click squares to move your pawn.",
        "• Hover a gap to preview a wall. Green means legal, red means invalid.",
        "• Human vs AI is ready now. AI vs AI is still locked.",
    ]

    for i, line in enumerate(info_lines):
        txt = ui.SMALL_FONT.render(line, True, (220, 220, 220))
        ui.screen.blit(txt, (58, info_y + i * 19))

    status_surface = ui.SMALL_FONT.render(menu_status, True, menu_color)
    status_surface.set_alpha(max(70, min(255, int(status_alpha * 255))))
    ui.screen.blit(status_surface, (58, status_y))

    return start_rect, quit_rect, sound_rect, mode_rects, theme_rects, load_rect, ai_level_rects

def draw_board_background(anim_time):
    board_rect = pygame.Rect(ui.MARGIN - 6, ui.MARGIN - 6, ui.BOARD_SIZE + 12, ui.BOARD_SIZE + 12)
    pygame.draw.rect(ui.screen, (28, 32, 40), board_rect, border_radius=18)
    pygame.draw.rect(ui.screen, ui.PANEL_BORDER, board_rect, 2, border_radius=18)

    top_goal = pygame.Surface((ui.BOARD_SIZE, ui.CELL // 2), pygame.SRCALPHA)
    top_goal.fill((*ui.GOAL_TOP_COLOR, 90))
    ui.screen.blit(top_goal, (ui.MARGIN, ui.MARGIN - ui.CELL // 4))

    bottom_goal = pygame.Surface((ui.BOARD_SIZE, ui.CELL // 2), pygame.SRCALPHA)
    bottom_goal.fill((*ui.GOAL_BOTTOM_COLOR, 90))
    ui.screen.blit(bottom_goal, (ui.MARGIN, ui.MARGIN + ui.BOARD_SIZE - ui.CELL // 4))

    shimmer = pygame.Surface((ui.BOARD_SIZE, ui.BOARD_SIZE), pygame.SRCALPHA)
    line_alpha = 10 + int(8 * (0.5 + 0.5 * math.sin(anim_time * 2.0)))
    pygame.draw.rect(shimmer, (255, 255, 255, line_alpha), shimmer.get_rect(), 1, border_radius=16)
    ui.screen.blit(shimmer, (ui.MARGIN, ui.MARGIN))

def draw_walls(game, wall_animations):
    for r, c in game.h_walls:
        pygame.draw.rect(ui.screen, ui.WALL_COLOR, ui.get_wall_rect(r, c, 'H'), border_radius=4)
    for r, c in game.v_walls:
        pygame.draw.rect(ui.screen, ui.WALL_COLOR, ui.get_wall_rect(r, c, 'V'), border_radius=4)

    for anim in wall_animations:
        rect = ui.get_wall_rect(anim['r'], anim['c'], anim['orient'])
        progress = ui.ease_out_back(min(1.0, anim['progress']))
        alpha = int(120 * max(0.0, 1.0 - anim['progress']))

        if anim['orient'] == 'H':
            width = max(4, int(rect.width * min(progress, 1.0)))
            glow_rect = pygame.Rect(rect.centerx - width // 2, rect.y, width, rect.height)
        else:
            height = max(4, int(rect.height * min(progress, 1.0)))
            glow_rect = pygame.Rect(rect.x, rect.centery - height // 2, rect.width, height)

        glow = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        glow.fill((*ui.WALL_GLOW_COLOR, alpha))
        ui.screen.blit(glow, glow_rect.topleft)


def draw_pawns(game, pawn_visuals, move_animations, pulse_time, winner=None):
    for i, p in enumerate(game.players):
        x, y = pawn_visuals[i]
        radius = ui.CELL // 3
        extra = 0
        moving = move_animations[i] and move_animations[i]['progress'] < 1.0
        if moving:
            progress = move_animations[i]['progress']
            extra = int(5 * math.sin(progress * math.pi))
            glow_radius = radius + 18 + int(8 * math.sin(progress * math.pi))
            glow = pygame.Surface((glow_radius * 2 + 12, glow_radius * 2 + 12), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*ui.P_COLORS[i], 42), (glow_radius + 6, glow_radius + 6), glow_radius)
            ui.screen.blit(glow, (int(x - glow_radius - 6), int(y - glow_radius - 6)))

        if game.turn == i and not winner:
            ring_radius = radius + 12 + int(2 * math.sin(pulse_time * 5.0))
            ring = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(ring, (*ui.P_COLORS[i], 70), (ring_radius + 5, ring_radius + 5), ring_radius, 3)
            ui.screen.blit(ring, (int(x - ring_radius - 5), int(y - ring_radius - 5)))

        shadow_radius = radius + 6 + extra
        shadow = pygame.Surface((shadow_radius * 2 + 8, shadow_radius * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(shadow, (0, 0, 0, 70), (shadow_radius + 4, shadow_radius + 4), shadow_radius)
        ui.screen.blit(shadow, (int(x - shadow_radius - 4), int(y - shadow_radius - 1 + 6)))
        pygame.draw.circle(ui.screen, ui.P_COLORS[i], (int(x), int(y - extra)), radius + extra)
        pygame.draw.circle(ui.screen, (255, 255, 255), (int(x - radius // 3), int(y - extra - radius // 3)), max(3, radius // 5))


def draw(game, winner=None, status_message="", status_color=ui.MESSAGE_INFO, preview=None,
         pawn_visuals=None, move_animations=None, wall_animations=None, particles=None,
         pulse_time=0.0, status_alpha=1.0, selected_mode='hvh', action_mode='move'):
    ui.screen.fill(ui.BG_COLOR)
    draw_board_background(pulse_time)

    mouse_pos = pygame.mouse.get_pos()
    hovered_square = None
    if ui.is_inside_board(*mouse_pos):
        r, c, gx, gy = ui.get_board_coords(*mouse_pos)
        if not gx and not gy and 0 <= r < 9 and 0 <= c < 9:
            hovered_square = (r, c)

    valid_moves = game.get_valid_pawn_moves() if not winner and action_mode == "move" else []

    for r in range(9):
        for c in range(9):
            color = ui.BOARD_COLOR
            if (r, c) == hovered_square:
                color = ui.BOARD_HOVER_COLOR
            if (r, c) in valid_moves:
                pulse = 0.78 + 0.22 * (0.5 + 0.5 * math.sin(pulse_time * 6.0 + r + c))
                color = (
                    int(ui.MOVE_HINT_COLOR[0] * pulse),
                    int(ui.MOVE_HINT_COLOR[1] * pulse),
                    int(ui.MOVE_HINT_COLOR[2] * pulse),
                )
            rect = pygame.Rect(ui.MARGIN + c * (ui.CELL + ui.GAP), ui.MARGIN + r * (ui.CELL + ui.GAP), ui.CELL, ui.CELL)
            pygame.draw.rect(ui.screen, color, rect, border_radius=9)

    if particles:
        ui.draw_particles(particles)

    draw_wall_preview(preview, pulse_time)
    draw_walls(game, wall_animations or [])
    draw_pawns(game, pawn_visuals or [ui.board_to_pixel_center(p['pos']) for p in game.players], move_animations or [None, None], pulse_time, winner)

    return draw_status_bar(game, winner, status_message, status_color, pygame.mouse.get_pos(), pulse_time, status_alpha, selected_mode, action_mode)
