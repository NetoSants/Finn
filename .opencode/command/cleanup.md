---
description: Audita e limpa código morto, formatação insegura, redundâncias e docs desatualizados.
---

Audite o código fonte e faça uma limpeza completa:

1. **Código morto**: Encontre arquivos, funções, classes e imports que não são mais usados. Delete arquivos órfãos, remova imports não utilizados, elimine funções que não são chamadas.

2. **Formatação insegura**: Remova parâmetros que podem causar crash com dados do usuário (`parse_mode="Markdown"`, `unsafe` em templates, etc). Use texto puro ou HTML escapado.

3. **Redundâncias**: Se existirem comandos/fluxos que duplicam funcionalidade existente, remova os redundantes e atualize help/docs.

4. **Integrações abandonadas**: Se houver código de serviços externos que não são mais usados (APIs, SDKs), remova arquivos, imports, variáveis de ambiente e dependências.

5. **Comentários obsoletos**: Remova `# TODO`, `# FIXME`, código comentado e blocos de "implementar futuramente".

6. **`.env.example`**: Mantenha apenas variáveis realmente necessárias.

7. **Tipos inconsistentes**: Procure por bugs de tipo (Decimal * float, str + None, etc) e converta explicitamente.

8. **README/docs**: Atualize listas de comandos, features e stack para refletir apenas o que existe.

No final, mostre um resumo com diff de tudo que foi alterado. $ARGUMENTS
