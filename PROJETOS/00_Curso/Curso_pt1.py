# Atalho para execução de seleção = Shift + Alt + E

# Curso Python #01 - Seja um Programador
    # Apresentações
# Curso Python #02 - Para que serve o Python?
    # Como utilizar
# Curso Python #03 - Instalando o Python3 e o IDLE
    # Instalação
        import this

# Curso Python #04 - Primeiros comandos em Python3
# Curso Python #05 - Instalando o PyCharm e o QPython3
    # Tipo de operação
        print("Alô Mundo!") #Aspas duplas também podem ser utilizadas para texto
        print(7+4)
        print('7'+'4')

    # Variáveis
        nome = 'Jauber'
        idade = '40'
        peso = '50'
        print(nome,idade,peso)

    # InputBox
        nome = input('Nome? ')
        idade = input('Idade? ')
        peso = input ('Peso? ')
        print(nome,idade,peso)

    # Script salvo no diretório.

    # Exercício 1 / Entrada e Saída
        nome = input('Digite seu nome: ')
        print('Olá Senhor: {}'.format(nome))

    # Exercício 2 / Data separada
        dia = input('Dia? ')
        mes = input('Mês? ')
        ano = input('Ano? ')
        print(ano, '-', mes, '-', dia)
        print(ano + '-' + mes + '-' + dia)
        print('Você nasceu no dia ' + dia + ' do mês ' + mes + ' no ano de ' + ano)

    # Exercício Python #001 - Deixando tudo pronto
             print("Olá, Mundo!")
    # Exercício Python  # 002 - Respondendo ao Usuário
            nome = input('Qual seu nome? ')
            print('Seja bem vindo {}!'.format(nome)) #{} coloca a variável numa máscara

# Python Course # 06 - Primitives Types and Data Output
    # Tipos primitivos de dados
        print(type(int('2')))
        print(type(float('2.5')))
        print(type(bool(''))) # Célula vazia vai ser considerada como False
        print(type(bool(True)))
        print(type(str('Jauber')))

    # Exercício Python #003 - Somando dois números
        #Desafio 3, Soma de dois números
            n1 = int(input('Número 1: '))
            n2 = int(input('Número 2: '))
            soma = n1 + n2
            print('A soma dos números {0} e {1}, é {2}'.format(n1, n2, soma))

    # Exercício Python #004 - Dissecando uma Variável
        # Desafio 4, Todas informações sobre um caractere
            n = input('Digite um caractere: ')
            print('Tipo primitivo: ', type(n))
            print('Espaço: ', n.isspace())
            print('Numérico: ', n.isnumeric())
            print('Alfabético: ', n.isalpha())
            print('Alfanumérico: ', n.isalnum())
            print('Maísculo: ',n.isupper())
            print('Minúsculo: ',n.islower())
            print('Capitalizado: ',n.title())
            print('Exibível: ',n.isprintable())

