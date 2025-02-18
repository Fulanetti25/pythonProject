from PIL import Image
from blessed import Terminal

# Abrir a imagem antes de passar para a função
img = Image.open(r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\FILES\PlanilhaSobMedida.jpg")

term = Terminal()

# Função para converter imagem em ASCII
def imagem_para_ascii(img, largura=100):  # img já é um objeto Image

    # Redimensionar proporcionalmente
    proporcao = img.height / img.width
    altura = int(largura * proporcao * 0.55)  # Ajuste para terminal
    img = img.resize((largura, altura))

    # Converter para tons de cinza
    img = img.convert("L")

    # Mapa de caracteres ASCII
    chars = " .:-=+*%@#"
    escala = len(chars) / 256

    # Montar o ASCII
    ascii_art = ""
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            ascii_art += chars[int(pixel * escala)]
        ascii_art += "\n"

    return ascii_art

# Exibir no terminal
print(term.clear)
ascii_art = imagem_para_ascii(img, largura=100)
print(ascii_art)
