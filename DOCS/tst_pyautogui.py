import tst_pyautogui
import time

# Aguarda 2 segundos para garantir que a janela do Excel esteja ativa
time.sleep(2)

# Pressiona Alt + F4 para tentar fechar o Excel (similar ao fechamento manual)
pyautogui.hotkey('alt', 'f4')

# Caso haja algum prompt perguntando se você deseja salvar, você pode lidar com isso
# Aqui estamos assumindo que você quer fechar sem salvar
time.sleep(1)
pyautogui.press('left')  # Seleciona "Não salvar"
pyautogui.press('enter')
