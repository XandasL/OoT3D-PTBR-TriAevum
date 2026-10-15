# The Legend of Zelda: Ocarina of Time 3D — Tradução PT-BR para TriAevum

Port da tradução brasileira de **The Legend of Zelda: Ocarina of Time 3D** para execução através do **TriAevum**.

> **Versão atual: v1.2.1 para TriAevum v0.8.0-beta.1c.** Windows x64 com tradução comum e HD opcional. Linux x86_64 experimental, com validação funcional no jogo pendente. A v1.0.0 permanece disponível para TriAevum v0.6.0-alpha.2c.

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


## v1.2.1 — compatibilidade com TriAevum beta.1c

A versão 1.2.1 está disponível na [página de downloads e tutorial](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.1). Windows x64 inclui o componente HD opcional para TriAevum v0.8.0-beta.1c; Linux mantém a tradução comum e a validação funcional no jogo pendente.

A composição testada usa **Henriko Magnifico + texturas 4K do TopScreen + UI/MENU 4K TRADUZIDA PT-BR + PS5 LAYOUT**. Os packs continuam externos e pertencem aos respectivos autores. [Créditos e links completos](installer/TEXTURAS_CREDITOS.md).

São 71 correspondências de texturas: 13 menus/HUD e 58 adicionais de áreas, bosses e outros gráficos. O componente corrige o carregamento do HUD/menus e adapta hashes alterados pela tradução comum. Não há certificação de cobertura total. [Instalação e remoção do HD](installer/HD_INTEGRACAO.md).

1. Prepare a beta.1c pelo Forge em uma pasta nova e instale a tradução comum com a v1.2.1.
2. Mescle os packs externos, feche o jogo e use **Adicionar texturas HD (Windows 0.8)**.
3. Selecione `user/load/textures/0004000000033500`, a pasta que contém `pack.json`.
4. Abra **TriAevum-PTBR-HD.exe** diretamente. O executável original e seus saves são preservados.

Para atualizar uma instalação HD anterior, remova esse componente pelo instalador anterior antes de instalar a nova versão. Os downloads oferecem um ZIP por plataforma e o código-fonte correspondente em um pacote opcional separado. O ZIP do usuário contém instalador, instruções, créditos e licenças, sem a pasta `runtime-HD`. Os hashes estão na descrição da release.

## 📥 Downloads da v1.2.1

| Plataforma | Download |
| --- | --- |
| Windows x64 — tradução comum + HD opcional | [Baixar Windows](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.2.1/OoT3D_PTBR_TriAevum_v1.2.1_Windows-x64_HD.zip) |
| Linux AppImage — tradução comum, experimental | [Baixar Linux AppImage](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.2.1/OoT3D_PTBR_TriAevum_v1.2.1_Linux-x86_64-AppImage.zip) |
| Linux Flatpak — tradução comum, experimental | [Baixar Linux Flatpak](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.2.1/OoT3D_PTBR_TriAevum_v1.2.1_Linux-x86_64-Flatpak.zip) |

**Para jogar, baixe apenas o ZIP do seu sistema.** [Código-fonte HD correspondente](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.2.1/OoT3D_PTBR_TriAevum_v1.2.1_Fontes-HD.zip) — gratuito e opcional para jogar.

### Versão anterior — v1.2.0

Para TriAevum v0.8.0-beta.1, mantenha a [v1.2.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.0). O EXE HD antigo não deve ser copiado para a beta.1c.

### Versão anterior — v1.1.0

**Versão anterior:** [Notas e downloads da v1.1.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.1.0).

| Plataforma / instalação do TriAevum | Download |
| --- | --- |
| Windows x64 — testado | [Baixar instalador Windows](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.1.0/OoT3D_PTBR_TriAevum_v1.1.0_Windows-x64.zip) |
| Linux x86_64 — TriAevum AppImage (experimental) | [Baixar instalador para AppImage](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.1.0/OoT3D_PTBR_TriAevum_v1.1.0_Linux-x86_64-AppImage.zip) |
| Linux x86_64 — TriAevum Flatpak (experimental) | [Baixar instalador para Flatpak](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/1.1.0/OoT3D_PTBR_TriAevum_v1.1.0_Linux-x86_64-Flatpak.zip) |

