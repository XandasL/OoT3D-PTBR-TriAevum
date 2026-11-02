# The Legend of Zelda: Ocarina of Time 3D — Tradução PT-BR para TriAevum

Adaptação para **TriAevum** da tradução brasileira de *The Legend of Zelda: Ocarina of Time 3D*, com diálogos, menus e texturas nativas traduzidas.

> **Versão atual: [v2.0 Beta](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/2.0)** — compatível com **TriAevum v0.8.0-beta.1.2**. Windows x64 testado pelo autor; Linux x86_64 experimental, ainda sem validação dentro do jogo.

## 🇧🇷 Sobre a tradução

O projeto adapta uma tradução PT-BR existente, com autorização de seus responsáveis. A tradução preserva diálogos, nomes de locais, mensagens, menus e recursos gráficos nativos. O port também adapta os arquivos necessários ao ambiente EUR utilizado pelo TriAevum.

## ✨ v2.0 Beta — o que muda

- **Mod O3RO completo:** 126 substituições, incluindo os recursos gráficos nativos traduzidos.
- **Instalação portátil:** ativadores para Windows (CMD/PowerShell) e Linux (Bash), sem modificar o executável do TriAevum.
- **Arquivos originais preservados:** o mod utiliza um overlay virtual; não modifica o executável do TriAevum nem a RomFS original.
- **Integridade e backup:** verificação SHA-256 do O3RO e cópia de segurança do perfil de inicialização antes da alteração.
- **Créditos no pacote:** o `LEIA-ME.txt` contém os créditos e as informações de autorização da tradução.

O pacote da v2.0 Beta não inclui imagens HD, atlas TopScreen ou recursos de terceiros. **A compatibilidade com pacotes de texturas personalizadas não é garantida**, pois algumas substituições podem deixar de carregar quando seus hashes diferem dos recursos nativos traduzidos.

## 📥 Downloads da v2.0 Beta

| Plataforma | Arquivo |
| --- | --- |
| **Windows x64 — testado** | [OoT3D_PTBR_TriAevum_v2.0_Windows-x64.zip](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/2.0/OoT3D_PTBR_TriAevum_v2.0_Windows-x64.zip) |
| **Linux x86_64 — experimental** | [OoT3D_PTBR_TriAevum_v2.0_Linux-x86_64.zip](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/2.0/OoT3D_PTBR_TriAevum_v2.0_Linux-x86_64.zip) |

O pacote Linux é único para instalações do TriAevum via **AppImage ou Flatpak**. Não é um aplicativo independente. O ativador Linux requer Bash, `jq` e `sha256sum`; não requer Python.

[Consulte a release v2.0 Beta e as observações de compatibilidade.](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/2.0)

### Versões anteriores

| Release | TriAevum |
| --- | --- |
| [v1.3.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.3.0) | v0.8.0-beta.1.1 |
| [v1.2.1](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.1) | v0.8.0-beta.1c |
| [v1.2.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.0) | v0.8.0-beta.1 |
| [v1.1.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.1.0) | v0.8.0-beta.1 |
| [v1.0.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v1.0.0) | v0.6.0-alpha.2c |

Utilize o pacote correspondente à sua versão do TriAevum. As releases anteriores continuam disponíveis com seus próprios métodos de instalação.

## 🛠️ Instalação da v2.0 Beta

1. Prepare o jogo pelo **TriAevum Forge v0.8.0-beta.1.2** e feche o jogo e o Forge.
2. Extraia o ZIP de seu sistema na pasta preparada pelo TriAevum, preservando as subpastas.
3. **Windows:** execute `Ativar-PTBR.cmd`. **Linux:** abra o terminal na pasta de extração e execute `bash Ativar-PTBR-Linux.sh` (requer `jq` instalado).
4. Inicie o TriAevum normalmente.

O ativador verifica `data/mods/OoT3D-PTBR/OoT3D-PTBR.o3ro` e modifica somente `data/TriAevum.launch.json` para configurar `--romfs-overlay`. Antes disso, cria um backup do perfil quando ainda não existe. Não altera saves, o executável ou a RomFS original.

Se o Forge regenerar o perfil após um novo **Prepare and install**, talvez seja necessário ativar o mod novamente.

### Texturas personalizadas

A v2.0 Beta foi validada com os gráficos clássicos. Com pacotes HD ou personalizados ativados, algumas texturas, principalmente de HUD e menus, podem não carregar como esperado. **Essa compatibilidade permanece limitada nesta versão.** Nenhuma imagem HD de terceiros acompanha o download.

### Remoção da v2.0 Beta

Não há desinstalador automático. Com o jogo fechado, remova o parâmetro `--romfs-overlay` e o caminho associado do perfil `data/TriAevum.launch.json`, ou restaure o backup do perfil se ele for adequado à sua instalação. Depois, caso deseje, remova a pasta `data/mods/OoT3D-PTBR`. **Não remova a RomFS nem os saves.**

## ✅ Validação

O autor testou o carregamento da tradução clássica, com 126 substituições, e confirmou que o pacote portátil com o ativador revisado funciona no Windows usando o **TriAevum v0.8.0-beta.1.2**. A integridade do O3RO também é verificada pelo SHA-256. A v2.0 Beta não possui certificação de compatibilidade com Linux ou outras versões do TriAevum.

## ❤️ Créditos e autorização

**Tradução PT-BR original:**
- Projeto Zelda Brasil – Heroes of Time
- Catatau Game Dev e Traduções
- Elite dos Quatro Traduções
- JumpManClub Brasil Traduções
- TRADU-ROMS

**Port e adaptação para TriAevum:** XandasL.

A tradução original não foi criada por este repositório. O port e a distribuição da tradução completa são realizados com autorização do responsável pela tradução, condicionados à manutenção dos créditos dentro e fora do jogo. Os créditos também estão incluídos no `LEIA-ME.txt` da v2.0 Beta.

## ⚠️ Aviso

Este projeto não disponibiliza o jogo completo, uma ROM original ou uma cópia integral da RomFS. É necessário preparar separadamente uma instalação compatível do TriAevum utilizando os arquivos legítimos do jogo.

Projeto de fãs, sem afiliação oficial com a Nintendo. *The Legend of Zelda* e demais propriedades relacionadas pertencem aos respectivos titulares.

