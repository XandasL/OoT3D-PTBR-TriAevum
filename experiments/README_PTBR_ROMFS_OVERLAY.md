## Novo gate de teste (27/10/2026) — validação somente de leitura

A rotina de conversão `ptbr_qm_beta12.py` agora implementa os **2510 registros**, cópia dos slots EUR e normalização de aliases UTF-8, aceitando apenas o arquivo QM original de SHA-256 aprovado. O gerador preserva o arquivo QBF nativo da ROM e confirma que os primeiros 1608 bytes (métricas/diretório) coincidem com o payload aprovado. Foram adicionados testes sintéticos `test_ptbr_qm_beta12.py`.

O primeiro passo é executar, na raiz do projeto:

```powershell
py -3 experiments\\test_ptbr_qm_beta12.py
```

Depois, com um checkout do código-fonte TriAevum exatamente em `v0.8.0-beta.1.2`, rode o gerador com `--check-only` apontando para o RomFS validado, o manifesto e a tradução local. Esse modo confere os **126 destinos**, confirma o SHA-256 da base e executa a conversão do QM em pasta temporária; **não cria arquivo O3RO, não edita o perfil de execução e não modifica a instalação**.

Somente após o resultado `overlay_targets_found: 126` / `native_font_preserved: true` será permitido criar um arquivo O3RO experimental fora da pasta do jogo. Isso ainda não resolve TopScreen, HD64, compatibilidade com outros mods nem ativação no Forge. Os testes ainda não foram executados pelo autor para esta alteração.

## Base local validada pelo autor — 27/10/2026

O teste no Windows beta.1.2 encontrou `romfs_service_offset=0`, `romfs_service_size=473522176`, arquivo local `romfs.bin` com **473522176 bytes** e **SHA-256 `dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56`**. Esse hash coincide com o contrato beta conhecido, e o script experimental agora recusa bases de tamanho/hash diferente. O autor também confirmou os **112 arquivos da tradução, todos com SHA-256 íntegro** via `ptbr_romfs_overlay_probe.py --payload ... --json`. A geração de O3RO continua bloqueada até conversão QM e testes do TopScreen.

## Bloqueio de segurança antes do teste em jogo (27/10/2026)

A auditoria identificou que o V4 converte os **2510 registros QM** e normaliza os aliases PT-BR. A conversão foi implementada em módulo experimental com validação por hash, mas **a execução no jogo ainda não foi validada**. Priorize o teste sintético e o modo `--check-only`; não instale um overlay não testado.

# Experimento isolado — tradução PT-BR como mod RomFS nativo (O3RO)

**Estado: EXPERIMENTO DE GERADOR O3RO PARA beta.1.2; NÃO É INSTALADOR FINAL OU MOD PRONTO PARA DISTRIBUIÇÃO.**

Base: branch `feat/v1.3.0-full-ptbr-native-textures`, sem mudar o `main`, a release v1.3.0, os ZIPs, o TriAevum ou os saves.

## Resultado da leitura do código original do TriAevum

- `coccofresco/TriAevum/docs/TRIAEVUM_MOD_VANILLA_PLUS_LINK.md` documenta o **O3RO v1**, que substitui arquivos RomFS por uma visão virtual e o argumento de execução `--romfs-overlay <file>`.
- `tools/triaevum_release/romfs_mods.py` contém um catálogo fechado (`CATALOG`) para mods previamente aprovados; Forge não oferece importação universal de pacotes ou pastas PT-BR.
- O overlay valida a identidade dos bytes originais de metadados, exige caminhos existentes no RomFS e modifica a visão virtual, não a ROM original.
- A integração do Vanilla+ no Forge não implica compatibilidade automática com os **112** arquivos de tradução, seus **14** espelhos EUR ou as opções de fonte HD64.
- Para a tradução real, são necessários testes de overlays grandes, localização dos arquivos no serviço RomFS, idioma EUR/USA, convivência com TopScreen e outros mods, persistência e restauração de saves.

## Prova de conceito desta branch

