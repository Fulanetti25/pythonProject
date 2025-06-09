# 📦 Módulo: `cls_LogHandler`

Este módulo centraliza o registro estruturado de logs de execução e processos, usando configuração dinâmica via JSON externo. Ideal para rastrear a execução de scripts automatizados.

---

## 🔧 Classe Principal

```mermaid
classDiagram
    class LogHandler {
        - json : JsonHandler
        - nome_config : str
        - _configurar_logging()
        + execucao(modulo, funcao, status, detalhe)
        + processo(modulo, funcao, detalhe, erro)
    }


| Método                | Descrição                                                              |
|-----------------------|------------------------------------------------------------------------|


🧪 Exemplo de uso
from functions.cls_LogHandler.cls_LogHandler import LogHandler
import inspect

logger = LogHandler()
logger.processo(modulo=__name__, funcao=inspect.currentframe().f_code.co_name, detalhe="Processo executado com sucesso", erro=False)