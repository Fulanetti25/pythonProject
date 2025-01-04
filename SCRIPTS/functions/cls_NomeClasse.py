import inspect


def fnc_NomeClasse(modulo):

	ultima_barra = modulo.rfind("\\")
	if ultima_barra == -1:
		ultima_barra = modulo.rfind("/")

	varg_modulo = modulo[ultima_barra + 1:]
	return varg_modulo


def main():
	resultado = fnc_NomeClasse(inspect.stack()[0].filename)
	print(resultado)


if __name__ == "__main__":
	main()