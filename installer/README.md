# Fontes do instalador

O instalador atual é a **v1.2.1**, para **TriAevum v0.8.0-beta.1c**. Consulte [BUILD_V1.2.1.md](BUILD_V1.2.1.md) para gerar os pacotes e [HD_INTEGRACAO.md](HD_INTEGRACAO.md) para adicionar ou remover as texturas HD. A interface atual é `OoT3D_PTBR_TriAevum_v1.2.1.py`; o núcleo é `Instalador_Traducao_PTBR_OoT3D_V4_compat_test.py`.

## Histórico da primeira versão

### Atualização v1.3.0-experimental.2

O botão separado de recuperação foi removido. Ao clicar em **Instalar / aplicar
fonte**, o instalador recupera primeiro qualquer operação interrompida verificável
e depois instala a tradução ou aplica a fonte selecionada na tentativa atual.
**Restaurar original** também recupera operações anteriores antes de restaurar;
se a recuperação já concluiu a restauração, apenas verifica o original.
Alterações externas incompatíveis continuam bloqueando a operação, com arquivos
preservados. A consulta de status não altera arquivos.

Gate local: 24 testes, incluindo reinstalação após interrupções na cópia,
ativação do perfil, fonte e restauração, além da recusa de perfil externo.

Esta pasta preserva o código e os arquivos de build do instalador da tradução PT-BR para **TriAevum v0.6.0-alpha.2c**.

**Compatibilidade validada:** TriAevum **v0.6.0-alpha.2c Windows x64**. O protótipo Linux desta pasta também tem como alvo a **v0.6.0-alpha.2c distribuída via Flatpak**.

## Componentes

- `Instalador_Traducao_PTBR_OoT3D_V4.py` — núcleo validado do instalador: validação do RomFS, aplicação dos 112 recursos, adaptação USA → EUR, 14 espelhos de menu, ajuste TopScreen, backups, restauração e status.
- `OoT3D_PTBR_TriAevum_v1.0.py` — interface gráfica final para Windows, validada com TriAevum v0.6.0-alpha.2c e preparada para execução em modo PyInstaller one-file.
- `OoT3D_PTBR_TriAevum_v1.0_Linux.py` — protótipo Linux/Flatpak direcionado especificamente ao TriAevum v0.6.0-alpha.2c; ainda requer validação Linux.
- `OoT3D_PTBR_TriAevum_v1.0.spec` — configuração PyInstaller usada para incorporar o núcleo e o payload `TraducaoCompleta`.
- `GERAR_EXE_WINDOWS.bat` — script de compilação no Windows.
- `COMO_GERAR_EXE.txt` — instruções rápidas de build.

## Payload da tradução

O build final espera a estrutura:

```text
TraducaoCompleta/
└── citra/
    └── romfs/
```

O payload validado contém 112 recursos reais da tradução. A pasta `scene/fazer` do pacote original contém arquivos-base/backup e não é incorporada ao instalador.

## Build

Em Windows com Python 3 instalado, execute `GERAR_EXE_WINDOWS.bat`. O script instala/atualiza o PyInstaller e gera:

```text
dist\OoT3D_PTBR_TriAevum_v1.0.exe
```

O executável deve ser colocado diretamente na raiz do TriAevum, ao lado de `TriAevum.launch.json`.

## Release validada

A release pública v1.0.0 distribui `OoT3D_PTBR_TriAevum_v1.0.zip`. O SHA-256 do ZIP validado é:

`7bdcb391d4ae746d456c1bcb853371bd8be1bb9a3b9e63311aab1b487b300f7b`


### Henriko com as texturas nativas PT-BR

O carregador reconhece imagens por hash; traduzir as texturas muda esses hashes.
Para quem deseja o Henriko original sobre a tradução, há um
[pack.json externo opcional](../compatibility/henriko-5.0a-ptbr-v1.3.0/README.md)
com 71 aliases. Aprovado pelo usuário, testado com menus HD em inglês, sem PNGs
adaptados nem executável modificado. Esse arquivo é aplicado manualmente ao
pack pelo usuário, e não pelo instalador. Leia a instrução sobre a raiz do pack.