# Curso Python #07 - Operadores Aritméticos
    numero1 = int(input('Número 1: '))
    numero2 = int(input('Número 2: '))
    soma = numero1 + numero2
    subt = numero1 - numero2
    mult = numero1 * numero2
    divi = numero1 / numero2
    divint = numero1 // numero2
    modu = numero1 % numero2
    expo = numero1 ** numero2
    # Ordem de precedencia: parenteses > exponenciação > multiplicação/divisão/divisãointeira/restodivisão > soma/subtração
        print('Operadores Matemáticos em ordem de precedencia: ')
        print('A exponenciação é: ', expo) #Função pow(n1,n2)
        print('Multiplicação: {}, Divisão: {:.1f}, Div. Inteira: {}, Resto Div.: {}'.format(mult,divi,divint,modu))
        print('Soma: {}, Subtração: {}'.format(soma,subt))

    # Testes de string
        print('Oi!' + 'Olá!')
        print('Oi!'*10)
        print('='*20)
        print('{:20}!'.format('Fula'))
        print('{:>20}!'.format('Fula'))
        print('{:<20}!'.format('Fula'))
        print('{:=^20}!'.format('Fula'))
        print('{:^20}!'.format('Fula'))
        print('{:^20}'.format(10 + 50))
        print('Oi!', end=' ') #end= Retirar quebra de linha
        print('Fim!')
        print('t1: {} \nt2: {:.1f} \nt3: {} \nt4.: {}'.format(1,2,3,4)) #\n = Acrescentar quebra de linha

    # Python Exercise # 005 - Predecessor and Successor
        n = int(input('Digite um número: '))
        print('O número é {}! Antecedido por {}, Sucedido por {}'.format(n,n-1,n+1))  # {} coloca a variável numa máscara

    # Exercício Python #006 - Dobro, Triplo, Raiz Quadrada
        n = int(input('Digite um número: '))
        d = n * 2
        t = n * 3
        #import math OU #from math import sqrt
        r = n ** (1/2)
        #math.sqrt(n) OU #r = sqrt(n)
        print('O número é {}! Dobro é {}, Triplo é {}, Raiz Quadrada é {:.2f}'.format(n, d, t, r))  # {} coloca a variável numa máscara

    # Exercício Python #007 - Média Aritmética
        n1 = float(input('Digite uma nota: '))
        n2 = float(input('Digite outra nota: '))
        m = (n1+n2) / 2
        print('A média é {}!'.format(m))

    # Exercício Python #008 - Conversor de Medidas
        m = int(input('Digite o valor em metros: '))
        cm = m * 100
        mm = m * 1000
        print('Metros: {} \nCentímetros: {}\nMilímetros: {}'.format(m,cm,mm))

    # Exercício Python #009 - Tabuada
        n = int(input('Digite o número: '))
        print('-'*50)
        print('{:2} X  {:2} = {:2}'.format(n, 1, n*1))
        print('{:2} X  {:2} = {:2}'.format(n, 2, n*2))
        print('{:2} X  {:2} = {:2}'.format(n, 3, n*3))
        print('{:2} X  {:2} = {:2}'.format(n, 4, n*4))
        print('{:2} X  {:2} = {:2}'.format(n, 5, n*5))
        print('{:2} X  {:2} = {:2}'.format(n, 6, n*6))
        print('{:2} X  {:2} = {:2}'.format(n, 7, n*7))
        print('{:2} X  {:2} = {:2}'.format(n, 8, n*8))
        print('{:2} X  {:2} = {:2}'.format(n, 9, n*9))
        print('{:2} X  {:2} = {:2}'.format(n, 10 ,n*10))
        print('-'*50)

    # Exercício Python #010 - Conversor de Moedas
        r = float(input('Quantos reais você tem na carteira: '))
        d = r / 3.27
        dh = r / 5.04
        print('Você pode comprar {:.2f} dólares em 2017'.format(d))
        print('Você pode comprar {:.2f} dólares em 2023'.format(dh))

    # Exercício Python #011 - Pintando Parede
        h = float(input('Digite a altura em metros: '))
        l = float(input('Digite a largura em metros: '))
        a = h*l
        t = a/2
        print('Para pintar a parede de {} m², você precisará de {} litros de tinta'.format(a,t))

    # Exercício Python #012 - Calculando Descontos
        v = float(input('Digite o valor do produto: '))
        vd = v - (0.05*v)
        print('O produto de R$ {} , com 5% de desconto fica R$ {:.2f}'.format(v, vd))

    # Exercício Python #013 - Reajuste Salarial
        v = float(input('Digite o valor do salário: '))
        vd = v + (0.15 * v)
        print('O salário de R$ {} , com 15% de aumento fica R$ {:.2f}'.format(v, vd))

    # Exercício Python #014 - Conversor de Temperaturas
        c = float(input('Digite a temperatura em ºC: '))
        f = 9*c/5+32
        print('A temperatura em ºF é: {}'.format(f))

    # Exercício Python #015 - Aluguel de Carros
        d = float(input('Quantos dias: '))
        k = float(input('Quantos km: '))
        va = (d * 60) + (k * 0.15)
        print('O valor do aluguel é: {:.2f}'.format(va))

#Curso Python #08 - Utilizando Módulos
    import math #importar biblioteca
    from math import sqrt, ceil #importar função
    from math import #Ctrl + Espaço mostra todas opções
        ceil #arredondar para cima
        floor #arredondar para baixo
        trunc #truncar
        pow #potencia = **
        sqrt #raiz quadrada
        factorial #fatorial

    # Raiz Quadrada
        from math import sqrt, ceil
        n = int(input('Digite um número: '))
        print('Raiz Quadrada Arredondada é {}'.format(ceil(sqrt(n))))

    # Bibliotecas (Versão verificada no Python Console ou cmd)
        https://docs.python.org/3.10/

    # Random
        import random # import Ctrl + Space > list all
        n = random.randint(1,10)
        print(n)

    # Bibliotecas Externas
        https://pypi.org/
        import emoji
        print(emoji.emojize('Olá mundo :glasses:'))
        print(emoji.emojize('Olá mundo :earth_americas:'))

    # Exercício Python #016 - Quebrando um número
        from math import trunc
        n = float(input('Digite um número: '))
        print('Porção inteira é {}'.format(trunc(n)))

    # Exercício Python #017 - Catetos e Hipotenusa
        from math import hypot
        o = float(input('Cateto Oposto: '))
        a = float(input('Cateto Adjacente: '))
        print('Hipotenusa é {:.2f}'.format(hypot(o,a)))
        #print('Hipotenusa é {:.2f}'.format((o ** 2 + a ** 2) ** (1/2)))

    # Exercício Python #018 - Seno, Cosseno e Tangente
        import math
        a = float(input('Angulo: '))
        x = math.radians(a)
        print('Seno é {:.2f}, Cosseno é {:.2f}, Tangente é {:.2f}'.format(math.sin(x), math.cos(x), math.tan(x)))

    # Exercício Python #019 - Sorteando um item na lista
        from random import choice
        a1 = input('Aluno 1: ')
        a2 = input('Aluno 2: ')
        a3 = input('Aluno 3: ')
        a4 = input('Aluno 4: ')
        lista = [a1,a2,a3,a4]
        n = choice(lista)
        print('Escolhido {}'.format(n))

    # Exercício Python #020 - Sorteando uma ordem na lista
        from random import shuffle
        a1 = str(input('Aluno 1: '))
        a2 = str(input('Aluno 2: '))
        a3 = str(input('Aluno 3: '))
        a4 = str(input('Aluno 4: '))
        lista = [a1, a2, a3, a4]
        random.shuffle(lista)
        print('Escolhido {}'.format(lista))

    # Exercício Python #021 - Tocando um MP3
        import pygame
        pygame.init()
        pygame.mixer.music.load('00 - FILES/teste.mp3')
        pygame.mixer.music.play()
        pygame.event.wait()

