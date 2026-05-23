"""Application entry point and event loop. Run this file to start the game."""

import math
import sys
import pygame

from logic import QuoridorLogic
from ai import AI_PLAYER, choose_ai_action
import ui_ux as ui
import gui


def main():
    game = QuoridorLogic()
    winner = None
    scene = "menu"
    selected_mode = "hvh"
    selected_ai_level = "medium"
    action_mode = "move"

    now = pygame.time.get_ticks() / 1000.0
    status_state = ui.set_status("Welcome! Choose a mode and start.", ui.MESSAGE_INFO, now)

    pawn_visuals = ui.sync_pawn_visuals(game)
    move_animations = [None, None]
    wall_animations = []
    particles = []
    menu_particles = ui.seed_menu_particles()
    overlay_progress = 0.0
    win_confetti_timer = 0.0

    while True:
        dt = ui.clock.tick(ui.FPS) / 1000.0
        now = pygame.time.get_ticks() / 1000.0
        mouse_pos = pygame.mouse.get_pos()

        ui.update_pawn_animations(pawn_visuals, move_animations, dt)
        wall_animations = ui.update_wall_animations(wall_animations, dt)
        particles = ui.update_particles(particles, dt)
        ui.update_menu_particles(menu_particles, dt)

        if winner:
            overlay_progress = min(1.0, overlay_progress + dt * 4.5)
            win_confetti_timer += dt
            if win_confetti_timer >= 0.14:
                win_confetti_timer = 0.0
                ui.spawn_particles(
                    particles, ui.WIN_SIZE * 0.5, 90, 10, ui.PARTICLE_COLORS,
                    speed_range=(60, 180), life_range=(0.8, 1.35),
                    size_range=(2, 5), gravity=160, spread=math.pi
                )
        else:
            overlay_progress = 0.0
            win_confetti_timer = 0.0

        preview = ui.get_hover_preview(game, mouse_pos, winner, action_mode) if scene == "game" else None
        restart_btn = menu_back_btn = quit_overlay_btn = None
        action_move_btn = action_wall_btn = None
        menu_controls = None
        undo_btn_rect = redo_btn_rect = None
        new_game_btn_rect = menu_btn_rect = None

        if scene == "menu":
            menu_controls = gui.draw_menu(
                mouse_pos,
                now,
                menu_particles,
                selected_mode,
                selected_ai_level,
                status_state['message'],
                status_state['color'],
                ui.current_status_alpha(status_state, now),
            )
        else:
            new_game_btn_rect, menu_btn_rect, action_move_btn, action_wall_btn, undo_btn_rect, redo_btn_rect, save_btn_rect = gui.draw(
                game,
                winner,
                status_state['message'],
                status_state['color'],
                preview,
                pawn_visuals,
                move_animations,
                wall_animations,
                particles,
                now,
                ui.current_status_alpha(status_state, now),
                selected_mode,
                action_mode,
            )
            if winner:
                restart_btn, menu_back_btn, quit_overlay_btn = gui.draw_winner_overlay(
                    mouse_pos, winner, overlay_progress, now
                )
        if (
                scene == "game"
                and selected_mode == "hvai"
                and not winner
                and game.turn == AI_PLAYER
                and all(anim is None for anim in move_animations)
                and len(wall_animations) == 0
        ):
            action = choose_ai_action(game, ai_player=AI_PLAYER, difficulty=selected_ai_level)

            if action is not None:
                kind, payload = action

                if kind == "move":
                    start_pos = pawn_visuals[AI_PLAYER]
                    result, mover = game.move_pawn(payload)

                    if result == "WIN":
                        ui.begin_pawn_animation(game, pawn_visuals, move_animations, mover, start_pos, duration=0.27)
                        winner = "RED" if mover == 0 else "BLUE"
                        overlay_progress = 0.0
                        action_mode = "move"
                        status_state = ui.set_status(f"{winner} wins!", ui.MESSAGE_SUCCESS, now)
                        px, py = ui.board_to_pixel_center(game.players[mover]['pos'])
                        ui.spawn_particles(particles, px, py, 26, ui.PARTICLE_COLORS,
                                        speed_range=(80, 220), life_range=(0.7, 1.2),
                                        size_range=(2, 6), gravity=180)
                        ui.play_sound("win")

                    elif result is True:
                        ui.begin_pawn_animation(game, pawn_visuals, move_animations, mover, start_pos, duration=0.22)
                        status_state = ui.set_status("AI moved", ui.MESSAGE_SUCCESS, now)
                        px, py = ui.board_to_pixel_center(game.players[mover]['pos'])
                        ui.spawn_particles(particles, px, py, 10,
                                        [ui.P_COLORS[mover], (255, 255, 255)],
                                        speed_range=(35, 120), life_range=(0.25, 0.55),
                                        size_range=(2, 4), gravity=100)
                        ui.play_sound("move")

                elif kind == "wall":
                    r, c, orient = payload
                    success, reason, info = game.place_wall(r, c, orient)

                    status_state = ui.set_status(reason if success else "AI wall failed",
                                              ui.MESSAGE_SUCCESS if success else ui.MESSAGE_ERROR, now)

                    if success and info:
                        wall_animations.append({
                            'orient': orient,
                            'r': info['r'],
                            'c': info['c'],
                            'progress': 0.0,
                            'duration': 0.22
                        })
                        rect = ui.get_wall_rect(info['r'], info['c'], orient)
                        ui.spawn_particles(particles, rect.centerx, rect.centery, 12,
                                        [ui.WALL_GLOW_COLOR, (255, 255, 255)],
                                        speed_range=(30, 110), life_range=(0.28, 0.6),
                                        size_range=(2, 4), gravity=90)
                        ui.play_sound("wall")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and scene == "game" and not winner:
                if event.key == pygame.K_m:
                    action_mode = "move"
                    status_state = ui.set_status("Move Mode: click a square to move your pawn", ui.MESSAGE_INFO, now)
                    ui.play_sound("click")
                    continue
                if event.key == pygame.K_w:
                    if game.players[game.turn]['walls'] <= 0:
                        status_state = ui.set_status("No walls left", ui.MESSAGE_ERROR, now)
                        ui.play_sound("error")
                    else:
                        action_mode = "wall"
                        status_state = ui.set_status("Wall Mode: click a gap to place a wall", ui.MESSAGE_INFO, now)
                        ui.play_sound("click")
                    continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                if scene == "menu":
                    start_btn, menu_quit_btn, sound_btn, mode_rects, theme_rects, load_rect, ai_level_rects = menu_controls

                    if sound_btn and sound_btn.collidepoint(event.pos) and ui.AUDIO_READY:
                        ui.SOUND_ENABLED = not ui.SOUND_ENABLED
                        status_state = ui.set_status("Sound enabled" if ui.SOUND_ENABLED else "Sound disabled", ui.MESSAGE_INFO, now)
                        ui.play_sound("toggle")
                        continue

                    clicked_theme = False
                    for theme_name, rect in theme_rects.items():
                        if rect.collidepoint(event.pos):
                            ui.apply_theme(theme_name)
                            menu_particles = ui.seed_menu_particles()
                            status_state = ui.set_status(f"Theme switched to {theme_name}", ui.MESSAGE_SUCCESS, now)
                            ui.play_sound("theme")
                            clicked_theme = True
                            break
                    if clicked_theme:
                        continue

                    clicked_mode = False
                    for item in ui.MODE_OPTIONS:
                        rect = mode_rects[item['key']]
                        if rect.collidepoint(event.pos):
                            clicked_mode = True
                            if item['available']:
                                selected_mode = item['key']
                                status_state = ui.set_status(f"Mode selected: {item['name']}", ui.MESSAGE_SUCCESS, now)
                                ui.play_sound("click")
                            else:
                                status_state = ui.set_status(f"{item['name']} is coming soon when AI logic is added", ui.MESSAGE_ERROR, now)
                                ui.play_sound("error")
                            break
                    if clicked_mode:
                        continue

                    if selected_mode == "hvai":
                        clicked_ai_level = False
                        for item in ui.AI_LEVEL_OPTIONS:
                            rect = ai_level_rects.get(item["key"])
                            if rect and rect.collidepoint(event.pos):
                                selected_ai_level = item["key"]
                                status_state = ui.set_status(
                                    f"AI difficulty selected: {item['name']}",
                                    ui.MESSAGE_SUCCESS,
                                    now
                                )
                                ui.play_sound("click")
                                clicked_ai_level = True
                                break

                        if clicked_ai_level:
                            continue

                    if load_rect and load_rect.collidepoint(event.pos):
                        success, msg = game.load_from_disk()
                        if success:
                            # Transition to the game scene
                            scene = "game"
                        
                            # Reset all visual states to match the loaded file
                            pawn_visuals = ui.sync_pawn_visuals(game)
                            move_animations = [None, None]
                            wall_animations = []
                            particles = []
                            winner = None
                            action_mode = "move"
                        
                            # Set success status and play sound
                            status_state = ui.set_status(msg, ui.MESSAGE_SUCCESS, now)
                            ui.play_sound("start")
                        else:
                            # If loading failed (no file), show error
                            status_state = ui.set_status(msg, ui.MESSAGE_ERROR, now)
                            ui.play_sound("error")
                        continue

                    if start_btn and start_btn.collidepoint(event.pos):
                        if selected_mode == 'aivai':
                            status_state = ui.set_status("AI vs AI is not ready yet", ui.MESSAGE_ERROR, now)
                            ui.play_sound("error")
                        else:
                            game, winner, _, _ = ui.reset_game()
                            status_state = ui.set_status(f"New {ui.MODE_LABELS[selected_mode]} game started", ui.MESSAGE_INFO,
                                                      now)
                            scene = "game"
                            pawn_visuals = ui.sync_pawn_visuals(game)
                            move_animations = [None, None]
                            wall_animations = []
                            particles = []
                            overlay_progress = 0.0
                            action_mode = "move"
                            ui.play_sound("start")
                    
                    elif menu_quit_btn and menu_quit_btn.collidepoint(event.pos):
                        ui.play_sound("click")
                        pygame.quit()
                        sys.exit()
                    continue
                    
                elif scene == 'game':
                    if action_move_btn and action_move_btn.collidepoint(event.pos) and not winner:
                        action_mode = "move"
                        status_state = ui.set_status("Move Mode: click a square to move your pawn", ui.MESSAGE_INFO, now)
                        ui.play_sound("click")
                        continue
                    if action_wall_btn and action_wall_btn.collidepoint(event.pos) and not winner:
                        if game.players[game.turn]['walls'] <= 0:
                            status_state = ui.set_status("No walls left", ui.MESSAGE_ERROR, now)
                            ui.play_sound("error")
                        else:
                            action_mode = "wall"
                            status_state = ui.set_status("Wall Mode: click a gap to place a wall", ui.MESSAGE_INFO, now)
                            ui.play_sound("click")
                        continue
                
                    if ui.NEW_GAME_BTN.collidepoint(event.pos):
                        game, winner, msg, color = ui.reset_game()
                        status_state = ui.set_status(msg, color, now)
                        pawn_visuals = ui.sync_pawn_visuals(game)
                        move_animations = [None, None]
                        wall_animations = []
                        particles = []
                        overlay_progress = 0.0
                        action_mode = "move"
                        ui.play_sound("start")
                        continue
                    if ui.MENU_BTN.collidepoint(event.pos):
                        scene = "menu"
                        winner = None
                        overlay_progress = 0.0
                        action_mode = "move"
                        status_state = ui.set_status("Returned to main menu", ui.MESSAGE_INFO, now)
                        ui.play_sound("click")
                        continue

                    if winner:
                        if restart_btn and restart_btn.collidepoint(event.pos):
                            game, winner, msg, color = ui.reset_game()
                            status_state = ui.set_status(msg, color, now)
                            pawn_visuals = ui.sync_pawn_visuals(game)
                            move_animations = [None, None]
                            wall_animations = []
                            particles = []
                            overlay_progress = 0.0
                            action_mode = "move"
                            ui.play_sound("start")
                        elif menu_back_btn and menu_back_btn.collidepoint(event.pos):
                            scene = "menu"
                            winner = None
                            overlay_progress = 0.0
                            action_mode = "move"
                            status_state = ui.set_status("Returned to main menu", ui.MESSAGE_INFO, now)
                            ui.play_sound("click")
                        elif quit_overlay_btn and quit_overlay_btn.collidepoint(event.pos):
                            ui.play_sound("click")
                            pygame.quit()
                            sys.exit()
                        continue

                    # --- UNDO CLICK ---
                    if undo_btn_rect and undo_btn_rect.collidepoint(event.pos):
                        if game.undo():
                            # If playing AI, undo twice so it's the human's turn again
                            if selected_mode == "hvai" and game.turn == AI_PLAYER:
                                game.undo()
                            
                            pawn_visuals = ui.sync_pawn_visuals(game)
                            move_animations = [None, None]
                            wall_animations = []
                            winner = None
                            action_mode = "move"
                            status_state = ui.set_status("Undo successful", ui.MESSAGE_SUCCESS, now)
                            ui.play_sound("click")
                        else:
                            status_state = ui.set_status("Nothing to undo", ui.MESSAGE_ERROR, now)
                            ui.play_sound("error")
                        continue

                    # --- REDO CLICK ---
                    if redo_btn_rect and redo_btn_rect.collidepoint(event.pos):
                        if game.redo():
                            # If playing AI, redo twice to skip AI turn
                            if selected_mode == "hvai" and game.turn == AI_PLAYER:
                                game.redo()
                            
                            pawn_visuals = ui.sync_pawn_visuals(game)
                            move_animations = [None, None]
                            wall_animations = []
                            winner = None
                            action_mode = "move"
                            status_state = ui.set_status("Redo successful", ui.MESSAGE_SUCCESS, now)
                            ui.play_sound("click")
                        else:
                            status_state = ui.set_status("Nothing to redo", ui.MESSAGE_ERROR, now)
                            ui.play_sound("error")
                        continue

                    if save_btn_rect.collidepoint(event.pos) and not winner:
                        msg = game.save_to_disk()
                        status_state = ui.set_status(msg, ui.MESSAGE_SUCCESS, now)
                        ui.play_sound("click")
                        continue

                    if not ui.is_inside_board(*event.pos):
                        continue

                r, c, gx, gy = ui.get_board_coords(*event.pos)

                if action_mode == "move":
                    if not gx and not gy:
                        current_player = game.turn
                        start_pos = pawn_visuals[current_player]
                        result, mover = game.move_pawn((r, c))
                        if result == "WIN":
                            ui.begin_pawn_animation(game, pawn_visuals, move_animations, mover, start_pos, duration=0.27)
                            winner = "RED" if mover == 0 else "BLUE"
                            overlay_progress = 0.0
                            action_mode = "move"
                            status_state = ui.set_status(
                                f"{winner} wins! Use Restart, New Game, or Back to Start.",
                                ui.MESSAGE_SUCCESS,
                                now,
                            )
                            px, py = ui.board_to_pixel_center(game.players[mover]['pos'])
                            ui.spawn_particles(particles, px, py, 26, ui.PARTICLE_COLORS, speed_range=(80, 220), life_range=(0.7, 1.2), size_range=(2, 6), gravity=180)
                            ui.play_sound("win")
                        elif result is True:
                            ui.begin_pawn_animation(game, pawn_visuals, move_animations, mover, start_pos, duration=0.22)
                            action_mode = "move"
                            status_state = ui.set_status("Pawn moved", ui.MESSAGE_SUCCESS, now)
                            px, py = ui.board_to_pixel_center(game.players[mover]['pos'])
                            ui.spawn_particles(particles, px, py, 10, [ui.P_COLORS[mover], (255, 255, 255)], speed_range=(35, 120), life_range=(0.25, 0.55), size_range=(2, 4), gravity=100)
                            ui.play_sound("move")
                        else:
                            status_state = ui.set_status("Invalid move", ui.MESSAGE_ERROR, now)
                            ui.play_sound("error")
                    else:
                        status_state = ui.set_status("You are in Move Mode. Press Wall or hit W to place a wall.", ui.MESSAGE_ERROR, now)
                        ui.play_sound("error")

                elif action_mode == "wall":
                    if gx and not gy:
                        success, reason, info = game.place_wall(r, c, 'V')
                        status_state = ui.set_status(reason, ui.MESSAGE_SUCCESS if success else ui.MESSAGE_ERROR, now)
                        if success and info:
                            wall_animations.append({'orient': 'V', 'r': info['r'], 'c': info['c'], 'progress': 0.0, 'duration': 0.22})
                            rect = ui.get_wall_rect(info['r'], info['c'], 'V')
                            ui.spawn_particles(particles, rect.centerx, rect.centery, 12, [ui.WALL_GLOW_COLOR, (255, 255, 255)], speed_range=(30, 110), life_range=(0.28, 0.6), size_range=(2, 4), gravity=90)
                            action_mode = "move"
                            ui.play_sound("wall")
                        else:
                            ui.play_sound("error")

                    elif not gx and gy:
                        success, reason, info = game.place_wall(r, c, 'H')
                        status_state = ui.set_status(reason, ui.MESSAGE_SUCCESS if success else ui.MESSAGE_ERROR, now)
                        if success and info:
                            wall_animations.append({'orient': 'H', 'r': info['r'], 'c': info['c'], 'progress': 0.0, 'duration': 0.22})
                            rect = ui.get_wall_rect(info['r'], info['c'], 'H')
                            ui.spawn_particles(particles, rect.centerx, rect.centery, 12, [ui.WALL_GLOW_COLOR, (255, 255, 255)], speed_range=(30, 110), life_range=(0.28, 0.6), size_range=(2, 4), gravity=90)
                            action_mode = "move"
                            ui.play_sound("wall")
                        else:
                            ui.play_sound("error")

                    else:
                        status_state = ui.set_status("You are in Wall Mode. Click a gap, not a square.", ui.MESSAGE_ERROR, now)
                        ui.play_sound("error")

        pygame.display.flip()


if __name__ == "__main__":
    main()
