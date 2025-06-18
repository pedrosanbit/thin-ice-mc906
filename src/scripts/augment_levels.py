import os
import shutil
import numpy as np
from src.levels import get_level, encode_levels_to_txt

ORIGINAL_FOLDER = "original_game"
AUGMENTED_FOLDER = "original_game_augmented"

def rotate_position(pos, angle, height, width):
    x, y = pos
    if angle == 180:
        return (width - 1 - x, height - 1 - y)
    return pos

def rotate_grid(grid, angle):
    np_grid = np.array(grid)
    if angle == 180:
        return np.rot90(np_grid, k=2).tolist()
    return grid

def rotate_all_elements(elements, angle, height, width):
    return [rotate_position(p, angle, height, width) for p in elements]

def main():
    output_dir = os.path.join("data", "levels", AUGMENTED_FOLDER)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    level_idx = 0
    original_dir = os.path.join("data", "levels", ORIGINAL_FOLDER)
    num_levels = len([f for f in os.listdir(original_dir) if f.startswith("level_") and f.endswith(".txt")])

    for i in range(num_levels):
        grid, start, coin_bags, keys, blocks, teleports = get_level(ORIGINAL_FOLDER, i)
        h, w = len(grid), len(grid[0])
        total_tiles = sum(1 for row in grid for val in row if val != 0)

        # Rotaciona apenas 180 graus
        angle = 180
        rotated_grid = rotate_grid(grid, angle)
        rotated_start = rotate_position(start, angle, h, w)
        rotated_coin_bags = rotate_all_elements(coin_bags, angle, h, w)
        rotated_keys = rotate_all_elements(keys, angle, h, w)
        rotated_blocks = rotate_all_elements(blocks, angle, h, w)
        rotated_teleports = rotate_all_elements(teleports, angle, h, w)

        encode_levels_to_txt(
            folder=AUGMENTED_FOLDER,
            index=level_idx,
            grid=rotated_grid,
            start=rotated_start,
            coin_bags=rotated_coin_bags,
            keys=rotated_keys,
            blocks=rotated_blocks,
            teleports=rotated_teleports,
            total_tiles=total_tiles,
        )
        level_idx += 1

if __name__ == "__main__":
    main()
