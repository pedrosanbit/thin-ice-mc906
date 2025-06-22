# src/level_generator/actions.py
MOVE_UP = 0
MOVE_DOWN = 1
MOVE_LEFT = 2
MOVE_RIGHT = 3
PLACE_COIN = 4
PLACE_KEY = 5
PLACE_LOCK = 6
PLACE_TELEPORT = 7
PLACE_FINISH = 8
DISCARD = 9

DIRS = [(0, -1),  # 0: cima
        (1,  0),  # 1: direita
        (0,  1),  # 2: baixo
        (-1, 0)]  # 3: esquerda