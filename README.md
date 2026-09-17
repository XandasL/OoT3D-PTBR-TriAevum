# The Legend of Zelda: Ocarina of Time 3D — Tradução PT-BR para TriAevum

Port da tradução brasileira de **The Legend of Zelda: Ocarina of Time 3D** para execução através do **TriAevum**.

> **Status: v1.0 concluída e validada.** O instalador final em `.exe` foi testado no ciclo completo de instalação, restauração e nova instalação, incluindo execução da tradução dentro do jogo.

## 🇧🇷 Sobre o projeto

Este projeto adapta uma tradução PT-BR já existente para a estrutura utilizada pelo TriAevum. O port preserva textos, menus, interface e recursos gráficos traduzidos e inclui os ajustes necessários para o runtime do TriAevum.

A tradução inclui:

- diálogos e textos em PT-BR;
- nomes de locais, mensagens e placas;
- menus e interface;
- texturas e elementos gráficos traduzidos;
- tela de título e demais recursos da tradução original;
- adaptação do slot USA para o layout EUR utilizado pelo runtime;
- compatibilidade com **TopScreen / Single Screen**.

## 📥 Download

O instalador oficial da **v1.0** será disponibilizado na seção **Releases** deste repositório.

O arquivo de distribuição é um executável único:

`OoT3D_PTBR_TriAevum_v1.0.exe`

Não é necessário instalar Python nem copiar scripts ou pastas de desenvolvimento.

## 🛠️ Instalação

1. Tenha uma instalação funcional e compatível do TriAevum para Ocarina of Time 3D.
2. Baixe `OoT3D_PTBR_TriAevum_v1.0.exe` pela seção **Releases**.
3. Coloque o executável na pasta principal do TriAevum, ao lado de `TriAevum.launch.json`.
4. Feche o jogo e o TriAevum antes de modificar os arquivos.
5. Abra o instalador e clique em **Verificar status**.
6. Clique em **Instalar tradução** e aguarde a conclusão.
7. Inicie o jogo normalmente pelo TriAevum.

O instalador valida a instalação antes de aplicar o port e cria backups dos arquivos necessários.

## 🔄 Restaurar o jogo original

Abra o mesmo instalador e escolha **Restaurar original**. O instalador utiliza os backups criados durante a instalação para desfazer as alterações.

**Não apague os backups criados pelo instalador enquanto desejar manter a opção de restauração.**

## 🎮 Compatibilidade

A v1.0 foi validada com a estrutura do **TriAevum v0.6.0-alpha.2c para Windows x64** utilizada durante o desenvolvimento.

O port leva em consideração a adaptação USA → EUR feita pelo runtime e possui correção específica para preservar o funcionamento de **TopScreen / Single Screen** com a interface traduzida.

Outras versões do TriAevum podem exigir nova validação.

## ✅ Validação da v1.0

Foram testados no executável final:

- detecção da instalação do TriAevum;
- verificação do estado do RomFS;
- instalação completa da tradução;
- textos, menus, HUD e recursos gráficos dentro do jogo;
- TopScreen / Single Screen;
- criação e utilização dos backups;
- restauração para o RomFS original;
- nova instalação após restauração;
- execução independente das antigas pastas de desenvolvimento.

## ❤️ Créditos e autorização

Este projeto é um **port para TriAevum de uma tradução PT-BR existente**. A tradução original não foi criada por este repositório.

Os créditos da tradução e do port estão em [`CREDITOS.md`](CREDITOS.md) e também são mantidos no instalador.

O port e a distribuição da tradução completa são realizados com autorização do responsável pela tradução, condicionados à preservação dos devidos créditos dentro e fora do jogo.

## ⚠️ Aviso

Este repositório **não distribui ROM, dump ou cópia de The Legend of Zelda: Ocarina of Time 3D**.

O usuário deve possuir separadamente os arquivos compatíveis necessários para executar o jogo. O projeto distribui somente os componentes do port/tradução cuja distribuição foi autorizada.

**The Legend of Zelda** e demais propriedades relacionadas pertencem aos seus respectivos detentores. Este é um projeto de fãs, sem afiliação oficial com a Nintendo.

## 📌 Estado do projeto

- [x] Port dos textos PT-BR
- [x] Port dos recursos gráficos
- [x] Menus PT-BR no runtime EUR
- [x] Compatibilidade com TopScreen / Single Screen
- [x] Instalação, backup e restauração
- [x] Interface gráfica
- [x] Executável único para Windows
- [x] Teste completo do executável v1.0
- [ ] Publicação do binário na Release v1.0

## 🔧 Port e instalador

**XandasL** — port para TriAevum, adaptação técnica e empacotamento do instalador.
