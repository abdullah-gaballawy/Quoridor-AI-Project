"""Core Quoridor rules, movement, wall validation, undo/redo, and save/load."""

import collections
import copy
import json
import os


class QuoridorLogic:
    def __init__(self):
        self.players = [
            {'pos': (8, 4), 'walls': 10, 'goal': 0},
            {'pos': (0, 4), 'walls': 10, 'goal': 8}
        ]
        self.turn = 0
        self.h_walls = set()
        self.v_walls = set()
        
        # New State Tracking
        self.history = []
        self.redo_stack = []
        self.save_state()

    def save_state(self):
        state = {
            'players': copy.deepcopy(self.players),
            'turn': self.turn,
            'h_walls': set(self.h_walls),
            'v_walls': set(self.v_walls)
        }
        self.history.append(state)
        self.redo_stack.clear()

    def undo(self):
        if len(self.history) > 1:
            self.redo_stack.append(self.history.pop())
            state = self.history[-1]
            self.players = copy.deepcopy(state['players'])
            self.turn = state['turn']
            self.h_walls = set(state['h_walls'])
            self.v_walls = set(state['v_walls'])
            return True
        return False

    def redo(self):
        if self.redo_stack:
            state = self.redo_stack.pop()
            self.players = copy.deepcopy(state['players'])
            self.turn = state['turn']
            self.h_walls = set(state['h_walls'])
            self.v_walls = set(state['v_walls'])
            self.history.append(state)
            return True
        return False

    def get_valid_pawn_moves(self):
        r, c = self.players[self.turn]['pos']
        opp_r, opp_c = self.players[1 - self.turn]['pos']
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9 and not self.is_wall_blocking((r, c), (nr, nc)):
                if (nr, nc) == (opp_r, opp_c):
                    jr, jc = nr + dr, nc + dc
                    jump_blocked_by_edge = not (0 <= jr < 9 and 0 <= jc < 9)
                    jump_blocked_by_wall = False
                    if not jump_blocked_by_edge:
                        jump_blocked_by_wall = self.is_wall_blocking((nr, nc), (jr, jc))

                    if not jump_blocked_by_edge and not jump_blocked_by_wall:
                        moves.append((jr, jc))
                    else:
                        diag_side_steps = [(0, -1), (0, 1)] if dr != 0 else [(-1, 0), (1, 0)]
                        for dsr, dsc in diag_side_steps:
                            dr_final, dc_final = nr + dsr, nc + dsc
                            if 0 <= dr_final < 9 and 0 <= dc_final < 9:
                                if not self.is_wall_blocking((nr, nc), (dr_final, dc_final)):
                                    moves.append((dr_final, dc_final))
                else:
                    moves.append((nr, nc))
        return moves

    def is_wall_blocking(self, start, end):
        r1, c1 = start
        r2, c2 = end
        if r1 == r2:
            col = min(c1, c2)
            return (r1, col) in self.v_walls or (r1 - 1, col) in self.v_walls
        row = min(r1, r2)
        return (row, c1) in self.h_walls or (row, c1 - 1) in self.h_walls

    def has_path(self, p_idx):
        start, goal = self.players[p_idx]['pos'], self.players[p_idx]['goal']
        queue, visited = collections.deque([start]), {start}
        while queue:
            r, c = queue.popleft()
            if r == goal:
                return True
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 9 and 0 <= nc < 9 and (nr, nc) not in visited:
                    if not self.is_wall_blocking((r, c), (nr, nc)):
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return False

    def is_collision(self, r, c, orient):
        if r < 0 or r > 7 or c < 0 or c > 7:
            return True

        if orient == 'H':
            for wr, wc in self.h_walls:
                if wr == r and abs(wc - c) <= 1:
                    return True
            if (r, c) in self.v_walls:
                return True
        else:
            for wr, wc in self.v_walls:
                if wc == c and abs(wr - r) <= 1:
                    return True
            if (r, c) in self.h_walls:
                return True
        return False

    def validate_wall_placement(self, r, c, orient):
        if self.players[self.turn]['walls'] <= 0:
            return False, "No walls left", r, c

        final_r, final_c = r, c
        if self.is_collision(r, c, orient):
            found = False
            for s in [-1, 1, -2, 2]:
                tr = r + s if orient == 'V' else r
                tc = c + s if orient == 'H' else c
                if not self.is_collision(tr, tc, orient):
                    final_r, final_c, found = tr, tc, True
                    break
            if not found:
                return False, "Illegal wall", r, c

        target_set = self.h_walls if orient == 'H' else self.v_walls
        target_set.add((final_r, final_c))

        if self.has_path(0) and self.has_path(1):
            target_set.remove((final_r, final_c))
            return True, "Wall placement valid", final_r, final_c

        target_set.remove((final_r, final_c))
        return False, "Path blocked", final_r, final_c

    def place_wall(self, r, c, orient):
        is_valid, reason, final_r, final_c = self.validate_wall_placement(r, c, orient)
        if not is_valid:
            return False, reason, None

        target_set = self.h_walls if orient == 'H' else self.v_walls
        target_set.add((final_r, final_c))
        self.players[self.turn]['walls'] -= 1
        self.turn = 1 - self.turn
        self.save_state() # <--- ADDED THIS
        return True, "Wall placed", {'orient': orient, 'r': final_r, 'c': final_c}

    def move_pawn(self, pos):
        if pos in self.get_valid_pawn_moves():
            mover = self.turn
            self.players[self.turn]['pos'] = pos
            if pos[0] == self.players[self.turn]['goal']:
                self.save_state() # <--- ADDED THIS
                return "WIN", mover
            self.turn = 1 - self.turn
            self.save_state() # <--- ADDED THIS
            return True, mover
        return False, None

    # Inside your QuoridorLogic class:
    def save_to_disk(self, filename="savegame.json"):
        # We use the last state in our history
        state = self.history[-1]
    
        # We have to convert 'sets' to 'lists' because JSON doesn't support sets
        serializable_state = {
            'players': state['players'],
            'turn': state['turn'],
            'h_walls': list(state['h_walls']),
            'v_walls': list(state['v_walls'])
        }
    
        with open(filename, 'w') as f:
            json.dump(serializable_state, f)
        return "Game Saved!"

    def load_from_disk(self, filename="savegame.json"):
        if not os.path.exists(filename):
            return False, "No save file found"

        with open(filename, 'r') as f:
            data = json.load(f)

        # Fix: convert pos back to tuple for each player
        for player in data['players']:
            player['pos'] = tuple(player['pos'])  # ← this line

        self.players = data['players']
        self.turn = data['turn']
        self.h_walls = set(tuple(w) for w in data['h_walls'])
        self.v_walls = set(tuple(w) for w in data['v_walls'])

        self.history = []
        self.redo_stack = []
        self.save_state()
        return True, "Game Loaded!"
