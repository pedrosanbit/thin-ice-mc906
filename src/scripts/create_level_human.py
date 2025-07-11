# src/script/create_level.py

from src.level_generator import LevelCreatorHuman


def main():
    print("[*] Inicializando editor de fases Thin Ice...")
    print("[*] Controles:")
    print("    ↑ ↓ ← → : Mover o jogador")
    print("    1 - Colocar saco de moedas")
    print("    2 - Colocar chave")
    print("    3 - Colocar tranca (somente após chave)")
    print("    4 - Colocar par de teletransporte")
    print(" ENTER - Finalizar e salvar fase")
    print(" ESC   - Cancelar e sair")

    editor = LevelCreatorHuman()
    editor.run()

if __name__ == "__main__":
    main()
