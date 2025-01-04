#Testar escrita
try:
   with open(os.path.join(log_dir, 'teste.log'), 'w') as f:
       f.write("Teste de escrita no arquivo de log.\n")
   print(f"Arquivo de teste criado com sucesso: {test_log_file}")
except Exception as e:
   print(f"Erro ao escrever no arquivo: {e}")