> **Linux:** os pacotes foram compilados e passaram pelos autotestes, mas ainda **não foram validados funcionalmente dentro do jogo**. Os ZIPs Linux contêm o instalador executável para Linux e instruções específicas de localização dos dados; **não** são pacotes nativos .AppImage ou .flatpak.

### Versão anterior — v1.0.0

Para **TriAevum v0.6.0-alpha.2c (Windows x64)**, utilize a versão validada anteriormente:

[Baixar v1.0.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/download/v1.0.0/OoT3D_PTBR_TriAevum_v1.0.zip) · [Notas da versão](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v1.0.0)

### Instalação da v1.1.0

1. Prepare o jogo normalmente pelo **TriAevum Forge v0.8.0-beta.1**.
2. Feche o jogo e o Forge.
3. Baixe o ZIP correspondente ao sistema e extraia seu conteúdo.
4. Execute o instalador. No Linux, conceda permissão de execução se necessário e selecione a pasta de dados preparada pelo Forge.
5. Clique em **Verificar status**. Se a instalação for reconhecida como compatível, clique em **Instalar tradução**.
6. Inicie o jogo normalmente.

O instalador verifica a compatibilidade antes de alterar os arquivos e mantém backups para restauração. **Não apague os backups** enquanto desejar poder restaurar o original. Consulte o `LEIA-ME.txt` incluído no pacote.

## 🔄 Restaurar o jogo original

Abra o mesmo instalador e escolha **Restaurar original**. O instalador utiliza os backups criados durante a instalação para desfazer as alterações.

**Não apague os backups criados pelo instalador enquanto desejar manter a opção de restauração.**

## 🎮 Compatibilidade

A versão anterior v1.0.0 foi validada com a estrutura do **TriAevum v0.6.0-alpha.2c para Windows x64** utilizada durante o desenvolvimento.

O port leva em consideração a adaptação USA → EUR feita pelo runtime e possui correção específica para preservar o funcionamento de **TopScreen / Single Screen** com a interface traduzida.

**v1.1.0:** TriAevum **v0.8.0-beta.1**, com Windows x64 testado e Linux x86_64 ainda experimental. **v1.0.0:** TriAevum **v0.6.0-alpha.2c** no Windows x64. Não presuma compatibilidade com outras versões.

### Base histórica testada na v1.0.0 / hashes de referência

A instalação utilizada no desenvolvimento e na validação da tradução foi criada a partir de uma cópia **USA (En/Fr/Es)** de *The Legend of Zelda: Ocarina of Time 3D*. Estas hashes servem apenas para conferência de uma cópia obtida legalmente pelo próprio usuário; este repositório não fornece nem aponta downloads do jogo.

**Arquivo-base usado na validação:**

- SHA-256: `6510135ae6c385994fccdf525824abdf6be7aa473ed11ef5a07ff4601b7b3288`
- MD5: `0984d51928ce80623354c820c74f3a16`

**RomFS limpo gerado/adaptado pelo TriAevum v0.6.0-alpha.2c:**

- Tamanho: `473.522.176 bytes`
- SHA-256: `011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99`

O instalador v1.0.0 valida o RomFS compatível antes de aplicar a tradução.

## ✅ Histórico de validação da v1.0.0

Na versão anterior v1.0.0, foram testados no executável final:

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

Créditos da tradução PT-BR original:

- **Projeto Zelda Brasil – Heroes of Time**
- **Catatau Game Dev e Traduções**
- **Elite dos Quatro Traduções**
- **JumpManClub Brasil Traduções**
- **TRADU-ROMS**

Os créditos completos e informações adicionais estão em [`CREDITOS.md`](CREDITOS.md) e no `LEIA-ME.txt` incluído no download.

O port e a distribuição da tradução completa são realizados com autorização do responsável pela tradução, mantendo os devidos créditos dentro e fora do jogo.

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
- [x] Teste completo do executável
- [x] Release pública v1.0.0 (TriAevum v0.6.0-alpha.2c Windows x64)
- [x] Release pública v1.1.0 (TriAevum v0.8.0-beta.1; Windows x64 testado)
- [x] Builds Linux x86_64 separadas por instalação AppImage / Flatpak
- [ ] Validação funcional no Linux

## 🔧 Port e instalador

**XandasL** — port para TriAevum, adaptação técnica e empacotamento do instalador.
