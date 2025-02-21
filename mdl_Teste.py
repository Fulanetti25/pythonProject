import os
import csv
from math import comb
from itertools import combinations

combinacoes_validas = []

mapa_quadrantes = {
    "Q1": set(range(1, 6)) | set(range(11, 16)) | set(range(21, 26)),
    "Q2": set(range(6, 11)) | set(range(16, 21)) | set(range(26, 31)),
    "Q3": set(range(31, 36)) | set(range(41, 46)) | set(range(51, 56)),
    "Q4": set(range(36, 41)) | set(range(46, 51)) | set(range(56, 61))
}

mapa_linhas = {
    "L1": set(range(1, 11)),
    "L2": set(range(11, 21)),
    "L3": set(range(21, 31)),
    "L4": set(range(31, 41)),
    "L5": set(range(41, 51)),
    "L6": set(range(51, 61))
}

mapa_colunas = {
    "C1": {1, 11, 21, 31, 41, 51},
    "C2": {2, 12, 22, 32, 42, 52},
    "C3": {3, 13, 23, 33, 43, 53},
    "C4": {4, 14, 24, 34, 44, 54},
    "C5": {5, 15, 25, 35, 45, 55},
    "C6": {6, 16, 26, 36, 46, 56},
    "C7": {7, 17, 27, 37, 47, 57},
    "C8": {8, 18, 28, 38, 48, 58},
    "C9": {9, 19, 29, 39, 49, 59},
    "C0": {10, 20, 30, 40, 50, 60}
}


def filtrar(filtros):
    validos = 0
    todas_dezenas = []
    global combinacoes_validas
    combinacoes_validas = []

    # Aqui alimentamos os jogos da amostra
    for quadrante in filtros['quadrantes']:
        dezenas_quadrante = mapa_quadrantes[quadrante]
        todas_dezenas.extend(dezenas_quadrante)

    # Aqui processamos os jogos da amostra 1 a 1
    #LAÇO DAS COMBINAÇÕES
    for combinacao in combinations(todas_dezenas, filtros['dezenas_por_jogo']):
        combinacao_filtrada = True

        #REGRA 3)  X (0 a 6) Dezenas em 1 dos quadrantes - VALIDADO
        if filtros['max_dezenas_quadrante']:
            achou = False
            for quadrante in filtros['quadrantes']:
                dezenas_no_quadrante = [dezena for dezena in combinacao if dezena in mapa_quadrantes[quadrante]]
                quantidade_dezenas = len(dezenas_no_quadrante)
                # print(f"Combinacao: {combinacao} Quadrante: {quadrante}, Dezenas no quadrante: {dezenas_no_quadrante}, Quantidade: {quantidade_dezenas}")
                if quantidade_dezenas == filtros['max_dezenas_quadrante']:
                    achou = True
            if achou == True:
                combinacao_filtrada = False

        #REGRA 4) até X(0 a 6) números ímpares - VALIDADO
        if filtros['max_impares'] or filtros['max_impares'] == 0:
            impares = [dezena for dezena in combinacao if dezena % 2 != 0]
            quantidade_impares = len(impares)
            if quantidade_impares <= filtros['max_impares']:
                combinacao_filtrada = False

        #REGRA 5) até X (0 a 6) números pares - VALIDADO
        if filtros['max_pares'] or filtros['max_pares'] == 0:
            pares = [dezena for dezena in combinacao if dezena % 2 == 0]
            quantidade_pares = len(pares)
            if quantidade_pares <= filtros['max_pares']:
                combinacao_filtrada = False

        #REGRA 6) até X (0 a 10) números por linha - VALIDANDO
        if filtros['max_por_linha']:
            for linha in mapa_linhas:
                dezenas_na_linha = [dezena for dezena in combinacao if dezena in mapa_linhas[linha]]
                quantidade_linha = len(dezenas_na_linha)
                # print(f"Combinacao: {combinacao} Linha: {linha}, Dezenas no quadrante: {dezenas_na_linha}, Quantidade: {quantidade_linha}")
                if quantidade_linha <= filtros['max_por_linha']:
                    combinacao_filtrada = False

        #REGRA 7) até X (0 a 6) números por coluna
        if filtros['max_por_coluna']:
            for coluna in mapa_colunas:
                dezenas_na_coluna = [dezena for dezena in combinacao if dezena in mapa_colunas[coluna]]
                quantidade_coluna = len(dezenas_na_coluna)
                # print(f"Combinacao: {combinacao} Coluna: {coluna}, Dezenas no quadrante: {dezenas_na_coluna}, Quantidade: {quantidade_coluna}")
                if quantidade_coluna <= filtros['max_por_coluna']:
                    combinacao_filtrada = False

        #REGRA 8) até X (0 a 6) dezenas em sequência

        #REGRA 9) até X (0 a 6) dezenas na mesma linha Y

        #SAIDA UNICA
        if combinacao_filtrada == False:
            combinacoes_validas.append(combinacao)
            validos += 1

    return validos


def calcular_combinacoes_total(n_total, v_jogados, v_acertos):
    return comb(n_total, v_jogados) * comb(v_jogados, v_acertos)


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Processando... Aguarde a atualização da tela.", end='', flush=True)


