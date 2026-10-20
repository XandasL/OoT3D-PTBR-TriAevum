# Tradução PT-BR para TriAevum — v1.3.0

Atualização do instalador da tradução brasileira de **The Legend of Zelda:
Ocarina of Time 3D**, com suporte ao **TriAevum v0.8.0-beta.1.1** e escolha
entre a fonte original e a **fonte HD 128** desenvolvida para este projeto.

## ✨ Novidades

- Tradução completa: diálogos, mensagens e texturas nativas em português,
  com 112 recursos originais e 14 espelhos de menus para a base EUR.
- Escolha entre **Original do jogo** e **Fonte HD 128**, alterável depois
  sem reinstalar toda a tradução.
- Recuperação automática: se a instalação for interrompida, basta clicar
  novamente em **Instalar / aplicar fonte**. O instalador verifica e recupera
  a operação anterior antes de continuar com a escolha atual.
- **Restaurar original** também retoma operações interrompidas e recupera
  o perfil e a fonte anteriores.
- Instalação simplificada: utiliza o executável original do TriAevum.
  Saves, configurações gráficas e packs de terceiros são preservados.

## 📦 Qual arquivo baixar?

| Plataforma | Arquivo | Conteúdo |
| --- | --- | --- |
| **Windows x64** | `OoT3D_PTBR_TriAevum_v1.3.0_Windows-x64.zip` | Instalador, instruções e créditos |
| **Linux / TriAevum AppImage** | `OoT3D_PTBR_TriAevum_v1.3.0_Linux-x86_64-AppImage.zip` | Instalador, instruções e créditos |
| **Linux / TriAevum Flatpak** | `OoT3D_PTBR_TriAevum_v1.3.0_Linux-x86_64-Flatpak.zip` | Instalador, instruções e créditos |
| **Henriko 5.0a — opcional** | `OoT3D_PTBR_TriAevum_v1.3.0_Compatibilidade-Henriko.zip` | `pack.json` de compatibilidade e instruções |

**Para instalar a tradução, baixe somente o ZIP do seu sistema.** Cada pacote
contém apenas o instalador, `LEIA-ME.txt` e `CREDITOS.txt`. A tradução e a
cobertura da fonte HD já estão embutidas no instalador.

Os ZIPs Linux usam o mesmo instalador, executado fora do AppImage/Flatpak do
jogo. Não são novos pacotes do TriAevum. Relatórios de teste, fontes de build
e arquivos temporários não acompanham os downloads de instalação.

## 🎮 Compatibilidade e validação

| Recurso | Situação |
| --- | --- |
| TriAevum v0.8.0-beta.1.1 Windows x64 | Instalação, troca de fonte, recuperação e restauração verificadas com dados reais em cópia isolada |
| Fonte HD 128 | Cobertura aprovada, com métricas nativas preservadas |
| Windows e Linux | 24 testes automatizados e autoteste dos instaladores empacotados |
| Linux AppImage / Flatpak | Validação funcional dentro do jogo ainda pendente |

O RomFS traduzido e a cobertura HD permanecem iguais aos já conferidos no
jogo na beta.1.1. A nova recuperação automática foi exercitada com interrupções
simuladas, inclusive após ativação do perfil e durante a restauração.

Para versões anteriores do TriAevum, utilize a release correspondente.
Não presuma compatibilidade com bases diferentes.

## 🛠️ Tutorial — instalar a tradução

1. Prepare o jogo normalmente pelo **TriAevum Forge beta.1.1** e confira se ele abre.
2. Faça uma cópia dos seus saves e feche o jogo e o Forge.
3. Extraia o ZIP correspondente ao seu sistema.
4. **Windows:** abra o instalador `.exe`; ele pode ficar ao lado de `TriAevum.launch.json`.
5. **Linux:** conceda permissão de execução ao instalador (`chmod +x`) e abra-o.
6. Use **Selecionar pasta do TriAevum** se necessário. Escolha a pasta que contém
   `TriAevum.launch.json` e `data`, não o arquivo AppImage ou a pasta `/app` do Flatpak.
