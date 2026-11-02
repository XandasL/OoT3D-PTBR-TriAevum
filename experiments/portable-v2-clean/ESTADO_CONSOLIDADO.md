# Estado consolidado — OoT3D PT-BR v2 limpa

**Data da revisão:** 2026-11-02  
**Escopo:** branch `experiment/native-romfs-overlay-ptbr`, sem alterações na `main` ou nas releases.  
**Propósito:** referência única para decisões já tomadas; evitar reabrir questões resolvidas sem fatos novos.

## Decisões confirmadas pelo autor

1. A v2 limpa distribui **apenas a tradução clássica PT-BR**, sem imagens HD traduzidas de ChubbyCubby/Vanilla UI/HUD e sem conteúdos SingleScreen/TopScreen HD.
2. O arquivo antigo `installer/navi-hud-overlay.png` (correção histórica do texto «Navi» cortado) foi **removido da branch experimental**, commit `a82d3452`; não integra a v2.
3. **Não** manter instalador executável próprio (PyInstaller/Inno Setup) nesta fase. Distribuição alvo: ZIP portátil + `Ativar-PTBR.cmd` e `.ps1`.
4. Preservar os recursos **nativos da tradução original** e sua estrutura: 112 fontes verificadas, 14 espelhos EUR, total **126 substituições** O3RO.
5. Alvo testado: **TriAevum `v0.8.0-beta.1.2`**. Não prometer compatibilidade automática com outras versões nem alterar `TriAevum.exe` ou a RomFS original.
6. O usuário já **confirmou o funcionamento em jogo** do modo clássico sem HD e do ZIP portátil limpo com ativador. Não pedir repetição desses mesmos testes sem mudanças relevantes no conteúdo.
7. **Autorização da tradução original:** o autor do port informou que obteve autorização dos criadores para utilização e distribuição; o arquivo histórico `installer/CREDITOS.txt` já declara essa autorização, condicionada à preservação dos créditos dentro e fora do jogo. Não tratar a autorização dos tradutores como ausência de resposta, nem pedir novamente a mesma confirmação.
8. Direitos de terceiros são distintos: ChubbyCubby declarou que **não autoriza redistribuir** suas texturas modificadas; o material foi excluído da versão limpa. Não confundir essa negativa com a autorização da tradução clássica.
9. Integração nativa ao Forge permanece desejável, mas o catálogo de mods beta.1.2 é fechado; a solução portátil é a escolhida por enquanto.
10. **Decisão posterior do autor:** a v2.0 mantém o O3RO clássico completo, com 126 substituições, **sem garantir compatibilidade com packs de texturas HD/personalizadas**. Não desenvolver agora aliases, adaptadores de `pack.json`, nem variante reduzida de 95 registros. Há falha observada no HUD com tradução ativada e carregamento normal sem a tradução; documentar a limitação e priorizar a tradução estável.

## Créditos originais — já documentados

Fonte canônica: `installer/CREDITOS.txt`.

- Projeto Zelda Brasil – Heroes of Time
- Catatau Game Dev e Traduções
- Elite dos Quatro Traduções
- JumpManClub Brasil Traduções
- TRADU-ROMS
- XandasL — port e adaptação para TriAevum

O arquivo também documenta a autorização recebida do responsável pela tradução e os agradecimentos. **Créditos já integrados à embalagem atualizada:** `experiments/portable-v2-clean/CREDITOS.txt` está entre os cinco membros esperados pelo gerador. Preservar os nomes e a autorização documentada. Não renomear colaboradores.

## Artefatos, provas e caminhos técnicos

- Gerador O3RO: `experiments/build_ptbr_o3ro_beta12.py`.
- O3RO clássico local: **126 registros**, SHA-256 `4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3`.
- RomFS base verificada: SHA-256 `dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56`.
- Pacote portátil fonte: `experiments/portable-v2-clean/`.
- Ativador configura `--romfs-overlay` em `data/TriAevum.launch.json`, preservando opções gráficas do Forge; executar novamente `Prepare and install` pode sobrescrever o perfil e exigir nova ativação.
- Arquivos do ZIP local testado inicialmente: `Ativar-PTBR.cmd`, `Ativar-PTBR.ps1`, `LEIA-ME.txt`, `data/mods/OoT3D-PTBR/classico.o3ro`. A revisão posterior do gerador acrescentou `CREDITOS.txt`, necessitando validação do ZIP atualizado.
- Os 20 PNGs HD modificados e o atlas TopScreen não estão nas árvores atuais auditadas das 9 branches nem nas tags de código 1.2.0/1.2.1/1.3.0. Esse resultado **não é uma auditoria completa de todos os commits e arquivos ZIP das releases antigas**.
- O O3RO clássico contém payload de substituições RomFS e **não é apenas um manifesto de alterações**, mas não incorpora a RomFS integral. Esse fato técnico não altera o registro da autorização dos tradutores.
- A `main` e releases anteriores devem ficar intactas enquanto a versão experimental não for finalizada.

## Pendências reais — não confundir com decisões resolvidas

- **Créditos na distribuição final:** arquivo `CREDITOS.txt` incluído nos fontes e exigido pelo gerador; conferir sua presença no ZIP construído.
- **Verificação final da embalagem atualizada:** executar testes do gerador com os cinco membros e um teste funcional apenas se houver modificação relevante do ativador ou do conteúdo.
- **Delimitação de direitos:** autorização documentada dos tradutores cobre suas próprias contribuições; eventuais direitos dos titulares do jogo são um assunto distinto. Não reabrir discussão abstrata a cada passo; realizar uma revisão de publicação proporcional ao conteúdo final.
- **Compatibilidade:** restringir a beta.1.2; não insinuar certificação para versões futuras.
- **Histórico:** remover a imagem Navi do estado atual não apaga seus blobs de commits/tags antigos; não afirmar exclusão retroativa.
- **Testes automatizados:** `test_gerar_zip_local.py` foi adicionado, mas sua execução em Windows não foi confirmada no diálogo.

## Históricos separados — não são dependências da v2 limpa

- O3RO HD de 95 substituições, PNGs traduzidos, fonte HD64, atlas TopScreen, integração Inno Setup, compatibilidade Henriko, e documentação de releases v1.x. Manter como histórico técnico, **não empacotar**.
- O suporte genérico de mods pelo Forge ainda depende do upstream; não bloquear a v2 limpa esperando essa integração.

## Critério de conclusão

O caminho para finalizar a v2 é **incluir os créditos na embalagem**, executar os testes pertinentes e preparar a descrição de release beta. Não pedir novamente autorização ao responsável pela tradução original já registrada, salvo surgimento de evidência contraditória ou mudança de escopo.