# Curso Python #09 - Manipulating Text

    frase = 'Curso em Vídeo Python'
        print(frase)
        print(frase[9])
        print(frase[9:14])
        print(frase[9:21:2]) # pulando de 2 em 2
        print(frase[:5]) # terminando em 5, começando em 0
        print(frase[15:]) # começando em 15, terminando até o final
        print(frase[9::3]) # pulando de 3 em 3
        print(len(frase))
        print(frase.count('o'))
        print(frase.count('o',0,14))
        print(frase.find('deo'))
        print(frase.lfind('deo'))
        print(frase.rfind('deo'))
        print(frase.find('Android')) # -1 para não localizado
        print('Curso' in frase)
        print(frase.upper())
        print(frase.lower())
        print(frase.capitalize())
        print(frase.title())
        print(frase.strip())
        print(frase.rstrip())
        print(frase.lstrip())

        frase = 'Curso em Vídeo Python'
        frase = frase.replace('Python','Android') # Frase são imutáveis, a não ser que ocorra atribuição
        print(frase)

        frase = 'Curso em Vídeo Python'
        frase = frase.split()
        print(frase[0],frase[3])

        frase = 'Curso em Vídeo Python'
        frase = '-'.join(frase)
        print(frase)

        print("""
        1
        
        tudo, foda-ce. vai escrever tudo que tá na lista
        
        2
        """)

    # Exercício Python #022 - Analisador de Textos
        n = str(input('Digite seu nome: ')).strip()
        print(n.upper())
        print(n.lower())
        print('Letras: {}'.format(len(n)-n.count(' ')))
        print('{} tem {} letras'.format(n[0:n.find(' ')].capitalize(), n.find(' ')))
        separa = n.split()
        print(separa[0])

    # Exercício Python #023 - Separando dígitos de um número
        num = int(input('Digite um número: '))
        n = str(num)
        print('Unidade: {}'.format(n[3]))
        print('Dezena: {}'.format(n[2]))
        print('Centena: {}'.format(n[1]))
        print('Milhar: {}'.format(n[0]))

        num = int(input('Digite um número: '))
        u = num // 1 % 10
        d = num // 10 % 10
        c = num // 100 % 10
        m = num // 1000 % 10
        print('Unidade: {}'.format(u))
        print('Dezena: {}'.format(d))
        print('Centena: {}'.format(c))
        print('Milhar: {}'.format(m))

    # Exercício Python #024 - Verificando as primeiras letras de um texto
        n = str(input('Digite o nome da cidade: ')).strip()
        flag = n[:5].upper() == 'SANTO'
        print(flag)

    # Exercício Python #025 - Procurando uma string dentro de outra
        n = str(input('Digite o nome: ')).upper()
        print('Seu nome tem SILVA: {}'.format('SILVA' in n))

    # Exercício Python #026 - Primeira e última ocorrência de uma string
        frase = str(input('Digite uma frase: ')).strip().upper()
        print('Contagem de A: {}'.format(frase.count('A')))
        print('Primeiro A: {}'.format(frase.find('A')+1))
        print('Último A: {}'.format(frase.rfind('A')+1))

    # Exercício Python #027 - Primeiro e último nome de uma pessoa
        frase = str(input('Digite um nome: ')).strip()
        nome = frase.split()
        print('Primeiro Nome: {}'.format(nome[0]))
        print('Último Nome: {}'.format(nome[len(nome)-1]))

