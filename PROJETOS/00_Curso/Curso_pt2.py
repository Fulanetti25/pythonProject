# Mundo 02 - Curso de Python - Dicas e Regras

    # Curso Python #012 - Condições Aninhadas
        nome = str(input('Qual seu nome: '))
        if nome.lower() == 'paulo':
            print('Paulo é o seu nome.')
        elif nome.lower() == 'fula':
            print('Fula é seu apelido.')
        elif nome.lower() in 'jauber joseane juliana':
            print('Que diabo é isso?')
        else:
            print('Não é um nome.')

    # Exercício Python #036 - Aprovando Empréstimo
        valor = float(input('Qual o valor da casa: '))
        salario = float(input('Qual o seu salario: '))
        tempo = int(input('Em quantos anos vai pagar: '))
        parcela = valor / (tempo * 12)

        print('Para pagar uma casa de R${:.2f} em {} anos'.format(valor, tempo))
        print('A prestação será de R${:.2f}'.format(parcela))

        if parcela <= (salario * 30 / 100):
            print('EMPRÉSTIMO APROVADO')
        else:
            print('EMPRÉSTIMO REPROVADO')

    # Exercício Python #037 - Conversor de Bases Numéricas
        numero = int(input('Digite um numero: '))
        print('{} em binário é: {}'.format(numero, bin(numero)[2:]))
        print('{} em octal é: {}'.format(numero, oct(numero)[2:]))
        print('{} em hexadecimal é: {}'.format(numero, hex(numero)[2:]))

    # Exercício Python #038 - Comparando números
        n1 = int(input('Digite um numero: '))
        n2 = int(input('Digite um numero: '))

        if n1 > n2:
            print('O primeiro valor é o maior.')
        elif n2 > n1:
            print('O segundo valor é o maior.')
        else:
            print('Os números são iguais.')

    # Exercício Python #039 - Alistamento Militar
        from datetime import date
        n1 = int(input('Digite o ano de nascimento do rapaz: '))
        ano = date.today().year
        idade = ano - n1
        dif = 18-idade

        if idade <= 18:
            print('Você ainda não está em tempo de se alistar. Falta {} anos.'.format(dif))
        elif idade == 18:
            print('Está na hora de você se alistar.')
        else:
            print('Você passou do tempo de se alistar. Você atrasou em {} ano(s)'.format(abs(dif)))

    # Exercício Python #040 - Aquele clássico da Média
        n1 = float(input('Digite a nota 1: '))
        n2 = float(input('Digite a nota 2: '))
        media = (n1 + n2) / 2
        print (media)

        if media < 5.0:
            print('REPROVADO.')
        elif 7 > media >= 5.0:
            print('RECUPERAÇÃO.')
        else:
            print('APROVADO.')

    # Python Exercício #041 - Classificando Atletas
        n1 = int(input('Digite idade: '))

        if n1 <= 9:
            print('MIRIM.')
        elif n1 <= 14:
            print('INFANTIL.')
        elif n1 <= 19:
            print('JUNIOR.')
        elif n1 <= 20:
            print('SÊNIOR.')
        else:
            print('MASTER')

    # Exercício Python #042 - Analisando Triângulos v2.0
        n1 = float(input('Qual a medida da linha 1: '))
        n2 = float(input('Qual a medida da linha 2: '))
        n3 = float(input('Qual a medida da linha 3: '))
        if n1 < n2 + n3 and n2 < n1 + n3 and n3 < n1 + n2:
            print('Dá triângulo')
            if n1 == n2 == n3:
                print('EQUILÁTERO.')
            elif n1 != n2 != n3:
                print('ESCALENO.')
            else:
                print('ISÓSCELES.')
        else:
            print('Não dá triângulo')

    # Exercício Python #043 - Índice de Massa Corporal
        n1 = float(input('Digite seu peso em quilogramas: '))
        n2 = float(input('Digite sua altura em metros: '))
        imc = float(n1 / (n2**2))
        if imc < 18.5:
            print('ABAIXO DO PESO.')
        elif imc < 25:
            print('PESO IDEAL.')
        elif imc < 30:
            print('SOBREPESO.')
        elif imc < 40:
            print('OBESIDADE.')
        else:
            print('OBESIDADE MÓRBIDA.')

    # Exercício Python #044 - Gerenciador de Pagamentos
        n1 = float(input('Digite o preço: '))
        print('''
        Condições de pagamento:
        [1] = Dinheiro a vista
        [2] = Cheque a vista
        [3] = Cartão até 2x
        [4] = Cartão mais que 3x
        ''')
        tipo = int(input('Digite a condição de pagamento: '))
        if tipo == 1:
            print('Valor será: {}'.format(n1 - (n1 * 10 / 100)))
        elif tipo == 2:
            print('Valor será: {}'.format(n1 - (n1 * 5 / 100)))
        elif tipo == 3 or tipo == 4:
            parcelas = int(input('Quantas parcelas?'))
            if parcelas <= 2:
                print('Valor será: {}, em {} parcelas'.format(n1 + (n1 * 1 / 100),parcelas))
            else:
                print('Valor será: {}, em {} parcelas'.format(n1 + (n1 * 5 / 100),parcelas))
        else:
            print('Tá locão de crack?')

    # Exercício Python #045 - GAME: Pedra Papel e Tesoura
    from random import randint
    from time import sleep
        print('''
        Suas opções:
        [0] = PEDRA
        [1] = PAPEL
        [2] = TESOURA
        ''')
        itens = ('Pedra','Papel','Tesoura')
        computador = randint(0,2)
        #print ('O computador escolheu {}'.format(itens[computador]))
        jogador = int(input('Qual é a sua jogada?'))
        print('JAU')
        sleep(1)
        print('BER')
        sleep(1)
        print('PO')
        sleep(1)
        print('Computador: {}, Jogador: {}'.format(itens[computador], itens[jogador]))
        sleep(1)

        if jogador == 0: # pedra
            if computador == 0:
                print('EMPATE')
            elif computador == 1:
                print('DERROTA')
            elif computador == 2:
                print('VITÓRIA')
            else:
                print('JOGADA INVÁLIDA')

        elif jogador == 1: # papel
            if computador == 0:
                print('VITÓRIA')
            elif computador == 1:
                print('EMPATE')
            elif computador == 2:
                print('DERROTA')
            else:
                print('JOGADA INVÁLIDA')

        elif jogador == 2: # tesoura
            if computador == 0:
                print('DERROTA')
            elif computador == 1:
                print('VITÓRIA')
            elif computador == 2:
                print('EMPATE')
            else:
                print('JOGADA INVÁLIDA')

