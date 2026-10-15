# Compatibilidade da 1.2.1 com TriAevum beta.1c

Verificação local em Windows x64, em 15/10/2026. Os testes usaram cópia da instalação e dos saves; a pasta preparada pelo usuário foi preservada.

## Mudanças relevantes

- O Forge passou a gerar caminhos com `${runtime_dir}`. O núcleo aceita esse prefixo e o anterior `${profile_dir}`, mantendo os caminhos dentro da instalação selecionada e recusando variáveis desconhecidas.
- A atualização acumulada desde beta.1 modifica o plugin do título, TopScreen, menus, renderização, upscalers e políticas de carregamento. O runtime HD foi recompilado sobre os fontes da beta.1c; não reutiliza o EXE HD anterior.
- O RomFS preparado permanece na base conhecida. Os 112 recursos e 14 espelhos continuam resultando em 126 operações de tradução. A cobertura de fonte HD e a normalização dos acentos foram preservadas.
- As 71 correspondências de texturas e a composição do aviso Navi permanecem na receita. Packs continuam externos.

## Identidades

| Arquivo | SHA-256 |
| --- | --- |
| TriAevum.exe original beta.1c | `fe0b3b8cbff5c414d6e61817e810afa65ecd3f71f3a34d381cfb975445dcf404` |
| Runtime HD recompilado | `c84862b74da18aa73a922d8ab34a0937c0c8beec7aa44f2b90de6d079738adbf` |
| RomFS original | `dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56` |
| RomFS traduzido | `26caf9f8ea36c106f7fd8a9c737b09203ce4535d0113d5ba946e917058e8a39b` |

## Validação

- 33 testes Python de segurança e integração passaram.
- Testes C++ do provedor de texturas e renderer da UI passaram.
- Instalação e restauração reais da tradução e do HD passaram na cópia isolada.
- Seleção de arquivos: execução concluída, captura em português.
- Menu de pausa: 4.384 frames de jogo, captura com texturas HD e layout PS5; 58 consultas do provedor, 51 consultas pendentes e 5 substituições concluídas.
- O patch distribuído reproduz os 13 arquivos C++/CMake alterados na compilação, a partir do arquivo de fontes original da beta.1c.

Essa verificação cobre instalação, restauração, abertura e menus. Não certifica todas as cenas do jogo. Linux mantém a tradução comum experimental, com validação funcional no jogo pendente.
