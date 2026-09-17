# Fontes do instalador

Esta pasta preserva o código e os arquivos de build do instalador da tradução PT-BR para TriAevum.

## Componentes

- `Instalador_Traducao_PTBR_OoT3D_V4.py` — núcleo validado do instalador: validação do RomFS, aplicação dos 112 recursos, adaptação USA → EUR, 14 espelhos de menu, ajuste TopScreen, backups, restauração e status.
- `OoT3D_PTBR_TriAevum_v1.0.py` — interface gráfica final preparada para execução em modo PyInstaller one-file.
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