#Curso Python #013 - Estrutura de repetição for
    for i in range(0,5):
        print(i, 'Arrombado')

    for i in range(10, 0, -1):
        if i % 2 == 0 :
            print(i, 'Arrombado')

    for i in range(0, 100, 20):
        print(i, 'Arrombado')

    i = 1
    f = 10
    p = 1
    for c in range(i,f,p):
        print(c, i, f, p)

    # Exercício Python #046 - Contagem regressiva
        from time import sleep
        fogos = int(input('Quantos fogos vai estourar?'))
        for i in range(fogos, 0, -1):
            print('Estourou o fogo {}, tapora'.format(i))
            sleep(0.5)

    # Exercício Python #047 - Contagem de pares
        for i in range(0, int(input('Qual o número máximo?')), 1):
            if (i+1) % 2 == 0:
                print((i+1), '... ', end='',)
        print('\nÉ tudo par.')

    # Exercício Python #048 - Soma ímpares múltiplos de três
        soma = 0
        cont = 0
        for i in range(1, 501, 2):
            if i % 3 == 0:
                soma += i
                cont += 1
        print('A soma dos fatores é: {}'.format(soma))
        print('A cont dos fatores é: {}'.format(cont))

    # Exercício Python #049 - Tabuada v.2.0
        n = int(input('Digite o número: '))
        t = int(input('Digite o número de tabuadas: '))
        for i in range(1,t+1,1):
            print('{} x {} = {}'.format(n, i, n * i))

    # Exercício Python #050 -Soma dos pares
        soma = 0
        cont = 0
        for i in range(1,7,1):
            num = int(input('Digite um valor para a matriz {} de 6'.format(i)))
            if num % 2 == 0:
                soma += num
                cont += 1
        print('Você informou {} números PARES e a soma foi {}.'.format(cont, soma))

    # Exercício Python #051 - Progressão Aritmética
        n1 = int(input('Digite o primeiro valor:'))
        nr = int(input('Digite a razão da progressão:'))
        nt = int(input('Digite o termo da progressão:'))
        razionezimo = n1 + (nt-1) * nr
        pa = 0
        for i in range(n1,razionezimo+nr,nr):
            print('{} '.format(i), end= '→ ')
            pa += i
        print('\n',pa)

    # Exercício Python #052 - Números primos
        n = int(input('\033[30mDigite um número:'))
        l = False
        for i in range(2,n,1):
            if n % i == 0:
                print('\033[31m', end='')
                l = True
            else:
                print('\033[34m', end='')
            print('{} '.format(i), end='')
        if l == True:
            print('\033[30m\nO número {} não é primo'.format(n))
        else:
            print('\033[30m\nO número {} é primo'.format(n))

    # Exercício Python #053 - Detector de Palíndromo
        frase = str(input('Digite a frase')).replace(' ','').lower()
        inverso = frase[::-1] # Fatiou / Passou
        frase_invertida = str('')
        for caractere in range(len(frase)-1,-1,-1):
            frase_invertida = frase_invertida + frase[caractere]
        if frase == frase_invertida:
            print('É um palíndromo.')
        else:
            print('Nãolíndromo.')

    # Exercício Python #054 - Grupo da Maioridade
        from datetime import date
        ano = date.today().year
        print(ano)
        a = [0, 0, 0, 0, 0, 0, 0]
        for i in range(0, 7, 1):
            a[i] = int(input('Digite o ano de nascimento para a pessoa {} de 7'.format(i + 1)))
        for i in range(0,7,1):
            if (ano - a[i]) > 21:
                variavel = 'SIM'
            else:
                variavel = 'NÃO'
            print('A pessoa {}, que nasceu em {}, chegou à maioridade legal? {}'.format(i, a[i], variavel))

    # Exercício Python #055 - Maior e menor da sequencia
        a = [0, 0, 0]
        for i in range(0, 3, 1):
            a[i] = float(input('Digite o peso da pessoa {} de 3'.format(i + 1)))
        print('Gordão é o que pesa: {}.'.format(max(a)))
        print('Magrão é o que pesa: {}.'.format(min(a)))

    # Exercício Python #056 - Analisador completo
        somaidade = 0
        contreg = 0
        totmulher20 = 0
        nomevelho = ''
        maioridadehomem = 0
        for i in range(1,4,1):
            print('----- Pessoa {} -----'.format(i))
            # Entrada
            nome = str(input('Nome: '))
            idade = int(input('Idade: '))
            sexo = str(input('Sexo [M/F]: '))
            # Idade
            somaidade += idade
            contreg += 1
            # Nome do mais velho
            if i == 1 and sexo in 'Mm':
                maioridadehomem = idade
                nomevelho = nome
            if sexo in 'Mm' and idade > maioridadehomem:
                maioridadehomem = idade
                nomevelho = nome
            # Quantidade de fêmeas
            if sexo in 'Ff' and idade < 20:
                totmulher20 += 1
        mediaidade = somaidade / contreg
        print('A média de idade do grupo é de {:.2f} anos'.format(mediaidade))
        print('O mais velho é {} com {} anos'.format(nomevelho,maioridadehomem))
        print('Tem {} fêmeas com menos que 20 anos'.format(totmulher20))

