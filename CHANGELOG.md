# Changelog

## v3.0.1 — 2026-11-13

- Corrigidos problemas de texturas deslocadas e crash ao sair de uma área do Castelo de Ganon.
- Reconstruídos **9 arquivos ZAR** de cena a partir de recursos originais, reutilizando exclusivamente as texturas de nome PT-BR.
- Preservados os **76 arquivos de cena** e os **126 recursos** da tradução, sem remoções.
- Auditoria estática de 76 ZAR e 152 texturas CTXB internas; dados de cena não traduzidos preservados.
- Validação prática da correção no local onde ocorria o problema; outras cenas e o Linux ainda não foram retestados integralmente.
- Acrescentadas ferramentas Python reproduzíveis de reconstrução, comparação e validação, sem redistribuir ROMs nem recursos protegidos no código-fonte.
- Pacote publicado: [v3.0.1](https://github.com/XandasL/OoT3D-PTBR-TriAevum/releases/tag/v3.0.1).

## v3.0 — 2026-11-13

- Migração para **Echoes of Time (TriAevum v0.8.0-beta.2)** e seu sistema nativo **Custom RomFS**.
- Pacote único de tradução para ROMs **USA e EUR**, ambas testadas com sucesso.
- Distribuição unificada para Windows e Linux, sem instaladores, ativadores ou O3RO pré-compilado.
- Mantidos os **126 recursos** da tradução clássica PT-BR, com arquivo de mensagens adaptado para ambas as regiões.
- Preservação da ROM original, executável do TriAevum e créditos da tradução.
- Compatibilidade com texturas HD/personalizadas ainda sujeita a diferenças de hashes das texturas nativas.

## v2.0 Beta — 2026-11-02

- Transição para mod O3RO com 126 substituições e preservação da RomFS original.
- Pacotes com ativadores para Windows e Linux para configuração do overlay.
- Compatibilidade com TriAevum v0.8.0-beta.1.2.

## v1.3.0 — 2026-10-21

- Tradução clássica com 112 recursos de origem e 14 espelhos de menus EUR.
- Otimização e opção de fonte HD 64, preservando opção de fonte original.
- Pacotes para Windows e Linux e compatibilidade opcional com pack Henriko 5.0a.

## v1.2.1 — 2026-10-15

- Compatibilidade com os caminhos `${runtime_dir}` dos novos perfis Forge.
- Runtime HD atualizado para a base TriAevum v0.8.0-beta.1c, preservando as correções recentes do TopScreen e renderer.
- Mantidas as 71 correspondências HD, a correção da Navi e a fonte com acentos PT-BR.
- Instalação e restauração da tradução verificadas numa cópia isolada da nova base.
- Pacotes simplificados e fontes correspondentes separados; releases anteriores preservadas.

## v1.0 — 2026-09-17

Primeira versão pública preparada do port PT-BR de **The Legend of Zelda: Ocarina of Time 3D** para **TriAevum v0.6.0-alpha.2c**.

### Tradução

- Adaptação completa dos recursos utilizados pela tradução PT-BR.
- Conversão do arquivo de mensagens do layout USA para o slot EUR utilizado pelo runtime.
- Espelhamento dos recursos de menu necessários para a interface em execução.
- Instalação dos recursos gráficos traduzidos.

### Compatibilidade

- Compatibilidade com a estrutura testada do TriAevum v0.6.0-alpha.2c Windows x64.
- Correção de compatibilidade com TopScreen / Single Screen preservando o payload de substituição do TriAevum.

### Instalador

- Interface gráfica para Windows.
- Verificação do estado da instalação.
- Validação do RomFS compatível antes da modificação.
- Backup automático dos arquivos modificados.
- Instalação da tradução completa.
- Restauração do estado original.
- Distribuição planejada como executável único, sem dependência de Python para o usuário final.

### Testes

O executável v1.0 foi validado no ciclo completo: instalação → execução no jogo → restauração → reabertura do instalador → nova instalação. Também foi testado sem depender das antigas pastas externas de desenvolvimento.
