# Inserção por linhas manualmente
import csv
with open(r'C:\Users\paulo\PycharmProjects\pythonProject\FILES/names1.csv', 'w') as csvfile:
    fieldnames = ['first_name', 'last_name']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'first_name': 'baked1', 'last_name': 'beans1'})
    writer.writerow({'first_name': 'baked2', 'last_name': 'beans2'})
    writer.writerow({'first_name': 'baked3', 'last_name': 'beans3'})
    writer.writerow({'first_name': 'baked4', 'last_name': 'beans4'})
    print('Sucesso')

# Inserção por lista em laço
import csv
names = [{'first_name': 'baked1', 'last_name': 'beans1'},
         {'first_name': 'baked2', 'last_name': 'beans2'},
         {'first_name': 'baked3', 'last_name': 'beans3'},
         ]
with open(r'C:\Users\paulo\PycharmProjects\pythonProject\FILES/names2.csv', 'w') as csvfile:
    fieldnames = names[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in names:
        writer.writerow(row)
    print('Sucesso')

# Inserção por lista completa
import csv
names = [{'first_name': 'baked1', 'last_name': 'beans1'},
         {'first_name': 'baked2', 'last_name': 'beans2'},
         ]
with open(r'C:\Users\paulo\PycharmProjects\pythonProject\FILES/names3.csv', 'w') as csvfile:
    fieldnames = names[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(names)
    print('Sucesso')

with open(r'C:\Users\paulo\PycharmProjects\pythonProject\FILES/append.txt',"a") as arq:
    arq.write("Olá mundo1\n")
    arq.write("Olá mundo2\n")

# Leitura e substituição de caractere em arquivo
tsvfile = open(r'C:\Users\paulo\OneDrive\Área de Trabalho\archive/2004-2021.tsv', 'r', encoding = 'UTF-8')
csvfile = open(r'C:\Users\paulo\OneDrive\Área de Trabalho\archive/2004-2021.csv', 'w')
# print(tsvfile.read())
# print(tsvfile.readlines(5))
while 1:
    old_char = tsvfile.read(1)
    # break # Quebra de Linha
    if ord(old_char) == 9:
        new_char = ';'
    else:
        new_char = old_char
    # print('Caractere:', old_char,'ASCII:', ord(old_char), 'Vira:', new_char, 'ASCII:', ord(new_char))
    # print(new_char, end = '')
    csvfile.write(new_char)


