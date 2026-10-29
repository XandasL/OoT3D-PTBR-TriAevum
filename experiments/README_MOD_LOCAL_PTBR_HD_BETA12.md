# Preparação de mod local HD PT-BR (experimental)

A tradução textual já foi validada pelo autor com a variante de 95 destinos O3RO. Ele também confirmou o carregamento de suas texturas HD após substituir PNGs na pasta de mods. Não redistribuir esses PNGs sem licença.

Este script apenas **prepara uma cópia isolada**; não modifica TriAevum.exe, RomFS, a pasta Vanilla UI/HUD 3.2 original ou o perfil de lançamento. Não altera a release 1.3.0. A cópia inclui `source.json` originalmente gerado pelo Forge para preservar o layout, mas **não deve ser assumida como automaticamente reconhecida/validada pelo Forge**: a validação do recibo e a ativação ainda exigem homologação.

Da pasta `experiments`, simular:

```powershell
$runtime = "E:\Mods Creation\TriAevum-PT-BR\TriAevum-v0.8.0-beta.1.2-Windows-x64"
$zip = "E:\Mods Creation\TriAevum-PT-BR\Texturas Prontas.zip"
$vanilla = "$runtime\data\mods\ui-textures\vanilla_ui_hud-3.2"
$dest = "E:\Mods Creation\TriAevum-PT-BR\OoT3D-PTBR-local\hd-ui"

py -3 prepare_ptbr_hd_mod_beta12.py --textures-zip $zip --vanilla $vanilla --destination $dest --dry-run
```

Se não houver ambiguidade e a simulação listar 20 texturas, executar sem `--dry-run`. O destino deve **não existir** previamente. Caso algum nome de PNG apareça em múltiplos diretórios, fornecer `--mapping mapa.json` com os nomes de arquivo como chaves e os caminhos relativos ao Vanilla como valores, somente depois de confirmar o destino real.

As operações sobre arquivos gráficos permanecem locais. Antes de ativação automática num perfil, validar se a cópia modificada é reconhecida pelo carregador com seu recibo e se o carregamento de arquivos personalizados do jogador mantém precedência. O TopScreen deve receber o caminho da versão HD traduzida já presente no pacote, sem modificar o O3TU.

Testes: `py -3 test_prepare_ptbr_hd_mod_beta12.py`.

