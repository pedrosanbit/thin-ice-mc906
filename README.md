O projeto *Thin Ice* é um jogo de raciocínio em que o jogador percorre um grid 2D buscando chegar ao ponto final da fase, interagindo com blocos, chaves, sacos de moedas, e tiles de gelo com diferentes comportamentos. Sua principal aplicação atual é como ambiente para treinamento de agentes de aprendizado por reforço, especialmente DQN (Deep Q-Network).

---

## 🎮 Estrutura do Projeto

O projeto está organizado em módulos principais:

* **`src/game.py`**: lógica do jogo — define a movimentação do jogador, transições de tiles (gelo derretendo, teleporte etc.), manipulação de blocos e coleta de itens.
* **`src/levels.py`**: responsável pela leitura, construção e escrita dos níveis em formato `.txt`.
* **`src/env/thin_ice_env.py`**: ambiente Gym compatível com RL, contendo as regras de transição de estados, recompensas e terminação.
* **`src/agents/dqn_agent.py`**: implementação do agente DQN, com redes neurais convolucionais, epsilon-greedy, replay buffer e Double DQN.
* **`src/scripts/train.py`**: script que treina um agente DQN por 2000 episódios, avalia desempenho e gera gráficos.
* **`src/main.py`**: versão jogável interativa usando `pygame` para renderização e controle via teclado.
* **`src/utils.py`**: utilitários de interface visual, como renderização da HUD e do grid.

---

## ✅ Execução dos Componentes

### Treinamento de agente DQN:

```bash
python3 -m src.scripts.train
```

* Gera 1000 fases proceduralmente (`build_random_levels`)
* Treina um agente DQN com observações do grid (em one-hot 15x19xC) por 2000 episódios
* Salva gráficos:

  * `success_moving_average.png`: taxa de sucesso
  * `tile_ratio_per_episode.png`: tiles coletados por fase

### Jogo interativo com teclado:

```bash
python3 -m src.main
```

* Abre janela do jogo (Pygame)
* Movimentos com as setas
* Permite observar o comportamento das fases manualmente

---

## 📦 Dependências Recomendadas (via `requirements.txt`)

Essas bibliotecas são necessárias para executar e treinar o jogo corretamente:

```txt
gymnasium>=0.28
numpy>=1.23
torch>=1.12
stable-baselines3[extra]~=2.6.0
sb3-contrib>=1.7
matplotlib>=3.5
pygame~=2.6.1
pillow~=11.2.1
```

Instalação sugerida com:

```bash
pip install -r requirements.txt
```

---

## 📘 Ementa Resumida

Segundo o manual oficial:

* Cada fase é um desafio único e **completável** com **um caminho ideal garantido**.
* Blocos de gelo derretem, podem se tornar intransitáveis.
* Existem **blocos empurráveis**, **trancas**, **chaves**, **moedas** e **teletransportes** que mudam dinamicamente o mapa.
* O jogador só falha se ficar sem movimentos possíveis, e **não pode reiniciar manualmente**.
* Pontuação considera gelo derretido e itens coletados.
* O objetivo é alcançar o **único ponto final** da fase.
