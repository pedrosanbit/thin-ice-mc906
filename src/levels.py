# /src/levels.py

from src.mapping import Map, char_to_level_map, level_map_to_char
import random
import copy
import os

from typing import List, Tuple


class Level:
    def __init__(
        self,
        level_folder: str,  # Pasta dos níveis (nome do diretório)
        loop_on_finish: bool = False,  # Se o jogo deve reiniciar a fase após a conclusão
        current_level_id: int = 0,  # ID do nível atual
    ):
        self.level_folder = level_folder
        self.loop_on_finish = loop_on_finish
        self.current_level_id = current_level_id

        self.max_level_id: int = self.compute_max_level_id()

        self.grid: List[List[int]] = []
        self.start: Tuple[int, int] = (0, 0)
        self.coin_bags: List[Tuple[int, int]] = []
        self.keys: List[Tuple[int, int]] = []
        self.blocks: List[Tuple[int, int]] = []
        self.teleports: List[Tuple[int, int]] = []

        self.load_level()

        #self.total_tiles: int = self.compute_total_tiles()
        #self.total_points: int = self.compute_total_points() 


    def compute_max_level_id(self) -> int:
        """Infere o número máximo de níveis dentro da pasta de níveis, considerando a indexação 0."""
        output_dir, _ = get_level_path(self.level_folder, self.current_level_id)
        level_files = [
            f for f in os.listdir(output_dir)  # Alterei de 'output_dir' para 'os.listdir(output_dir)'
            if f.endswith(".txt") and f.startswith("level_")
        ]

        if not level_files:
            print("Aviso: Não há arquivos de níveis na pasta.")
            return 0


        # O número de arquivos - 1, considerando que a indexação é de 0
        return len(level_files) - 1 if level_files else 0

    def compute_total_tiles(self) -> int:
        """Calcula o total de tiles de gelo no nível (gelo fino e grosso)."""
        return sum(
            1 for row in self.grid for val in row if val == Map.THIN_ICE.value
        ) + 2 * sum(
            1 for row in self.grid for val in row if val == Map.THICK_ICE.value
        )

    def compute_total_points(self) -> int:
        """Calcula a pontuação total, considerando gelo fino, grosso, sacos de moedas e outros itens."""
        thin = sum(
            1 for row in self.grid for val in row
            if val == Map.THIN_ICE.value
        )
        thick = sum(
            1 for row in self.grid for val in row
            if val == Map.THICK_ICE.value
        )
        bags = len(self.coin_bags)
        return thin + 2 * thick + 100 * bags

    def load_level(self) -> None:
        """Carrega o nível atual do conjunto."""
        _, level_path = get_level_path(self.level_folder, self.current_level_id)
        self.grid, self.start, self.coin_bags, self.keys, self.blocks, self.teleports = get_level(self.level_folder, self.current_level_id)

        self.total_tiles: int = self.compute_total_tiles()
        self.total_points: int = self.compute_total_points()
        

    def load_next_level(self) -> None:
        print(f"[DEBUG] Avançando para o nível {self.current_level_id} de {self.max_level_id}")



        """Avança para o próximo nível."""

        if self.current_level_id < self.max_level_id:
            self.current_level_id += 1
        else:
            print(f"DEBUG {self.current_level_id} >= {self.max_level_id}")
            if self.loop_on_finish:
                self.current_level_id = 0  # Volta ao primeiro nível se o loop for ativado
            else:
                self.current_level_id = self.max_level_id
        print(f"[DEBUG] Avançando para o nível {self.current_level_id} de {self.max_level_id}")
        self.load_level()
        print(f"[DEBUG] Avançando para o nível {self.current_level_id} de {self.max_level_id}")

    def reload_level(self) -> None:
        """Recarrega o nível atual."""
        print(f"[DEBUG-RELOAD A] Avançando para o nível {self.current_level_id} de {self.max_level_id}")
        self.load_level()
        print(f"[DEBUG-RELOAD B] Avançando para o nível {self.current_level_id} de {self.max_level_id}")


    def change_folder(self, new_folder: str) -> None:
        """Troca o conjunto de níveis, voltando para o nível 0 da nova pasta."""
        self.level_folder = new_folder
        self.current_level_id = 0
        self.max_level_id = self.compute_max_level_id()  # Atualiza o max_level_id com a nova pasta
        self.load_level()


