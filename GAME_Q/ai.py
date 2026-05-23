"""AI player logic: legal action generation, evaluation, and minimax search."""

from collections import deque

from logic import QuoridorLogic
import random


AI_PLAYER = 1   # Blue

AI_LEVELS = {
    "easy": {
        "depth": 1,
        "random_chance": 0.45,
        "include_walls": False
    },
    "medium": {
        "depth": 2,
        "random_chance": 0.15,
        "include_walls": True
    },
    "hard": {
        "depth": 3,
        "random_chance": 0.0,
        "include_walls": True
    }
}

AI_DEPTH = AI_LEVELS["medium"]["depth"]

def clone_game(game):
    new_game = QuoridorLogic()
    new_game.players = [
        {
            'pos': game.players[0]['pos'],
            'walls': game.players[0]['walls'],
            'goal': game.players[0]['goal']
        },
        {
            'pos': game.players[1]['pos'],
            'walls': game.players[1]['walls'],
            'goal': game.players[1]['goal']
        }
    ]
    new_game.turn = game.turn
    new_game.h_walls = set(game.h_walls)
    new_game.v_walls = set(game.v_walls)
    return new_game


def get_winner(game):
    if game.players[0]['pos'][0] == game.players[0]['goal']:
        return 0
    if game.players[1]['pos'][0] == game.players[1]['goal']:
        return 1
    return None


def shortest_path_length(game, player_idx):
    start = game.players[player_idx]['pos']
    goal_row = game.players[player_idx]['goal']

    q = deque([(start, 0)])
    visited = {start}

    while q:
        (r, c), dist = q.popleft()

        if r == goal_row:
            return dist

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 9 and 0 <= nc < 9 and (nr, nc) not in visited:
                if not game.is_wall_blocking((r, c), (nr, nc)):
                    visited.add((nr, nc))
                    q.append(((nr, nc), dist + 1))

    return 9999


def validate_wall_placement_strict(game, r, c, orient):
    if game.players[game.turn]['walls'] <= 0:
        return False

    if game.is_collision(r, c, orient):
        return False

    target_set = game.h_walls if orient == 'H' else game.v_walls
    target_set.add((r, c))

    ok = game.has_path(0) and game.has_path(1)

    target_set.remove((r, c))
    return ok

def get_candidate_wall_actions(game):
    candidates = set()

    # search near both players to reduce branching
    important_positions = [
        game.players[0]['pos'],
        game.players[1]['pos']
    ]

    for pr, pc in important_positions:
        for r in range(max(0, pr - 2), min(7, pr + 2) + 1):
            for c in range(max(0, pc - 2), min(7, pc + 2) + 1):
                candidates.add((r, c, 'H'))
                candidates.add((r, c, 'V'))

    valid_actions = []
    for r, c, orient in candidates:
        if validate_wall_placement_strict(game, r, c, orient):
            valid_actions.append(("wall", (r, c, orient)))

    return valid_actions


def get_all_legal_actions(game, include_walls=True):
    actions = [("move", pos) for pos in game.get_valid_pawn_moves()]

    if include_walls and game.players[game.turn]['walls'] > 0:
        actions.extend(get_candidate_wall_actions(game))

    return actions


def apply_action(game, action):
    kind, payload = action

    if kind == "move":
        result, _ = game.move_pawn(payload)
        return result in (True, "WIN")

    if kind == "wall":
        r, c, orient = payload
        success, _, _ = game.place_wall(r, c, orient)
        return success

    return False


def evaluate(game, ai_player):
    winner = get_winner(game)
    if winner is not None:
        return 100000 if winner == ai_player else -100000

    opp = 1 - ai_player

    my_dist = shortest_path_length(game, ai_player)
    opp_dist = shortest_path_length(game, opp)

    my_walls = game.players[ai_player]['walls']
    opp_walls = game.players[opp]['walls']

    score = 0
    score += (opp_dist - my_dist) * 25
    score += (my_walls - opp_walls) * 2

    # small bonus if it's currently AI's turn
    if game.turn == ai_player:
        score += 1

    return score


def order_actions(game, actions, ai_player):
    scored = []

    for action in actions:
        child = clone_game(game)
        ok = apply_action(child, action)
        if ok:
            scored.append((evaluate(child, ai_player), action))

    reverse = (game.turn == ai_player)
    scored.sort(key=lambda x: x[0], reverse=reverse)

    return [action for _, action in scored]


def minimax(game, depth, alpha, beta, ai_player , include_walls=True):
    winner = get_winner(game)
    if depth == 0 or winner is not None:
        return evaluate(game, ai_player), None

    actions = get_all_legal_actions(game, include_walls = include_walls)
    actions = order_actions(game, actions, ai_player)

    if not actions:
        return evaluate(game, ai_player), None

    maximizing = (game.turn == ai_player)

    if maximizing:
        best_score = float("-inf")
        best_action = None

        for action in actions:
            child = clone_game(game)
            ok = apply_action(child, action)
            if not ok:
                continue

            score, _ = minimax(child, depth - 1, alpha, beta, ai_player, include_walls)

            if score > best_score:
                best_score = score
                best_action = action

            alpha = max(alpha, best_score)
            if beta <= alpha:
                break

        return best_score, best_action

    else:
        best_score = float("inf")
        best_action = None

        for action in actions:
            child = clone_game(game)
            ok = apply_action(child, action)
            if not ok:
                continue

            score, _ = minimax(child, depth - 1, alpha, beta, ai_player, include_walls)

            if score < best_score:
                best_score = score
                best_action = action

            beta = min(beta, best_score)
            if beta <= alpha:
                break

        return best_score, best_action


def choose_ai_action(game, ai_player=AI_PLAYER, difficulty="medium"):
    settings = AI_LEVELS.get(difficulty, AI_LEVELS["medium"])

    depth = settings["depth"]
    random_chance = settings["random_chance"]
    include_walls = settings["include_walls"]

    actions = get_all_legal_actions(game, include_walls=include_walls)

    if not actions:
        return None

    # Easy / Medium mistake chance
    if random.random() < random_chance:
        return random.choice(actions)

    _, action = minimax(
        clone_game(game),
        depth=depth,
        alpha=float("-inf"),
        beta=float("inf"),
        ai_player=ai_player,
        include_walls=include_walls
    )

    return action
