# Changelog

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
