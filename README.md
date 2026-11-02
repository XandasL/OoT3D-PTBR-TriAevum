# The Legend of Zelda: Ocarina of Time 3D — Tradução PT-BR para TriAevum

Adaptação para **TriAevum** da tradução brasileira de *The Legend of Zelda: Ocarina of Time 3D*, com diálogos, menus e texturas nativas traduzidas.

> **Próxima versão: v2.0 Beta — TriAevum v0.8.0-beta.1.2 (Windows).** O pacote portátil já foi testado pelo autor e está em preparação para publicação. **Última release publicada: [v1.3.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.3.0).** Não confunda esta versão em desenvolvimento com um download já publicado.

## 🇧🇷 Sobre a tradução

O projeto adapta uma tradução PT-BR existente, com autorização de seus responsáveis. A tradução preserva diálogos, nomes de locais, mensagens, menus e recursos gráficos nativos. O port também adapta os arquivos necessários ao ambiente EUR utilizado pelo TriAevum.

## ✨ v2.0 Beta — o que muda

- **Mod O3RO completo:** 126 substituições, incluindo os recursos gráficos nativos traduzidos.
- **Instalação simples:** ZIP portátil com `Ativar-PTBR.cmd` e `Ativar-PTBR.ps1`, sem instalador executável próprio.
- **Arquivos originais preservados:** o mod utiliza um overlay virtual; não modifica o executável do TriAevum nem a RomFS original.
- **Integridade e backup:** verificação SHA-256 do O3RO e cópia de segurança do perfil de inicialização antes da alteração.
- **Créditos no pacote:** o `LEIA-ME.txt` contém os créditos e as informações de autorização da tradução.

O pacote da v2.0 Beta não inclui imagens HD, atlas TopScreen ou recursos de terceiros. **A compatibilidade com pacotes de texturas personalizadas não é garantida**, pois algumas substituições podem deixar de carregar quando seus hashes diferem dos recursos nativos traduzidos.

## 📥 Download e compatibilidade

| Versão | TriAevum | Situação |
| --- | --- | --- |
| **v2.0 Beta** | **v0.8.0-beta.1.2 (Windows)** | Candidata testada; publicação pendente |
| [v1.3.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.3.0) | v0.8.0-beta.1.1 | Release anterior |
| [v1.2.1](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.1) | v0.8.0-beta.1c | Release anterior |
| [v1.2.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.0) | v0.8.0-beta.1 | Release anterior |
| [v1.1.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.1.0) | v0.8.0-beta.1 | Release anterior |
| [v1.0.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v1.0.0) | v0.6.0-alpha.2c | Release anterior |

Não utilize os arquivos ou instaladores de uma versão com outra base do TriAevum sem verificar a compatibilidade. As versões antigas possuem métodos de instalação diferentes e continuam disponíveis em suas próprias páginas.

## 🛠️ Instalação da v2.0 Beta (após disponibilização)

1. Prepare o jogo pelo **TriAevum Forge v0.8.0-beta.1.2** e feche o jogo e o Forge.
2. Extraia `OoT3D-PTBR-v2.0-Beta.zip` na pasta raiz da instalação, preservando as subpastas.
3. Execute `Ativar-PTBR.cmd`.
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

## 📌 Desenvolvimento

A preparação da v2.0 Beta está na branch [`experiment/native-romfs-overlay-ptbr`](https://github.com/XandasL/OoT3D-PTBR-TriAevum/tree/experiment/native-romfs-overlay-ptbr). As notas da candidata estão em [RELEASE_v2.0_BETA_DRAFT.md](https://github.com/XandasL/OoT3D-PTBR-TriAevum/blob/experiment/native-romfs-overlay-ptbr/experiments/portable-v2-clean/RELEASE_v2.0_BETA_DRAFT.md) e os arquivos-fonte permanecem na branch experimental.
