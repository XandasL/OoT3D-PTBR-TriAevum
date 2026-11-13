# The Legend of Zelda: Ocarina of Time 3D — Tradução PT-BR para Echoes of Time (TriAevum)

Adaptação da tradução brasileira de *The Legend of Zelda: Ocarina of Time 3D* para **Echoes of Time (TriAevum)**, incluindo diálogos, menus e texturas nativas traduzidas.

> **Versão atual: [v3.0.1](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v3.0.1)** — para **TriAevum v0.8.0-beta.2 (Echoes of Time)**, com ROMs **USA e EUR**. [Releases e downloads](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases).

## 🇧🇷 Sobre a tradução

Este projeto adapta uma tradução PT-BR existente com autorização de seu responsável, preservando os créditos originais dentro e fora do jogo. A v3.0.1 mantém **126 recursos de tradução** e foi testada com sucesso nas versões americana e europeia do jogo.

## 🔧 Correções da v3.0.1

- **Texturas estáveis e correção de crash:** nove arquivos de cena ZAR foram reconstruídos a partir dos originais, preservando somente as texturas PT-BR correspondentes.
- **76 cenas preservadas:** 67 recursos mantidos byte a byte e 9 reconstruídos; nenhuma cena precisou ser excluída.
- **Auditoria estrutural:** verificação de 76 ZAR, 152 CTXB internos e preservação dos recursos não traduzidos.
- **Teste funcional:** confirmado no Castelo de Ganon, onde as texturas se deslocavam e havia crash na transição de área. A atualização não foi testada exaustivamente em todas as cenas.

## ✨ Recursos da v3.0 mantidos

- **USA e EUR:** um único pacote, testado com sucesso em ambas as regiões.
- **Custom RomFS:** instalação integrada ao Forge, sem ativador, instalador externo ou distribuição de O3RO pré-compilado.
- **Windows e Linux:** mesmo ZIP, sem executáveis dependentes de plataforma. O funcionamento desta versão no Linux não foi testado diretamente; versões anteriores receberam confirmações de usuários Linux.
- **Arquivos originais preservados:** sem modificar a ROM nem o executável do TriAevum.

## 📦 Download

Baixe **[`OoT3D_PTBR_TriAevum_v3.0.1.zip`](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v3.0.1)** na página da release publicada.

Não são necessários pacotes separados para Windows e Linux.

### Versões anteriores

| Release | Versão do TriAevum |
| --- | --- |
| [v3.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v3.0) | v0.8.0-beta.2 |
| [v2.0 Beta](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/2.0) | v0.8.0-beta.1.2 |
| [v1.3.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.3.0) | v0.8.0-beta.1.1 |
| [v1.2.1](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.1) | v0.8.0-beta.1c |
| [v1.2.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.2.0) | v0.8.0-beta.1 |
| [v1.1.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/1.1.0) | v0.8.0-beta.1 |
| [v1.0.0](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v1.0.0) | v0.6.0-alpha.2c |

Use o pacote correspondente à versão do TriAevum. As releases antigas permanecem disponíveis com suas instruções próprias.

## 🛠️ Instalação — v3.0.1

1. Prepare o jogo normalmente pelo **TriAevum Forge v0.8.0-beta.2** e verifique se inicia sem mods.
2. Feche o jogo e extraia o ZIP na pasta preparada do TriAevum, preservando o caminho `data/mods/custom-romfs/`.
3. No Forge, abra **Enhancements**, ative **Custom RomFS** e clique em **Apply**.
4. Inicie o jogo normalmente.

**Atualizando da v3.0:** feche o jogo, substitua os arquivos da tradução pelos da v3.0.1 e clique novamente em **Apply** no Forge.

**Para desativar:** desmarque **Custom RomFS** e clique em **Apply**. Não é necessário editar `TriAevum.launch.json` nem usar ativadores.

## ⚠️ Texturas HD e limitações

Os recursos de interface traduzidos modificam texturas nativas. Isso pode alterar os hashes reconhecidos por pacotes de texturas HD/personalizadas e impedir que alguns elementos desses pacotes sejam aplicados. **A compatibilidade com packs HD não é garantida.**

O pacote não distribui a ROM, o jogo completo, executáveis do TriAevum ou texturas HD de terceiros.

## ✅ Validação

- **USA:** tradução testada no jogo nas versões USA/EUR; correção da v3.0.1 validada no Castelo de Ganon.
- **EUR:** tradução testada no jogo; correção da v3.0.1 não revalidada separadamente em todas as cenas.
- **Linux:** formato compartilhado com Windows; funcionamento da v3.0.1 ainda não verificado diretamente no Linux.

## 🧰 Código-fonte e manutenção das versões v3.x

A série v3.x utiliza o **Custom RomFS** integrado ao Forge. O código de manutenção atual encontra-se em [`tools/`](tools/README.md), com:

- reconstrução verificável do arquivo de mensagens USA/EUR (`build_v3_universal_qm.py`);
- geração do ZIP de distribuição a partir dos recursos previamente validados (`assemble_v3_package.py`);
- verificação de estrutura, integridade e hashes das releases (`verify_v3_package.py`);
- reconstrução verificável dos nove ZAR corrigidos na v3.0.1 (`rebuild_v301_scenes.py`);
- auditoria de todas as cenas e preservação dos dados originais (`audit_v301_scenes.py`).

Os instaladores anteriores em `installer/` são mantidos como **histórico de versões anteriores** e não são utilizados na série v3.x. Os arquivos da tradução permanecem distribuídos no ZIP da release, e não como ROM completa no repositório.

## ❤️ Créditos e autorização

**Tradução PT-BR original:**
- Projeto Zelda Brasil – Heroes of Time
- Catatau Game Dev e Traduções
- Elite dos Quatro Traduções
- JumpManClub Brasil Traduções
- TRADU-ROMS

**Port e adaptação para Echoes of Time (TriAevum):** XandasL.

A tradução original não foi criada por este repositório. O port e a distribuição da tradução completa são realizados com autorização do responsável pela tradução, condicionados à manutenção dos créditos dentro e fora do jogo.

Consulte [CREDITOS.md](CREDITOS.md) e o `LEIA-ME.txt` incluído no download.

## ⚠️ Aviso legal

Projeto de fãs, sem afiliação oficial com a Nintendo. *The Legend of Zelda* e demais propriedades relacionadas pertencem aos respectivos titulares.