7. Clique em **Verificar status**, escolha **Original do jogo** ou **Fonte HD 128**
   e clique em **Instalar / aplicar fonte**.
8. Aguarde a conclusão e abra o **TriAevum original** normalmente.

**Não apague os backups e recibos gerados pelo instalador** enquanto desejar
restaurar a instalação anterior.

## 🖼️ Texturas HD — opcionais

O instalador traduz as texturas nativas do jogo. Quem não usa pack HD continua
com esses elementos em português.

O **Henriko Magnifico — OOT3D 4K 5.0a (4K)** pode ser instalado separadamente
pelo próprio carregador de texturas do TriAevum. [Página do autor](https://www.henrikomagnifico.com/).
As imagens do Henriko permanecem no idioma do pack; os diálogos e as mensagens
da tradução continuam em português, com a fonte escolhida.

Para o Henriko original 5.0a, o download opcional de compatibilidade fornece
**71 aliases** para que suas imagens substituam os recursos nativos traduzidos:

1. Feche o jogo e preserve uma cópia do `pack.json` original do Henriko.
2. Extraia o ZIP opcional e copie seu `pack.json` para a raiz do pack, ao lado
   das pastas `UI`, `ENVIRONMENT` etc.
3. No TriAevum, ative as texturas personalizadas e selecione essa raiz:
   `user/load/textures/0004000000033500`, onde está o `pack.json`.
4. Abra o jogo novamente. Para desfazer, restaure o `pack.json` anterior.

Essa compatibilidade foi validada para o pack original indicado. Se seu
`pack.json` contém outros ajustes, preserve-os e mescle apenas os aliases.
O instalador não aplica esse arquivo automaticamente. Não há pack de imagens,
layout PlayStation, importador SingleScreen ou runtime modificado neste download.

## 🔄 Atualização e restauração

- **Vindo de uma versão antiga:** restaure a tradução e remova eventuais
  componentes HD com o instalador que os aplicou antes de migrar. Para uma
  nova versão do TriAevum, prefira uma pasta preparada pelo Forge correspondente.
- **Quer trocar somente a fonte?** Selecione a outra opção e clique em
  **Instalar / aplicar fonte** novamente.
- **A operação foi interrompida?** Abra o instalador e tente instalar novamente.
  A recuperação é automática para estados verificáveis.
- **Quer remover a tradução?** Use **Restaurar original** com o jogo fechado.

Se arquivos registrados forem alterados externamente ou estiverem ilegíveis,
o instalador preserva os dados e interrompe a operação para conferência.
Não apague backups para forçar uma nova instalação.

## ℹ️ Limites conhecidos

- Esta distribuição é uma **pré-release**, com compatibilidade declarada para beta.1.1.
- A execução do jogo no Linux ainda precisa de validação.
- Nem todos os menus e cenários foram conferidos visualmente.
- Os 71 aliases não representam cobertura HD de todas as imagens. Alguns
  elementos próprios do SingleScreen dependem do atlas HD importado pelo Forge.
- Os testes de recuperação não certificam falhas físicas de disco ou energia.

## 🇧🇷 Créditos

**Tradução PT-BR original:** Projeto Zelda Brasil — Heroes of Time, Catatau
Game Dev e Traduções, Elite dos Quatro Traduções, JumpManClub Brasil Traduções
e TRADU-ROMS.

**Port, adaptação e instalador para TriAevum:** **XandasL**.

**Recursos externos opcionais:** Henriko Magnifico; M-1 / rlgcarrot e
colaboradores do [SingleScreen / TopScreen](https://gamebanana.com/mods/695893).
Os respectivos packs e condições permanecem com seus autores.

Projeto de fãs, sem afiliação oficial com a Nintendo. **Nenhuma ROM ou cópia
do jogo está incluída.**
