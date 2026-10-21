# Tradução PT-BR para TriAevum — v1.3.0 (pré-release)

Instalador da tradução brasileira de **The Legend of Zelda: Ocarina of Time 3D** para o **TriAevum v0.8.0-beta.1.1**. Esta pré-release permanece em rascunho enquanto são concluídas as verificações de distribuição.

## Novidades e testes

- Tradução PT-BR completa, incluindo diálogos, mensagens, HUD, menus e texturas nativas: **112 recursos de origem** e **14 espelhos de menus EUR** (126 operações).
- Escolha entre **Original do jogo** e **Fonte HD 64**. A fonte HD 64 mantém caracteres e métricas nativas, e o usuário confirmou, em seus testes finais no Windows, boa fluidez, ausência de engasgos e caixas de diálogo aparecendo normalmente.
- **TriAevum original e intacto:** não modifica `TriAevum.exe`, shaders, FPS, resolução ou configurações gráficas.
- Instalação e restauração com backups, recibos, validação e recuperação de operações interrompidas.
- **Compatibilidade opcional com Henriko original 5.0a incluída em cada ZIP**, com `pack.json` e instruções na pasta `Henriko-5.0a-PTBR/`. Os 71 aliases permitem ao pack HD identificar texturas nativas traduzidas; as imagens do Henriko não são redistribuídas. O instalador **não aplica nem altera** o pack automaticamente.

## Qual arquivo baixar?

| Plataforma | Arquivo |
| --- | --- |
| **Windows x64** | `OoT3D_PTBR_TriAevum_v1.3.0_Windows-x64.zip` |
| **Linux x86_64 / TriAevum AppImage** | `OoT3D_PTBR_TriAevum_v1.3.0_Linux-x86_64-AppImage.zip` |
| **Linux x86_64 / TriAevum Flatpak** | `OoT3D_PTBR_TriAevum_v1.3.0_Linux-x86_64-Flatpak.zip` |

**Basta baixar um único ZIP**, correspondente ao sistema: cada um já contém o instalador, `LEIA-ME.txt`, `CREDITOS.txt` e `Henriko-5.0a-PTBR/pack.json` com seu guia. **Não é necessário baixar um ZIP separado para Henriko.**

O instalador Linux é executado fora do AppImage/Flatpak do jogo; os ZIPs não incluem o TriAevum. A compilação e o autoteste foram concluídos com sucesso em Windows e Linux, mas **o funcionamento dentro do jogo no Linux ainda não foi confirmado**.

## Como instalar

1. Prepare e teste o jogo usando o Forge do **TriAevum beta.1.1**. Faça uma cópia de segurança dos saves. Feche o jogo e o Forge.
2. Extraia o ZIP correspondente à sua plataforma.
3. **Windows:** execute o instalador `.exe`. **Linux:** conceda permissão de execução ao arquivo instalador (`chmod +x`) e execute-o fora do AppImage/Flatpak.
4. Selecione a pasta preparada pelo Forge que contém `TriAevum.launch.json` e `data`. Não selecione o arquivo AppImage nem a pasta `/app` do Flatpak.
5. Clique em **Verificar status**, escolha **Original do jogo** ou **Fonte HD 64** e use **Instalar / aplicar fonte**.
6. Após a conclusão, abra normalmente o **TriAevum original**. É possível trocar a fonte depois pelo mesmo instalador sem reinstalar a tradução.
7. Para reverter a tradução, feche o jogo e utilize **Restaurar original**. **Preserve os backups e recibos.**

**Migrando de instalação antiga:** restaure primeiro a versão anterior com o instalador correspondente. Não aplique a nova versão sobre dados modificados por outros instaladores.

## Texturas HD Henriko 5.0a — opcional

O jogo funciona sem pacote HD adicional; as texturas nativas traduzidas seguem em português. Para integrar o **pack original Henriko Magnifico 5.0a**:

1. Instale o pack adquirido/baixado do autor pelos meios indicados por ele. Feche o jogo.
2. Faça backup do `pack.json` existente na **raiz do pack Henriko original 5.0a**, ao lado das pastas `UI`, `ENVIRONMENT` etc.
3. No ZIP do nosso instalador, abra `Henriko-5.0a-PTBR/` e copie o `pack.json` incluído para a raiz do pack Henriko.
4. Nas configurações do TriAevum, ative texturas personalizadas e selecione **a raiz do pack** que contém o `pack.json` (por exemplo, `user/load/textures/0004000000033500`), não a pasta `user` acima dela.
5. Reabra o jogo. Para desfazer, restaure o `pack.json` que foi guardado.

Se seu `pack.json` já contém outros ajustes, **não sobrescreva diretamente**; preserve esses ajustes e mescle os aliases. O arquivo é específico para o **Henriko original 5.0a** testado, não para versões alteradas do pack. A compatibilidade oferece **71 associações**, não uma tradução dos PNGs HD do autor. Seus elementos gráficos permanecem como distribuídos pelo autor.

## Status, limites e segurança

- **Windows x64 / TriAevum beta.1.1:** usuário relatou que os testes finais com fonte HD 64 e tradução PT-BR estão funcionando bem.
- **Windows e Linux x64:** build, testes de segurança e autotestes do instalador aprovados. **Linux no jogo:** teste funcional pendente.
- Nem todos os cenários e menus foram verificados visualmente.
- Backups e recuperação são conservadores; não há garantia contra falha física de disco ou energia.
- Nenhuma ROM, executável do TriAevum, saves, PNGs do Henriko ou pacote comercial está incluído.
- Para versões diferentes de TriAevum, use o instalador compatível com a versão correspondente.

[Compilação Windows/Linux aprovada](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39640033781) · [Testes de segurança aprovados](https://github.com/XandasL/OoT3D-PTBR-TriAevum/actions/runs/39640033690)

## Créditos

**Tradução PT-BR original:** Projeto Zelda Brasil — Heroes of Time; Catatau Game Dev e Traduções; Elite dos Quatro Traduções; JumpManClub Brasil Traduções; TRADU-ROMS.

**Port, adaptação e instalador para TriAevum:** XandasL.

**Recursos externos opcionais:** Henriko Magnifico; M-1 / rlgcarrot e colaboradores do SingleScreen / TopScreen. Respeite as licenças e os créditos respectivos. Projeto de fãs sem afiliação oficial com a Nintendo.
