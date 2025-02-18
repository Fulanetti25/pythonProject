from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console()

# Carregar a imagem
img = Image.open(r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\FILES\PlanilhaSobMedida.jpg")

# Exibir imagem no terminal (funciona melhor com terminal que suporta gráficos)
console.print(Panel(Text.from_markup("[bold cyan]Imagem:[/bold cyan]")))
console.print(img)
