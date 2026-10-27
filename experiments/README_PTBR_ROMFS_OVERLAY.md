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