def get_level_path(folder: str, index: int) -> Tuple[str, str]:
    """Retorna o caminho do diretório e do arquivo do nível."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    output_dir = os.path.join(repo_root, "data", "levels", folder)  # Ensure this is a string, not a list
    os.makedirs(output_dir, exist_ok=True)  # Create directory if not exists
    path = os.path.join(output_dir, f"level_{index:04}.txt")
    return output_dir, path

#def encode_levels_to_txt(level, folder, index):
def encode_levels_to_txt(folder, index, grid, start, coin_bags, keys, blocks, teleports, total_tiles):
    _, output_path = get_level_path(folder, index)
        
    

    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"START:{start[0]},{start[1]}\n")
            f.write(f"TOTAL_TILES:{total_tiles}\n")
            f.write(f"COIN_BAGS:{';'.join(f'{x},{y}' for x, y in coin_bags)}\n")
            f.write(f"KEYS:{';'.join(f'{x},{y}' for x, y in keys)}\n")
            f.write(f"BLOCKS:{';'.join(f'{x},{y}' for x, y in blocks)}\n")
            f.write(f"TELEPORTS:{';'.join(f'{x},{y}' for x, y in teleports)}\n") 

            for i, row in enumerate(grid):
                line = ""
                for j, val in enumerate(row):
                    coord = (j, i)
                    if coord == start:
                        line += 'A'
                    elif coord in coin_bags:
                        line += '8'
                    elif coord in keys:
                        # Inferir tipo original se quiser, ou usar 'B' genérico
                        if val == Map.THIN_ICE.value:
                            line += 'B'
                        elif val == Map.THICK_ICE.value:
                            line += 'C'
                        elif val == Map.TILE.value:
                            line += 'D'
                        else:
                            line += level_map_to_char.get(Map(val), '0')
                    elif coord in blocks:
                        line += '6'
                    else:
                        line += level_map_to_char.get(Map(val), '0')
                f.write(line + "\n")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar nível {index}: {e}")

def get_level(folder, index):
    _, input_path = get_level_path(folder, index)
    
    with open(input_path, "r", encoding="utf-8") as f:
        start = (0, 0)
        total_tiles = 0
        coin_bags, keys, blocks, teleports = [], [], [], []

        while True:
            line = f.readline()
            if not line or not line.strip():
                break
            if line.startswith("START:"):
                x, y = map(int, line.strip().split(":")[1].split(","))
                start = (x, y)
            elif line.startswith("TOTAL_TILES:"):
                total_tiles = int(line.strip().split(":")[1]) - 1
            elif line.startswith("COIN_BAGS:"):
                items = line.strip().split(":")[1]
                coin_bags = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
            elif line.startswith("KEYS:"):
                items = line.strip().split(":")[1]
                keys = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
            elif line.startswith("BLOCKS:"):
                items = line.strip().split(":")[1]
                blocks = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
            elif line.startswith("TELEPORTS:"):
                items = line.strip().split(":")[1]
                teleports = [tuple(map(int, item.split(","))) for item in items.split(";") if item]
            else:
                break

        grid_lines = [line.strip() for line in [line] + f.readlines()]
        grid = []
        for i, line in enumerate(grid_lines):
            row = []
            for j, char in enumerate(line):
                map_enum = char_to_level_map.get(char, Map.EMPTY)
                row.append(map_enum.value)
            grid.append(row)

        #return Level(grid, start, coin_bags, keys, blocks, teleports, total_tiles)
        return grid, start, coin_bags, keys, blocks, teleports
    
