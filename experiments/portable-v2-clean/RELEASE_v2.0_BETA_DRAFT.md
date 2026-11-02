# OoT3D PT-BR v2.0 Beta — TriAevum v0.8.0-beta.1.2

Esta versão da tradução brasileira de **The Legend of Zelda: Ocarina of Time 3D** traz uma instalação mais simples, utilizando o suporte a overlays O3RO do TriAevum. Os diálogos, menus e elementos gráficos nativos traduzidos são preservados, sem necessidade de modificar o executável do jogo ou a RomFS original.

## ✨ Novidades

- **Tradução clássica completa:** 126 substituições O3RO, incluindo textos, menus e recursos gráficos nativos em português brasileiro.
- **Instalação portátil:** basta extrair o ZIP e executar `Ativar-PTBR.cmd`; não há instalador executável compilado.
- **Integração com O3RO:** a tradução é ativada por meio do perfil de inicialização do TriAevum, preservando a RomFS original.
- **Verificação de integridade:** o ativador confere o SHA-256 do arquivo `OoT3D-PTBR.o3ro` antes de modificar o perfil.
- **Backup do perfil:** é criada uma cópia de `data/TriAevum.launch.json` antes da primeira ativação, sem sobrescrever um backup anterior.
- **Créditos completos:** incorporados ao `LEIA-ME.txt` que acompanha o pacote.

## 📦 Download

**Windows — TriAevum v0.8.0-beta.1.2**

Arquivo: `OoT3D-PTBR-v2.0-Beta.zip`

O ZIP contém o ativador CMD/PowerShell, as instruções com os créditos e o mod `data/mods/OoT3D-PTBR/OoT3D-PTBR.o3ro`. Não inclui o executável do TriAevum, a RomFS original ou pacotes de texturas HD de terceiros.

## 🛠️ Como instalar

1. Prepare uma instalação compatível do jogo no **TriAevum Forge v0.8.0-beta.1.2** e confirme que ela inicia normalmente.
2. Feche o jogo e o Forge.
3. Extraia o conteúdo do ZIP **na pasta raiz da instalação do TriAevum**, mantendo a estrutura de diretórios.
4. Execute `Ativar-PTBR.cmd`. O ativador valida o mod, preserva uma cópia do perfil e configura o carregamento do O3RO.
5. Abra o TriAevum normalmente. A tradução estará ativa.

O ativador não altera o executável, a RomFS original, os arquivos de save ou os pacotes de texturas do usuário. Ele modifica somente o perfil de inicialização para adicionar ou atualizar `--romfs-overlay`.

**Atenção:** executar novamente **Prepare and install** no Forge pode recriar o perfil. Se isso acontecer, execute `Ativar-PTBR.cmd` novamente.

## 🎮 Compatibilidade e validação

| Recurso | Situação |
| --- | --- |
| TriAevum v0.8.0-beta.1.2 — Windows | Tradução e ativador testados no jogo pelo autor |
| Overlay O3RO — 126 substituições | Validado; conteúdo da tradução mantido |
| RomFS e executável originais | Preservados |
| Texturas HD / personalizadas | Compatibilidade não garantida |
| Outras versões do TriAevum e Linux | Não validadas nesta distribuição |

### Texturas personalizadas

**A v2.0 Beta foi preparada para a experiência clássica, sem pacotes HD.** Como a tradução substitui texturas nativas, os hashes utilizados pelo carregador de texturas personalizadas podem ser diferentes dos originais. Isso pode impedir que determinados elementos do HUD, menus e outras imagens HD sejam carregados. O ativador não modifica esses pacotes; a compatibilidade com eles não é garantida nesta versão.

## 🔄 Atualização e remoção

Para futuras atualizações, utilize sempre o pacote indicado para a versão correspondente do TriAevum. O O3RO e seu hash são verificados pelo ativador; não substitua arquivos entre versões incompatíveis.

O ativador cria um backup do perfil de inicialização, mas **não oferece um comando de desinstalação**. Para desativar o mod, feche o jogo, remova o argumento `--romfs-overlay` e seu caminho do arquivo `data/TriAevum.launch.json`, ou restaure o backup do perfil se ele corresponder à configuração que deseja recuperar. Não apague os saves nem a RomFS.

## 🇧🇷 Créditos

**Tradução PT-BR original:** Projeto Zelda Brasil – Heroes of Time; Catatau Game Dev e Traduções; Elite dos Quatro Traduções; JumpManClub Brasil Traduções; TRADU-ROMS.

**Port e adaptação para TriAevum:** XandasL.

A distribuição da tradução é realizada com autorização do responsável pela tradução original, mediante manutenção dos créditos. Os agradecimentos e o aviso de autoria encontram-se integralmente no `LEIA-ME.txt`.

Projeto de fãs, sem afiliação oficial com a Nintendo. *The Legend of Zelda* e demais propriedades relacionadas pertencem aos seus respectivos titulares.

---

**Estado:** texto preparado para uma **pré-release (Beta)**. Esta é uma proposta de descrição; a release ainda não foi publicada.