`experiments/ptbr_romfs_overlay_probe.py` é uma **sonda somente de leitura**: conta os recursos originais por pasta e, opcionalmente, verifica o SHA-256 de cada arquivo contra o manifesto do instalador. Não cria overlays, não grava arquivos, não baixa ROMs e não ativa mods.

Executar da raiz do checkout:

```sh
python experiments/ptbr_romfs_overlay_probe.py --json
python experiments/ptbr_romfs_overlay_probe.py --payload "/caminho/para/TraducaoCompleta/citra/romfs" --json
```

Um resultado positivo no SHA-256 significa somente que a fonte da tradução é íntegra. **Não** significa que Forge possa carregá-la.

## Critérios antes da primeira execução no jogo

1. Obter uma interface documentada e compatível com TriAevum **v0.8.0-beta.1.2** (tag exata confirmada no GitHub). Seu código contém \`romfs_mods.py\` e O3RO v1. Não presumir suporte automático a uma tradução PT-BR completa.
2. Produzir o O3RO em pasta privada de teste a partir da ROM fornecida pelo próprio usuário, com hashes e proteção contra caminhos inesperados.
3. Confirmar que a montagem inclui os 112 arquivos originais e os espelhos EUR relevantes, sem perda da tradução nem regressão de fonte.
4. Validar conflitos com TopScreen / SingleScreen e compatibilidade Henriko, bem como o comportamento ao remover o mod.
5. Apenas após testes sintéticos e validação real, propor integração opt-in. Nenhuma alteração automática na release está autorizada.

Fontes: https://github.com/coccofresco/TriAevum/blob/main/docs/TRIAEVUM_MOD_VANILLA_PLUS_LINK.md e https://github.com/coccofresco/TriAevum/blob/main/tools/triaevum_release/romfs_mods.py

## Alvo confirmado — v0.8.0-beta.1.2

Tag oficial: https://github.com/coccofresco/TriAevum/releases/tag/v0.8.0-beta.1.2 (22/10/2026). Nesta tag existe o módulo `romfs_mods.py` com `build_romfs_overlay` e `romfs_service_view`. O Forge ainda controla a ativação pelos mods catalogados.

### Gerador experimental dos 126 alvos

O script `experiments/build_ptbr_o3ro_beta12.py` utiliza **a implementação O3RO original desta tag**, sem copiar ou modificar runtime:
- valida SHA-256 de **112 arquivos** originais antes de qualquer escrita;
- replica o remapeamento de `message/us` para `message/eu`, de `misc/us` para `misc/eu` e os **14 CTXB** em `menu/02_EU_ENGLISH`;
- rejeita alvos ausentes no RomFS, source checkout diferente da tag, conflitos de caminho e sobreescrita de saída;
- gera **somente um arquivo O3RO separado**, sem mudar RomFS, savegames, Forge ou o perfil de execução.

Exemplo de teste local, **apenas em cópias** e com arquivos da ROM obtida pelo próprio usuário:

```sh
git clone https://github.com/coccofresco/TriAevum.git TriAevum-beta12-src
git -C TriAevum-beta12-src checkout v0.8.0-beta.1.2
python experiments/build_ptbr_o3ro_beta12.py \
  --triaevum-source ./TriAevum-beta12-src \
  --payload "/caminho/TraducaoCompleta/citra/romfs" \
  --romfs-image "/caminho/copia-original/romfs.bin" \
  --process-manifest "/caminho/copia-original/process-manifest.json" \
  --output "/caminho/experimentos/ptbr-beta12.o3ro"
```

**Não adicionar ainda `--romfs-overlay` ao perfil padrão.** A tradução precisa de um teste de conflito com mods existentes, verificação de leitura do RomFS virtual e diagnóstico do TopScreen: o instalador anterior ajustava o hash do `menu_top` no O3TU, coisa que um O3RO isolado não faz. A fonte HD64 segue como experimento separado.

O comando gera um artefato privado de teste, não um pacote redistribuível. A execução real no jogo ainda não foi validada.
