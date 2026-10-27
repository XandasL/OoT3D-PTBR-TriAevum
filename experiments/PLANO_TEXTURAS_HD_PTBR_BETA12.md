# Inventário inicial de artes HD PT-BR — TriAevum beta.1.2

**Status:** diagnóstico visual; nenhuma textura original ou runtime alterado.

Fontes fornecidas pelo autor: `vanilla_ui_hud-3.2.zip` e `topscreen.zip`. A beta.1.2 prepara uma UI TopScreen HD independente do O3RO PT-BR. Manter a tradução O3RO de 126 recursos; este trabalho trata apenas dos textos **desenhados dentro dos PNGs**.

## Prioridade 1 — visibilidade geral

| Identificador da textura | Contexto | Exemplos de texto original | Proposta |
| --- | --- | --- | --- |
| `1FAF9B5B2ADF6038` | Atlas HD TopScreen | Mod Options | Opções do Mod |
| `71EC8EF34C17BF8F` e `C0F1BD5D88603724` | Seleção de arquivos | Erase, Copy, Yes, No, Cancel, Start, Options | Apagar, Copiar, Sim, Não, Cancelar, Iniciar, Opções |
| `D6B04AFDACA985EF` | Tela de opções | Save, Don't Save, Hold, Switch, On, Off | Salvar, Não Salvar, Segurar, Alternar, Ligado, Desligado |
| `1B1E40F8F6E53947` | Menu de pausa | Continue, Quit, Gear, Map, Items, Back | Continuar, Sair, Equip., Mapa, Itens, Voltar |
| `164411C4E5F37729` | Inventário EUR | Gear, Map, Items, View, Back | Equip., Mapa, Itens, Ver, Voltar |
| `8E797095DBD2BD5F` | Mapa de masmorras | Inside the Deku Tree, Forest Temple etc. | Nomes PT-BR conforme tradução |
| `EF60A5ECFCD8F99D` | Mapa de Hyrule | Kokiri Forest, Hyrule Field etc. | Nomes PT-BR conforme tradução |

## Prioridade 2 — completude

- `BB00B25B152582B6`: outra variante de inventário USA; confirmar carregamento antes de editar
- `7D6716CEB0D7F7FA`: versão comum do inventário; confirmar precedência
- `CC7BF161FC89CB3B`: Challenge Cleared / Failed, Battle / Cancel
- `3149F395AE28A5F7`: THE END
- `EE6E53B64A496595`: Vision
- `554DABA69F3B3E2C`: Game Over e instruções

## Não traduzir indiscriminadamente

Preservar símbolos de botões `A/B/X/Y/ZL/ZR/START/SELECT`, ícones, áreas transparentes, sprites de animação e layouts. Checar no jogo se cada arquivo é realmente usado; alguns elementos foram reimplementados como UI nativa por TopScreen/Ocarina Reframed.

## Regra de compatibilidade

- **O3RO** contém os recursos RomFS e mensagens PT-BR, já testados no jogo.
- **O3TU** e `ui_atlas_hd.png` são recursos próprios do TopScreen. Não substituir diretamente arquivos gerenciados pelo Forge, nem mudar hashes de `import.json` sem integração controlada.
- O HD Vanilla UI/HUD 3.2 possui identificadores Azahar: preservar seus nomes e dimensões. Texturas do usuário devem continuar com prioridade.
- Criar uma **única instalação PT-BR** que prepare todos os recursos automaticamente, sem exigir uso manual de Load Textures.
- **Licenciamento:** arte de terceiros no Vanilla UI/HUD 3.2 tem restrições para derivados redistribuídos; usar como referência técnica para protótipos locais, obter permissão explícita antes de distribuir obras derivadas ou produzir arte nova licenciável.

## Próxima prova de conceito

Começar pelo identificador `1FAF9B5B2ADF6038` (`Mod Options`). Preparar layout PT-BR na resolução **4096×2048** do atlas original, manter o alpha e todas as regiões não textuais byte-equivalentes na imagem decodificada. Inspecionar dimensões em jogo. Em paralelo estudar a precedência dos outros atlas para adaptar somente o que o runtime realmente carrega. Não lançar pacote antes das validações.
