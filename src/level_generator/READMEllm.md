# 🧩 Módulo de Geração de Fases – *Thin Ice*

Este módulo implementa um editor de fases interativo para o jogo *Thin Ice*, permitindo a criação manual de níveis compatíveis com a lógica e mecânicas do jogo.

## 📦 Estrutura dos Arquivos

| Arquivo                        | Função                                                                                                     |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| `level_generator.py`           | Classe `LevelCreator`, responsável por iniciar a tela, receber ações do usuário e aplicar efeitos no grid. |
| `drawing.py`                   | Funções de renderização com Pygame, incluindo `draw_level` e `close_display`.                              |
| `movement.py`                  | Define o movimento do jogador e o sistema de ações via `apply_action`.                                     |
| `objects.py` / `validation.py` | Contêm regras para adicionar objetos (moedas, chave, tranca, teleporte) e validar tiles.                   |
| `teleport.py`                  | Lida com o posicionamento do par de teleporte (entrada e saída).                                           |
| `save.py`                      | Define a lógica de salvamento da fase, respeitando as condições de completabilidade.                       |
| `actions.py`                   | Define constantes inteiras que representam as ações disponíveis.                                           |

---

## 🕹️ Controles (Editor Manual)

Durante a execução do editor (`LevelCreator().run()`), o usuário pode usar as teclas:

| Tecla   | Ação                                                                   |
| ------- | ---------------------------------------------------------------------- |
| ↑ ↓ ← → | Mover o jogador no grid                                                |
| 1       | Colocar **saco de moedas** (uma vez)                                   |
| 2       | Colocar **chave** (uma vez)                                            |
| 3       | Colocar **tranca** (uma vez, requer chave colocada antes)              |
| 4       | Iniciar **teleporte** (coloca entrada e escolhe saída automaticamente) |
| Enter   | Colocar **ponto final da fase** e salvar                               |
| Esc     | Descartar fase atual e fechar                                          |

---

## 🧠 Lógica de Construção

### Regras para Inserção de Objetos

* **Chave** deve ser colocada antes da **tranca**.
* A **tranca** só pode ser colocada em um tile rodeado por exatamente 3 paredes.
* Um **par de teletransporte** é permitido por fase, e a saída é escolhida aleatoriamente entre paredes válidas.
* O **ponto final** só pode ser colocado se não for o tile de início, e não pode haver chave sem tranca.

### Validação Interna

Ao tentar salvar uma fase (`PLACE_FINISH`), o sistema garante:

* Completabilidade mínima: o jogador pode chegar ao ponto final.
* Apenas um ponto final por fase.
* Nenhum item sobreposto no mesmo tile.

---

## 💾 Salvamento

As fases são salvas em:

```
data/levels/custom_created/level_XXXX.txt
```

O salvamento é automático após o posicionamento do ponto final válido (`Enter`), usando a função `encode_levels_to_txt`.

---

## 🧪 Exemplo de Uso

```python
from src.level_generator.level_generator import LevelCreator

editor = LevelCreator()
editor.run()
```

---

## 🔧 Possíveis Extensões Futuras

* Suporte a múltiplos sacos de moedas
* Rotação ou pré-visualização de fases
* Integração com o pipeline de RL para treinar com fases customizadas

---

## 📚 Referência de Elementos

Os elementos do grid seguem a descrição da ementa do jogo:

* `Map.WALL` – Parede (intransitável)
* `Map.THIN_ICE` – Derrete ao pisar
* `Map.THICK_ICE` – Vira gelo fino ao pisar
* `Map.TELEPORT` – Teleporte (uso único)
* `Map.COIN_BAG`, `Map.LOCK`, `Map.FINISH` – Objetos interativos
