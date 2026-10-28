# Integração local de texturas HD PT-BR — TriAevum beta.1.2

## Inventário realmente verificado — 28/10/2026

Foi possível ler o anexo local `Texturas Prontas(1).zip`: 21 PNGs, sendo 20 em `VanillaUI/` e um em `TopScreen/`. A verificação CRC do arquivo passou e os 21 arquivos têm cabeçalhos PNG válidos, modo RGBA e dimensões legíveis. O atlas `TopScreen/ui_atlas_hd.png` tem 4096×2048 e é byte a byte idêntico a `VanillaUI/tex1_512x256_1FAF9B5B2ADF6038_13_mip0.png`. Estes dois arquivos são intencionalmente **um só destino de conteúdo**, mas alimentam flags distintas do runtime.

O instalador experimental exige agora esse layout e evita dupla correspondência. **Ainda não foi homologado contra uma pasta `vanilla_ui_hud-3.2` real.** Os nomes de PNG podem existir em múltiplas pastas de idioma, e `find_targets` permanece fail-closed: interrompe o processo se a correspondência for ambígua. Não altere manualmente o script para escolher um destino arbitrário.

**Pendências reais:** identificar os 20 destinos a partir da estrutura efetiva `common/` e `languages/` no runtime do autor; estudar os CTXB do O3RO e testes A/B com o overlay ligado/desligado; integrar `--romfs-overlay` numa transação comum com o perfil HD; validar precedência do pacote de texturas personalizado do jogador; testar restauração e cenários de interrupção. Os commits atuais não representam integração O3RO+HD concluída.

Os PNGs derivados de terceiros não foram publicados no repositório; mantê-los locais até a autorização de redistribuição.


**Experimental e não testado em instalação real nesta alteração.** Este procedimento não distribui texturas modificadas de terceiros. O proprietário mantém seu ZIP localmente; a autorização de publicação das artes ainda precisa ser resolvida.

## O que o script faz

- Confere se o Vanilla UI/HUD 3.2 já foi preparado pelo Forge.
- Lê PNGs do ZIP de texturas traduzidas e procura os nomes correspondentes no pacote já preparado.
- Recusa imagens com dimensões diferentes da referência, caminhos ZIP inseguros, nomes duplicados ou destinos ambíguos.
- Cria uma cópia completa do pacote Vanilla em `data/mods/ui-textures/ptbr-hd-beta12/`; não sobrescreve os originais.
- Salva o perfil de lançamento original em `data/mods/ptbr-hd-beta12-launch-original.json` e registra as alterações em `data/mods/ptbr-hd-beta12-receipt.json`.
- Altera apenas `--ui-texture-pack` para a cópia integrada. **Se** a textura `1FAF9B5B2ADF6038` constar no ZIP, também altera o caminho `--topscreen-ui-atlas-hd` para a versão traduzida.
- **Não altera** `--romfs-overlay`, o O3RO PT-BR, o executável, a ROM, a pasta do Vanilla original nem os saves.

## Comandos PowerShell (raiz do repositório)

Deixe o TriAevum e o Forge **fechados**.

Primeiro, faça a simulação (somente leitura):

```powershell
py -3 experiments\install_ptbr_hd_vanilla_beta12.py `
  --runtime "E:\Mods Creation\TriAevum-PT-BR\TriAevum-v0.8.0-beta.1.2-Windows-x64" `
  --textures-zip "E:\Mods Creation\TriAevum-PT-BR\Texturas Prontas.zip" `
  --dry-run
```

O comando não altera a instalação. Revise os caminhos e a quantidade de imagens listadas. Se houver mensagens `Ambiguous texture filename` ou `Texture not present`, corrija a estrutura do ZIP antes de prosseguir. **Não force destinos arbitrários**.

Após o relatório de simulação ser aprovado, execute o mesmo comando **sem** `--dry-run`:

```powershell
py -3 experiments\install_ptbr_hd_vanilla_beta12.py `
  --runtime "E:\Mods Creation\TriAevum-PT-BR\TriAevum-v0.8.0-beta.1.2-Windows-x64" `
  --textures-zip "E:\Mods Creation\TriAevum-PT-BR\Texturas Prontas.zip"
```

Abra diretamente `TriAevum.exe` sem reexecutar o Forge, que pode reconfigurar os argumentos. Teste menu de opções, itens, mapas, HUD e a sobreposição O3RO. O fato de o arquivo ser identificado não garante que o runtime carregue aquela textura — é preciso validar dentro do jogo.

## Restauração do perfil

Com o jogo fechado:

```powershell
py -3 experiments\install_ptbr_hd_vanilla_beta12.py `
  --runtime "E:\Mods Creation\TriAevum-PT-BR\TriAevum-v0.8.0-beta.1.2-Windows-x64" `
  --uninstall
```

O script só restaura o backup se o arquivo de perfil ainda corresponder exatamente ao estado instalado. Se outro programa modificar o perfil depois, ele recusa sobrescrever mudanças de terceiros. O pacote PT-BR gerado é mantido no disco por segurança; pode ser eliminado manualmente depois que o perfil original for restaurado e conferido.

## Limitações atuais

1. O script **não altera** as substituições CTXB antigas dentro do O3RO experimental. Por isso, o conflito entre overlays de RomFS e texturas HD em determinados menus **não está resolvido**. Precisamos testar e analisar o gerador O3RO separadamente.
2. Texturas com um mesmo nome em pastas de idioma diferentes exigem caminhos inequívocos dentro do ZIP; o script recusa correspondência ambígua. Não presume que a mesma tradução serve a variantes diferentes.
3. O ZIP de texturas prontas foi inspecionado em 28/10/2026. Ainda falta a correspondência inequívoca dos 20 PNGs aos caminhos locais de idiomas do pacote Vanilla preparado.
4. Este é um protótipo restrito à beta.1.2, não um instalador final. Verificações de perfil após uma nova execução do Forge e conflitos com outros pacotes não estão homologadas.
5. Não publicar PNGs derivados de obras de terceiros sem autorização de redistribuição documentada.
