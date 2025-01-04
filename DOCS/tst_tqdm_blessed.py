import os
from tst_tqdm import tqdm
from tst_blessed import Terminal

term = Terminal()

# Define a posição
os.system('cls' if os.name == 'nt' else 'clear')
with term.location(x=50, y=50):  # Linha 5, coluna 0
    for _ in tqdm(range(100)):
        pass
