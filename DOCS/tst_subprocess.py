#FALHEI

import os
import sys
import tst_subprocess

# Configura o sys.path para importar módulos
sys.path.append(r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject")

# Caminho do script a ser executado
cls_Exporta = r"C:\Users\paulo\OneDrive\Documentos\Programação\pythonProject\SCRIPTS\cls_Exporta.py"

try:
    resultado = subprocess.run(
        ["python", cls_Exporta],  # Executa o script cls_Exporta.py
        text=True,
        capture_output=True,
        check=True
    )

    print("Saída padrão (stdout):")
    print(resultado.stdout)
    print("Erro padrão (stderr):")
    print(resultado.stderr)
    print(f"Código de retorno: {resultado.returncode}")

except subprocess.CalledProcessError as e:
    print("Erro na execução do subprocesso:")
    print(f"Saída padrão (stdout): {e.stdout}")
    print(f"Erro padrão (stderr): {e.stderr}")
    print(f"Código de retorno: {e.returncode}")
