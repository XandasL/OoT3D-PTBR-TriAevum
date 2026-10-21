# HD 128 — experimento de desempenho do decodificador A4

Este experimento é **isolado**. Ele não altera o instalador da tradução, o atlas HD 128, o ROMFS, os arquivos de texturas personalizados ou a release pública.

## Origem

Arquivos fornecidos pelo usuário após interrupção do Codex em 21/10/2026:

- `pica_texture_decode.reference.cpp`: implementação A4 de referência.
- `pica_texture_decode.cpp`: versão otimizada.
- `tests/decoder_equivalence.cpp`: comparação de saída e erros em 33 casos, benchmark de uma textura A4 4096×2048.
- `tests/CMakeLists.txt`: teste C++20 isolado.

O teste compila as duas implementações com namespaces distintos. A variante A4 otimizada trata diretamente blocos 8×8 codificados na ordem Morton, com tabela de alpha e `memcpy` por par de pixels. Para dimensões não alinhadas mantém a rotina anterior. Outros formatos de textura não foram intencionalmente otimizados.

## Validação e limites

O Codex relatou ~73 ms para ~10 ms na decodificação isolada e 33 casos equivalentes; esse número **ainda não foi reproduzido por esta sessão**. O CI executa CTest no Windows e Linux com o código-base `v0.8.0-beta.1.1`.

O relatório do jogo mostra uma diferença de picos na cena inicial com fonte HD 128 (13 quadros >33,33 ms, contra 2 com fonte original, na comparação aquecida), com mais eventos WASAPI. Entretanto, tempo em `present` não distingue decodificação, reconstrução da fonte, upload, shader ou sincronização de GPU.

**Não declarar a regressão corrigida sem um novo teste no jogo.** A otimização do decodificador não elimina o trabalho em `NativeHdFontRuntime::Resolve()` de criar/recompor todo o atlas HD e produzir um hash. O runtime não foi reconstruído aqui; o erro de vínculo AOT identificado anteriormente precisa de análise específica, sem substituir símbolos por stubs silenciosamente.

## Próximo experimento seguro

1. Verificar a equivalência do CI e as medidas em Windows.
2. Usar um checkout isolado do TriAevum beta.1.1; manter o original preservado.
3. Se a compilação completa falhar, capturar erro de *link* completo e dependências; não aplicar correção AOT por suposição.
4. Instrumentar `NativeHdFontRuntime::Resolve` (tempo de comparação, composição A4, hash), decodificação A4, atualização da textura e espera em `present`.
5. Testar a mesma introdução em condições equivalentes: fonte original, HD 128 com runtime original, HD 128 com runtime candidato; ordem contrabalanceada e caches aquecidos.
6. Comparar distribuição dos frames, falhas do áudio e hashes de pixels. Somente então avaliar adoção do patch.
