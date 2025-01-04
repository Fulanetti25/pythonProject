from decouple import config

# Leitura das variáveis do arquivo .env
IMAP_SERVER = config('IMAP_SERVER')
IMAP_USER = config('IMAP_USER')
IMAP_PASS = config('IMAP_PASS')

# Teste de leitura
print(f"Conectando ao servidor IMAP: {IMAP_SERVER}")
print(f"Usuário: {IMAP_USER}")
print(f"Senha: {IMAP_PASS}")