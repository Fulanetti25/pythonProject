import urwid

def sair(button, user_data):
    raise urwid.ExitMainLoop()

def exibir_texto(button, user_data):
    print("Botão clicado!")

# Definindo os widgets
text_widget = urwid.Text(u"Click to interact")
button = urwid.Button(u"Click me!", exibir_texto)
footer = urwid.Text(u"Press 'q' to exit")

# Criando o Frame com os parâmetros corretos
frame = urwid.Frame(body=urwid.Pile([button]), footer=footer, header=text_widget)

# Usar o loop de evento padrão para contornar o problema no console
loop = urwid.MainLoop(frame, event_loop=urwid.AsyncioEventLoop())
loop.run()
