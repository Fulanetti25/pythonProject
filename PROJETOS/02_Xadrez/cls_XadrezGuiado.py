import pygame
import os

# Iniciar o Pygame
pygame.init()

# Definir tamanho da janela
LARGURA = 800
ALTURA = 800
TAMANHO_CAIXA = LARGURA // 8  # Dividido por 8 para o tamanho das casas
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Tabuleiro de Xadrez')

# Cores
COR_BAIXO = (255, 255, 255)
COR_CIMA = (125, 135, 150)

# Função para desenhar o tabuleiro
def desenhar_tabuleiro():
    for linha in range(8):
        for coluna in range(8):
            cor = COR_BAIXO if (linha + coluna) % 2 == 0 else COR_CIMA
            pygame.draw.rect(screen, cor, (coluna * TAMANHO_CAIXA, linha * TAMANHO_CAIXA, TAMANHO_CAIXA, TAMANHO_CAIXA))

# Função para carregar as imagens das peças
def carregar_imagens():
    peças = ['rei', 'rainha', 'bispo', 'cavalo', 'torre', 'peao']
    imagens = {}
    for peça in peças:
        for cor in ['branca', 'preta']:
            caminho = os.path.join('imagens', f'{cor}_{peça}.png')  # Supondo que as imagens estejam na pasta 'imagens'
            imagens[f'{cor}_{peça}'] = pygame.image.load(caminho)
    return imagens

# Função para desenhar as peças no tabuleiro
def desenhar_pecas(imagens):
    # Exemplo de como colocar as peças (ajuste conforme necessário)
    screen.blit(imagens['branca_torre'], (0, 0))  # Torre branca na posição (0,0)
    screen.blit(imagens['preta_torre'], (TAMANHO_CAIXA * 7, TAMANHO_CAIXA * 7))  # Torre preta na posição (7,7)
    # Coloque outras peças de maneira similar

# Carregar as imagens das peças
imagens = carregar_imagens()

# Loop principal
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False

    screen.fill((0, 0, 0))  # Limpar a tela
    desenhar_tabuleiro()  # Desenhar o tabuleiro
    desenhar_pecas(imagens)  # Desenhar as peças
    pygame.display.update()  # Atualizar a tela

pygame.quit()