def exibir_menu():
    filtros = {
        "dezenas_por_jogo": 6,
        "quadrantes": ['Q1','Q2'], #,'Q3','Q4'
        "max_dezenas_quadrante": None,
        "max_impares": None,
        "max_pares": None,
        "max_por_linha": None,
        "max_por_coluna": None,
        "max_sequencia": None,
        "max_na_mesma_linha": None
    }

    while True:
        limpar_tela()

        total_quadrante_sena = calcular_combinacoes_total(len(filtros['quadrantes'])*15, filtros['dezenas_por_jogo'], 6)
        total_quadrante_quina = calcular_combinacoes_total(len(filtros['quadrantes'])*15, filtros['dezenas_por_jogo'], 5)
        total_quadrante_quadra = calcular_combinacoes_total(len(filtros['quadrantes'])*15, filtros['dezenas_por_jogo'], 4)
        probabilidade_sena = 1 / total_quadrante_sena if total_quadrante_sena > 0 else 0
        probabilidade_quina = 1 / total_quadrante_quina if total_quadrante_quina > 0 else 0
        probabilidade_quadra = 1 / total_quadrante_quadra if total_quadrante_quadra > 0 else 0
        jogos_validos = filtrar(filtros)

        cabecalho = f"{'Combinações':>16} | {'Probabilidade':>18}"
        print("\033[F\033[K", end='', flush=True)  # Move para cima e limpa a linha
        print("\n" + " " * 6 + "Tabela de Probabilidades Inicial" + " " * 10 + "|" + " " * 10 + "Tabela de   Combinações  Final")
        print("-" * 48 + "|" + "-" * 48)
        print(f"{' ':>10}{cabecalho} | ")
        print("-" * 48 + "|" + "-" * 48)
        print(f"{'Sena:':>10} {total_quadrante_sena:>15,.0f} | {probabilidade_sena:>18.15f} | {'Combinações:':>10} {jogos_validos:>34,.0f}")
        print(f"{'Quina:':>10} {total_quadrante_quina:>15,.0f} | {probabilidade_quina:>18.15f} |")
        print(f"{'Quadra:':>10} {total_quadrante_quadra:>15,.0f} | {probabilidade_quadra:>18.15f} |")
        print("-" * 48 + "|" + "-" * 48)

        print("Menu de Filtros:")
        print(f"1) SELECIONE quantas dezenas por jogo (2 a 20): {filtros['dezenas_por_jogo']}")
        print(f"2) SELECIONE os quadrantes: {filtros['quadrantes']}")
        print(f"3) JOGOS COM X (0 a 6) Dezenas em 1 único quadrante: {filtros['max_dezenas_quadrante']}")
        print(f"4) JOGOS COM até X (0 a 6) números ímpares: {filtros['max_impares']}")
        print(f"5) JOGOS COM até X (0 a 6) números pares: {filtros['max_pares']}")
        print(f"6) JOGOS COM até X (0 a 10) números por linha: {filtros['max_por_linha']}")
        print(f"7) JOGOS COM até X (0 a 6) números por coluna: {filtros['max_por_coluna']}")
        print(f"8) JOGOS COM até X (0 a 6) dezenas em sequência: {filtros['max_sequencia']}")
        print(f"9) JOGOS COM até X (0 a 6) dezenas na mesma linha Y: {filtros['max_na_mesma_linha']}")
        print(f"X) EXPORTAR jogos")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            filtros['dezenas_por_jogo'] = int(input("Digite o número de dezenas por jogo (2 a 20): "))
        elif opcao == "2":
            filtros['quadrantes'] = input("Digite os quadrantes separados por vírgula (ex: Q1,Q3): ").strip().upper().split(',')
        elif opcao == "3":
            filtros['max_dezenas_quadrante'] = int(input("Digite quantas dezenas em um único quadrante (0 a 6): "))
        elif opcao == "4":
            filtros['max_impares'] = int(input("Digite o máximo de números ímpares (0 a 6): "))
        elif opcao == "5":
            filtros['max_pares'] = int(input("Digite o máximo de números pares (0 a 6): "))
        elif opcao == "6":
            filtros['max_por_linha'] = int(input("Digite o máximo de números por linha (0 a 10): "))
        elif opcao == "7":
            filtros['max_por_coluna'] = int(input("Digite o máximo de números por coluna (0 a 6): "))
        elif opcao == "8":
            filtros['max_sequencia'] = int(input("Digite o máximo de dezenas em sequência (0 a 6): "))
        elif opcao == "9":
            filtros['max_na_mesma_linha'] = int(input("Digite o máximo de dezenas na mesma linha (0 a 6): "))
        elif opcao.strip().upper() == "X":
            resposta = input(f'Isto vai exportar {jogos_validos:>15,.0f}'.replace(",", ".") + ' linhas de jogos. Tem certeza que deseja continuar? (s/n)').strip().upper()
            if resposta == "S":
                # Exportação para CSV
                nome_arquivo = "combinacoes_validas.csv"
                with open(nome_arquivo, mode="w", newline="") as arquivo_csv:
                    escritor_csv = csv.writer(arquivo_csv, delimiter=';')
                    escritor_csv.writerow(["Dezenas"])
                    for combinacao in combinacoes_validas:
                        escritor_csv.writerow(['-'.join(map(str, combinacao))])
                print(f"Arquivo {nome_arquivo} gerado com {len(combinacoes_validas)} combinações válidas.")
                input("Pressione Enter para continuar...")
        else:
            print("Opção inválida! Tente novamente.")

    return filtros


filtros_selecionados = exibir_menu()
print("\nFiltros selecionados:", filtros_selecionados)