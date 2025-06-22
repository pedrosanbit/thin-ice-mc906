# src/level_generation/movement.py

from src.mapping import *

from src.level_generator.objects import *
from src.level_generator.teleport import *
from src.level_generator.validation import *
from src.level_generator.save import *
from src.level_generator.actions import *
from src.level_generator.drawing import *


def _delta_from_relative(creator, rel):
    """
    Converte a tecla relativa para (dx, dy) absoluto
    rel =  0 → frente   (UP)
    rel = -1 → esquerda (LEFT)
    rel =  1 → direita  (RIGHT)
    rel =  2 → trás     (DOWN)
    """
    new_idx = (creator.dir_idx + rel) % 4
    return DIRS[new_idx], new_idx

def apply_action(creator, action):
    if action in (MOVE_UP, MOVE_LEFT, MOVE_RIGHT, MOVE_DOWN):
        rel = {MOVE_UP: 0, MOVE_LEFT: -1, MOVE_RIGHT: 1, MOVE_DOWN: 2}[action]
        (dx, dy), new_idx = _delta_from_relative(creator, rel)
        moved = try_move(creator, dx, dy)
        if moved:
            creator.dir_idx = new_idx
        try_move(creator, 1, 0)
    elif action == PLACE_COIN:
        add_coin(creator)
    elif action == PLACE_KEY:
        add_key(creator)
    elif action == PLACE_LOCK:
        add_lock(creator)
    elif action == PLACE_TELEPORT:
        add_teleport(creator)
    elif action == PLACE_FINISH:
        if not add_exit_point(creator):
            print("[i] Cancelando fase automaticamente.")
            close_display()
            return False
    elif action == DISCARD:
        print("[i] Fase descartada pelo usuário.")
        close_display()
        return False
    return True


def try_move(creator, dx, dy):
    nx, ny = creator.player_x + dx, creator.player_y + dy
    # verificação de limites, paredes, etc.
    if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT): 
        return False
    if (nx, ny) == creator.original_start or (nx, ny) in creator.forbidden_area:
        return False

    current_val = creator.grid[ny][nx]
    if current_val == creator.Map.WALL.value:
        creator.grid[ny][nx] = creator.Map.THIN_ICE.value
    elif current_val == creator.Map.THIN_ICE.value:
        creator.grid[ny][nx] = creator.Map.THICK_ICE.value
    elif current_val in (creator.Map.THICK_ICE.value, 
                         creator.Map.TELEPORT.value,
                         creator.Map.COIN_BAG.value, 
                         creator.Map.LOCK.value):
        return False

    # movimento realizado
    creator.player_x, creator.player_y = nx, ny
    return True
