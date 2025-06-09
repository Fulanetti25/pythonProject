# 📦 Módulo: `cls_Json`

Este módulo centraliza as operações de leitura, escrita, atualização e remoção de dados em arquivos `.json`.

---

## 🔧 Classe Principal

```mermaid
classDiagram
    class JsonHandler {
        - caminho_base : str
        + carregar(nome_arquivo)
        + salvar(nome_arquivo, dados)
        + atualizar(grupo, nome, campo, novo_valor)
        + deletar_por_filtro(server, data)
        + buscar_caminho(nome)
    }

| Método                | Descrição                                                              |
|-----------------------|------------------------------------------------------------------------|
| `carregar()`          | Carrega dados de um `.json` e retorna como dict/list.                  |
| `salvar()`            | Salva dados no `.json`, com indentação e UTF-8.                        |
| `atualizar()`         | Atualiza um campo específico de um registro dentro de um grupo.        |
| `deletar_por_filtro()`| Remove registros que combinem com filtros de `server` e `data`.        |
| `buscar_caminho()`    | Busca um caminho salvo no arquivo `caminhos.json` baseado no nome dado.|
