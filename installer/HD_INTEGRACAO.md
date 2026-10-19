# Texturas HD traduzidas — instalador 1.2.1

O componente HD é opcional e destinado ao **TriAevum v0.8.0-beta.1.1 Windows x64**. A tradução comum deve estar instalada e validada antes de adicionar o HD. O componente recusa executáveis de outras versões.

## Instalação

1. Prepare a beta.1.1 pelo Forge em uma pasta nova e confirme que o jogo abre; depois feche o jogo e o Forge.
2. Abra o instalador 1.2.1, selecione essa pasta e instale a tradução comum.
3. Mescle os packs externos: Henriko Magnifico, TopScreen 4K e UI/MENU 4K PT-BR + PS5 LAYOUT. [Créditos e downloads](TEXTURAS_CREDITOS.md).
4. Clique em **Adicionar texturas HD (Windows 0.8)** e escolha `user/load/textures/0004000000033500`, a pasta que contém `pack.json`. Uma pasta superior só é aceita quando contém um único pack.
5. Abra **TriAevum-PTBR-HD.exe** diretamente.

## Como funciona o launcher HD

A beta.1.1 já tem o resolvedor de texturas personalizadas para a interface. Para evitar misturar o executável HD antigo, compilado para a beta.1c, com o runtime e o plugin da beta.1.1, o instalador cria `TriAevum-PTBR-HD.exe` como uma **cópia byte a byte do `TriAevum.exe` validado dessa instalação**. Não baixa, não distribui e não substitui o executável oficial nem as DLLs da instalação.

Antes de qualquer gravação, o instalador confere o SHA-256 do executável e das dependências, valida os 112 recursos da tradução, os 14 espelhos de menu, as 126 operações e a integridade do RomFS. O launcher usa um perfil e uma configuração separados para apontar ao pack de texturas escolhido; o executável original, o perfil original e as DLLs ficam intactos. O caminho de saves do perfil original é preservado.

## Compatibilidade do HUD PS com SingleScreen 3.0

Na beta.1.1, o TopScreen desenha os botões do HUD a partir do atlas `custom_ui01` do SingleScreen 3.0, em vez das regiões correspondentes de `menu_top_parts00` usadas pelo layout PS5. Por isso, apenas substituir os aliases HD nativos não garante que todos os símbolos sejam apresentados no HUD.

O componente HD agora compõe nove regiões específicas do atlas HD com as imagens PS5 verificadas de `menu_top_parts00`: X vira triângulo, Y vira quadrado, B mantém o círculo, e ZR/ZL passam a R1/L1 nas posições do HUD. O mapa cobre também as cópias separadas de X/Y usadas nas legendas da tela de inventário e as regiões R1/L1 usadas pelas dicas laterais. Os círculos de fundo, D-pad, itens, contadores e demais regiões do atlas não são alterados por esse mapeamento.

Se o atlas HD estiver dentro do pack escolhido, a imagem composta é aplicada ali com backup transacional. Caso contrário, o instalador gera uma cópia própria em `data/mods/ptbr-hd/ui_atlas_hd.png` e redireciona somente o perfil HD para ela; o atlas importado pelo Forge e o executável oficial permanecem intactos. **A alteração é reversível**, e o recibo registra o arquivo criado/substituído para que a remoção restaure o estado anterior.

Essa composição agora possui testes automatizados para as posições do HUD e do menu de inventário, preservação dos pixels fora das células e restauração. A verificação definitiva de aparência depende também de teste visual dentro do jogo; esta branch continua sendo uma build de teste.

## Arquivos e restauração

Os 71 aliases em `UI/PTBR_HASHES` correspondem a 13 menus/HUD e 58 gráficos de áreas, bosses e outros recursos. As imagens originais do pack permanecem intactas. Arquivos idênticos preexistentes são preservados durante a remoção; conflitos desconhecidos são recusados antes de gravar.

O recibo da transação fica em `data/mods/ptbr-hd/installation.json`. Falhas de gravação desfazem a transação. **Remover suporte HD** desfaz os arquivos pertencentes ao componente e mantém suas preferências. Não apague recibos ou backups enquanto precisar da restauração. Arquivos modificados depois da instalação devem ser verificados antes da remoção.

**Restaurar original** remove primeiro o suporte HD registrado e depois restaura a tradução comum a partir dos backups. Para remover um componente HD de uma versão antiga, use o instalador que o instalou.

## Aviso da Navi e fonte

O instalador recompõe somente o espaço do texto `Navi` no alias traduzido do atlas HD. O PNG original do pack não é alterado. Um alias antigo que seja cópia exata do PNG validado pode ser atualizado com backup; a remoção devolve esse alias ao estado anterior.

A fonte nativa compatível com a cobertura HD do TriAevum é preservada. Os aliases de caracteres da tradução são normalizados para `ã/õ/Ã/Õ`, mantendo os offsets. A fonte do perfil TopScreen permanece em 1024×256. O atlas de dicas em vídeo sem PNG correspondente mantém a resolução nativa. A cobertura total dos gráficos não foi certificada.

## Pacote e código-fonte

O instalador não inclui executável ou DLL do TriAevum. O launcher HD é copiado da instalação validada no momento da instalação. O código-fonte correspondente ao runtime nativo está disponível no repositório oficial: https://github.com/coccofresco/TriAevum/tree/v0.8.0-beta.1.1. Os packs de texturas são externos.

As compilações Linux incluem a tradução comum; sua validação funcional dentro do jogo continua pendente e não incluem o componente HD. Consulte [Build da 1.2.1](BUILD_V1.2.1.md).
