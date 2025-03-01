import numpy as np
from PIL import Image
from blessed import Terminal

term = Terminal()

# Abrir e redimensionar a imagem
img = Image.open(r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\FILES\PlanilhaSobMedida.jpg")
img = img.resize((80, 40))  # Ajuste o tamanho
img = img.convert("RGB")

# Converter para numpy array
pixels = np.array(img, dtype=int)  # Converter para tipo int

# Exibir a imagem no terminal com blocos coloridos
print(term.clear)
for row in pixels:
    for r, g, b in row:
        print(term.on_rgb(int(r), int(g), int(b)) + "  ", end="")  # Converter valores para int
    print(term.normal)  # Reset de cor no final da linha