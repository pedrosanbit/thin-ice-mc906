# src/level_generation/movement.py

from src.mapping import *

from src.level_generator.objects import *
from src.level_generator.teleport import *
from src.level_generator.validation import *
from src.level_generator.save import *
from src.level_generator.actions import *
from src.level_generator.drawing import *

def apply_action(creator, action):
    if action == MOVE_UP:
        try_move(creator, 0, -1)
    elif action == MOVE_DOWN:
        try_move(creator, 0, 1)
    elif action == MOVE_LEFT:
        try_move(creator, -1, 0)
    elif action == MOVE_RIGHT:
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


def try_move(creator, dx, dy) -> bool:
    nx, ny = creator.player_x + dx, creator.player_y + dy

    if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
        return False
    if (nx, ny) == creator.original_start or (nx, ny) in creator.forbidden_area:
        return False

    current_val = creator.grid[ny][nx]

    if current_val == creator.Map.WALL.value:
        creator.grid[ny][nx] = creator.Map.THIN_ICE.value
    elif current_val == creator.Map.THIN_ICE.value:
        creator.grid[ny][nx] = creator.Map.THICK_ICE.value
    elif current_val in (
            creator.Map.THICK_ICE.value, creator.Map.TELEPORT.value,
            creator.Map.COIN_BAG.value, creator.Map.LOCK.value):
        return False

    creator.player_x, creator.player_y = nx, ny
    return True