# Curso Python #10 - Condições (Parte 1)

    # Condicional IF
        tempo = int(input('Quantos anos tem seu carro?'))
        if tempo > 5:
            print('Carro velho')
        else:
            print('Carro Novo')
        print('Fim')

        tempo = int(input('Quantos anos tem seu carro?'))
        print('Carro velho' if tempo > 5 else 'Carro Novo')

        nome = str(input('Qual seu nome?'))
        if nome.upper() == 'FULA':
            print('Arrombs!')
        print('Bom dia!')

        n1 = float(input('Nota 1?'))
        n2 = float(input('Nota 2?'))
        m = (n1 + n2)/2
        if m <= 7.0:
            print('Burrão!')
        print('Sua média foi: {}.'.format(m))

    # Exercício Python #028 - Jogo da Adivinhação v.1.0
        numero = int(input('Qual número de 0 a 5 estou pensando?'))
        from random import randint
        from time import sleep
        n = randint(1, 5)
        print('Processando...')
        sleep(5)
        if numero == n:
            print('Acertou!')
        else:
            print('Errou! eu pensei {}'.format(n))

    # Exercício Python #029 - Radar eletrônico
        numero = float(input('Qual a velocidade do carro em km/h?'))
        if numero >= 80:
            multa = (numero - 80) * 7
            print('Você foi multado em: {:.2f}'.format(multa))
        else:
            print('Tenha uma bom dia')

    # Exercício Python #030 - Par ou Ímpar?
        numero = int(input('Digite um número: '))
        if (numero%2) == 0 :
            print('Par')
        else:
            print('Impar')

    # Exercício Python #031 - Custo da Viagem
        numero = float(input('Quantos km de viagem: '))
        if numero <= 200:
            print('Preço total: {:.2f}'.format(numero * 0.5))
        else:
            print('Preço total: {:.2f}'.format(numero * 0.45))

    # Exercício Python #032 - Ano Bissexto
        from datetime import date
        numero = int(input('Digite o ano: . Coloque 0 para analisar o ano atual.'))
        if numero == 0:
            numero = date.today().year
        if numero % 4 == 0 and numero % 100 != 0 or numero % 400 == 0:
            print('O ano é bissesto;')
        else:
            print('Ano de {}, não é bissesto'.format(numero))

    # Exercício Python #033 - Maior e menor valores
        n1 = int(input('Digite o primeiro número: '))
        n2 = int(input('Digite o segundo número: '))
        n3 = int(input('Digite o terceiro número: '))
        lista = [n1,n2,n3]
        menor = min(lista)
        maior = max(lista)
        print('Menor é o: {}'.format(menor))
        print('Maior é o: {}'.format(maior))

    # Exercício Python #034 - Aumentos múltiplos
        numero = float(input('Qual o salário: '))
        if numero <= 1250:
            novo = numero + (numero * 15 /100)
        else:
            novo = numero + (numero * 10 /100)
        print('Novo salário é: {:.2f}'.format(novo))

    # Exercício Python #035 - Analisando Triângulo v1.0
        n1 = float(input('Qual a medida da linha 1: '))
        n2 = float(input('Qual a medida da linha 2: '))
        n3 = float(input('Qual a medida da linha 3: '))
        if n1 < (n2 + n3) and n2 < (n1 + n3) and n3 < (n1 + n2):
            print('Dá triângulo')
        else:
            print('Não dá triângulo')

# Curso Python #11 - Cores no Terminal

    # Sistema de Cores ANSI
        print('\033[0;30;42mOlá mundo!\033[m')
        print('\033[1;30;42mOlá mundo!\033[m')
        print('\033[4;30;42mOlá mundo!\033[m')
        print('\033[7;30;42mOlá mundo!\033[m')

    # Tabela de Estilos
        Style, 0 = none, 1 = bold, 4 = itallic, 7 = negative
        Text, 30 = White, 31 = Red, 32 = Green, 33 = Yellow, 34 = Blue, 35 = Purple, 36 = Cyan, 37 = Gray, 97 = White
        Back, 40 = White, 41 = Red, 42 = Green, 43 = Yellow, 44 = Blue, 45 = Purple, 46 = Cyan, 47 = Gray, 107 = White

    # Dentro do Print
        a = 3
        b = 5
        print('\033[mOs valores são \033[31m{}\033[m e \33[32m{}'.format(a,b))

    # Em matriz
        nome = 'Fula'
        cores = {'limpa':'\033[m'
                ,'azul':'\033[34m'
                ,'amarelo':'\033[33m'
                ,'ptebc':'\033[7:30m'}
        print('Olá, como vai, tudo bem? {}{}{}!!!'.format('\033[4;34m',nome,'\033[m'))
        print('Olá, como vai, tudo bem? {}{}{}!!!'.format(cores['amarelo'],nome,cores['azul']))
