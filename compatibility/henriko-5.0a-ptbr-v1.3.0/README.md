# Henriko 5.0a + tradução PT-BR v1.3.0

Arquivo de compatibilidade externo ao instalador, aprovado pelo usuário.
Acrescenta 71 aliases de hashes: associa as texturas nativas traduzidas aos
PNGs originais em inglês do Henriko, sem alterar ou redistribuir imagens.
A fonte original/HD 128 e o RomFS traduzido permanecem inalterados.

1. Feche o jogo.
2. Preserve uma cópia do pack.json do Henriko original 5.0a.
3. Copie este pack.json para a raiz do pack, ao lado de UI, ENVIRONMENT etc.
4. Nas configurações do TriAevum, selecione essa raiz como diretório de texturas,
   e não a pasta user acima dela. Os aliases são lidos do pack.json dessa raiz.
5. Ative as texturas personalizadas e abra o jogo novamente.

Validação: runtime original beta.1.1, RomFS completo PT-BR
26caf9f8ea36c106f7fd8a9c737b09203ce4535d0113d5ba946e917058e8a39b,
1850 frames, inventário e abas Gear/Map/Items em HD. Mantidos os controles
Nintendo, os diálogos PT-BR e a fonte 128. Todas as 71 imagens referenciadas
ficaram byte a byte iguais às do pack original. Outras áreas/menus não foram
todas conferidas visualmente. Metadados originais e opções de hash/flip/mipmap
preservados; nenhum executável ou shader é alterado.

O arquivo pronto foi validado para o pack original Henriko 5.0a fornecido.
Se o seu pack.json já tem outros ajustes, mescle a seção textures preservando
suas opções e aliases. Para desfazer, restaure o pack.json que você guardou.
Com o pack desligado, permanecem as texturas nativas PT-BR da tradução.
