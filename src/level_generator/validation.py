### src/level_generator/validation.py

from src.mapping import *

def is_tile_occupied(creator, x, y):
    return (x, y) in creator.coin_bags + creator.keys + creator.locks + creator.teleports

def _is_valid_tile_general(creator, x, y, exclude_start=False):
    if exclude_start and (x, y) == creator.original_start:
        return False
    tile = creator.grid[y][x]
    if tile != creator.Map.THIN_ICE.value:
        return False
    if is_tile_occupied(creator, x, y):
        return False
    return True

def is_valid_tile(creator, exclude_start=False):
    return _is_valid_tile_general(creator, creator.player_x, creator.player_y, exclude_start)

def is_valid_tile_at(creator, x, y):
    return _is_valid_tile_general(creator, x, y, exclude_start=(x, y) == creator.original_start)

def is_valid_finish_tile(creator):
    if (creator.player_x, creator.player_y) == creator.original_start:
        return False
    if creator.grid[creator.player_y][creator.player_x] != creator.Map.THIN_ICE.value:
        return False
    if is_tile_occupied(creator, creator.player_x, creator.player_y):
        return False
    return True

def can_save_level(creator):
    if (creator.player_x, creator.player_y) == creator.original_start:
        return False
    if creator.grid[creator.player_y][creator.player_x] not in (creator.Map.THIN_ICE.value, creator.Map.FINISH.value):
        return False
    if is_tile_occupied(creator, creator.player_x, creator.player_y):
        return False
    return True

def add_exit_point(creator):
    from src.level_generator.validation import is_valid_finish_tile
    from src.level_generator.save import save_level
    if not is_valid_finish_tile(creator):
        print("[!] Tile inválido para ponto final.")
        return False

    if creator.key_placed and not creator.lock_placed:
        print("[!] Há uma chave no mapa, mas nenhuma tranca foi colocada.")
        return False

    creator.grid[creator.player_y][creator.player_x] = creator.Map.FINISH.value
    print("[✓] Ponto final definido.")
    save_level(creator)
    return True

def add_coin(creator):
    if not creator.coin_placed and is_valid_tile(creator):
        creator.coin_bags.append((creator.player_x, creator.player_y))
        creator.coin_placed = True

def add_key(creator):
    if not creator.key_placed and is_valid_tile(creator):
        creator.keys.append((creator.player_x, creator.player_y))
        creator.key_placed = True
        print("[i] Chave colocada.")

def add_lock(creator):
    from src.level_generator.save import _mark_forbidden_area

    if not creator.key_placed or creator.lock_placed:
        return
    if not is_valid_tile(creator, exclude_start=True):
        return
    if (creator.player_x, creator.player_y) in creator.keys:
        return
    tile = creator.grid[creator.player_y][creator.player_x]
    if tile != creator.Map.THIN_ICE.value:
        return

    wall_count = sum([
        creator.grid[creator.player_y + dy][creator.player_x + dx] == creator.Map.WALL.value
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
        if 0 <= creator.player_x + dx < GRID_WIDTH and 0 <= creator.player_y + dy < GRID_HEIGHT
    ])
    if wall_count != 3:
        return
    if (creator.player_x, creator.player_y) in creator.coin_bags + creator.teleports + creator.keys:
        return

    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = creator.player_x + dx, creator.player_y + dy
        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
            if creator.grid[ny][nx] != creator.Map.WALL.value:
                creator.grid[ny][nx] = creator.Map.THIN_ICE.value

    creator.grid[creator.player_y][creator.player_x] = creator.Map.LOCK.value
    creator.lock_placed = True
    _mark_forbidden_area(creator)
    print("[i] Tranca colocada.")
