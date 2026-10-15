# Texturas HD traduzidas — instalador 1.2.1

O componente HD é opcional e destinado ao **TriAevum v0.8.0-beta.1c Windows x64**. A tradução comum deve estar instalada e validada antes de adicionar o HD.

## Instalação

1. Prepare a beta.1c pelo Forge em uma pasta nova e feche jogo e Forge.
2. Abra o instalador 1.2.1, selecione essa pasta e instale a tradução comum.
3. Mescle os packs externos: Henriko Magnifico, TopScreen 4K e UI/MENU 4K PT-BR + PS5 LAYOUT. [Créditos e downloads](TEXTURAS_CREDITOS.md).
4. Clique em **Adicionar texturas HD** e escolha `user/load/textures/0004000000033500`, a pasta que contém `pack.json`. Uma pasta superior só é aceita quando contém um único pack.
5. Abra **TriAevum-PTBR-HD.exe** diretamente.

O EXE HD é compilado sobre os fontes da beta.1c para manter as correções recentes de TopScreen, menus, gráficos e compatibilidade do plugin. Não copie o EXE HD da versão anterior para a pasta nova. Os saves podem ser copiados da instalação antiga com o jogo fechado.

## Arquivos e restauração

O executável original e seu perfil são preservados. O HD cria um launcher e uma configuração separados, mantendo o novo plugin, os recursos e os caminhos do perfil original. Ele usa a pasta de saves indicada nesse perfil.

Os 71 aliases em `UI/PTBR_HASHES` correspondem a 13 menus/HUD e 58 gráficos de áreas, bosses e outros recursos. As imagens originais do pack permanecem intactas. Arquivos idênticos preexistentes são preservados durante a remoção; conflitos desconhecidos são recusados antes de gravar.

O recibo da transação fica em `data/mods/ptbr-hd/installation.json`. Falhas de gravação desfazem a transação. **Remover suporte HD** desfaz os arquivos pertencentes ao componente e mantém suas preferências. Não apague recibos ou backups enquanto precisar da restauração. Arquivos modificados depois da instalação devem ser verificados antes da remoção.

**Restaurar original** remove primeiro o suporte HD registrado e depois restaura a tradução comum a partir dos backups. Para remover um componente de uma versão antiga, use o instalador que o instalou.

## Aviso da Navi e fonte

O instalador recompõe somente o espaço do texto `Navi` no alias traduzido do atlas HD. O PNG original do pack não é alterado. Um alias antigo que seja cópia exata do PNG validado pode ser atualizado com backup; a remoção devolve esse alias ao estado anterior.

A fonte nativa compatível com a cobertura HD do TriAevum é preservada. Os aliases de caracteres da tradução são normalizados para `ã/õ/Ã/Õ`, mantendo os offsets. A fonte do perfil TopScreen permanece em 1024×256. O atlas de dicas em vídeo sem PNG correspondente mantém a resolução nativa. A cobertura total dos gráficos não foi certificada.

## Pacote e código-fonte

O ZIP do usuário contém instalador, instruções, créditos e licenças. Os packs de texturas são externos. O pacote opcional `OoT3D_PTBR_TriAevum_v1.2.1_Fontes-HD.zip` oferece os fontes exatos do runtime e seu patch na mesma release. O insumo técnico do Actions permanece em draft interno separado.

Os fontes e o patch não ficam embutidos no instalador; são oferecidos somente no download separado. Os binários continuam sendo verificados pelos mesmos hashes antes da instalação.

As compilações Linux incluem a tradução comum; sua validação funcional no jogo continua pendente. [Build da 1.2.1](BUILD_V1.2.1.md).
