# OpÃƒÂ§ÃƒÂ£o de menus HD no instalador

A integraÃƒÂ§ÃƒÂ£o acrescenta um componente opcional ÃƒÂ  v1.2.0. A traduÃƒÂ§ÃƒÂ£o normal mantÃƒÂ©m seu nÃƒÂºcleo, payload e validaÃƒÂ§ÃƒÂµes. A opÃƒÂ§ÃƒÂ£o HD aceita somente o **TriAevum v0.8.0-beta.1 Windows x64 testado**, conferindo o SHA-256 do executÃƒÂ¡vel original, de suas dependÃƒÂªncias e do RomFS traduzido. Exige a traduÃƒÂ§ÃƒÂ£o completa e a polÃƒÂ­tica de preservaÃƒÂ§ÃƒÂ£o da fonte HD com os acentos normalizados. Linux e alpha.2c continuam utilizando a traduÃƒÂ§ÃƒÂ£o normal.

## Uso

1. Instale a traduÃƒÂ§ÃƒÂ£o normalmente e confira o jogo.
2. Feche o jogo e o Forge.
3. No instalador com o componente HD incluÃƒÂ­do, clique em **Adicionar texturas HD (Windows 0.8)**.
4. Selecione o pacote 4K mesclado com os PNGs traduzidos e TopScreen que foi validado. Ãƒâ€° possÃƒÂ­vel selecionar a pasta que contÃƒÂ©m `pack.json` ou uma pasta superior contendo um ÃƒÂºnico pack.
5. Abra **TriAevum-PTBR-HD.exe** na pasta do jogo.

O instalador verifica os hashes dos 75 PNGs relevantes. O pack original em inglÃƒÂªs ou outro conjunto de imagens nÃƒÂ£o ÃƒÂ© aceito automaticamente: mapear esses PNGs para hashes PT-BR poderia recolocar palavras em inglÃƒÂªs nos menus. Uma variante de pack exige receita e validaÃƒÂ§ÃƒÂ£o prÃƒÂ³prias. O pacote de texturas continua externo; nenhum PNG 4K ÃƒÂ© embutido no instalador.

## Arquivos e restauraÃƒÂ§ÃƒÂ£o

- O executÃƒÂ¡vel original, o perfil original, as configuraÃƒÂ§ÃƒÂµes originais, o RomFS, o O3TU e os saves nÃƒÂ£o sÃƒÂ£o modificados pela opÃƒÂ§ÃƒÂ£o HD.
- SÃƒÂ£o acrescentados o executÃƒÂ¡vel e o perfil `TriAevum-PTBR-HD`, alÃƒÂ©m de uma configuraÃƒÂ§ÃƒÂ£o prÃƒÂ³pria em `data/config/TriAevum-PTBR-HD.json`.
- As duas dependÃƒÂªncias opcionais do build testado sÃƒÂ£o acrescentadas somente se ausentes. Se uma DLL jÃƒÂ¡ existe com conteÃƒÂºdo diferente, a operaÃƒÂ§ÃƒÂ£o inteira ÃƒÂ© recusada.
- Os 71 aliases (13 menus + 58 ÃƒÂ¡reas, bosses e outros grÃƒÂ¡ficos) ficam em `UI/PTBR_HASHES` no pack selecionado. Arquivos jÃƒÂ¡ existentes e idÃƒÂªnticos sÃƒÂ£o registrados como nÃƒÂ£o pertencentes ÃƒÂ  instalaÃƒÂ§ÃƒÂ£o e preservados ao remover o HD.
- O recibo de transaÃƒÂ§ÃƒÂ£o fica em `data/mods/ptbr-hd/installation.json`. Uma falha de gravaÃƒÂ§ÃƒÂ£o retorna os arquivos ao estado anterior. Uma instalaÃƒÂ§ÃƒÂ£o interrompida pode ser revertida pelo mesmo comando de remoÃƒÂ§ÃƒÂ£o.
- **Remover suporte HD** desfaz apenas as alteraÃƒÂ§ÃƒÂµes pertencentes ao componente. A configuraÃƒÂ§ÃƒÂ£o HD ÃƒÂ© mantida para preservar preferÃƒÂªncias; fica inativa apÃƒÂ³s a remoÃƒÂ§ÃƒÂ£o de seu lanÃƒÂ§ador. Se um arquivo pertencente ÃƒÂ  instalaÃƒÂ§ÃƒÂ£o tiver sido modificado, a remoÃƒÂ§ÃƒÂ£o para antes de apagar outros arquivos.
- **Restaurar original** remove primeiro o componente HD registrado e entÃƒÂ£o chama a restauraÃƒÂ§ÃƒÂ£o existente da traduÃƒÂ§ÃƒÂ£o. Se essa segunda etapa falhar, a traduÃƒÂ§ÃƒÂ£o continua instalada com seus backups; o HD jÃƒÂ¡ removido pode ser reinstalado depois.

O atlas de dicas em vÃƒÂ­deo `menu_hint_movie_parts00.ctxb` nÃƒÂ£o possui PNG correspondente no pack e usa a resoluÃƒÂ§ÃƒÂ£o nativa. A fonte do perfil TopScreen permanece em 1024Ãƒâ€”256; 16 dos 17 atlas verificados aumentam a resoluÃƒÂ§ÃƒÂ£o.

## Build opcional

O build padrÃƒÂ£o permanece sem runtime HD. A receita estÃƒÂ¡ em `hd-recipe.json`; nÃƒÂ£o hÃƒÂ¡ download ou atualizaÃƒÂ§ÃƒÂ£o automÃƒÂ¡tica do runtime corrigido. Para preparar o bundle a partir do executÃƒÂ¡vel jÃƒÂ¡ testado:

```powershell
python installer/prepare_hd_runtime.py --executable "caminho/TriAevum-TexturasHD.exe" --upstream "caminho/TriAevum-v0.8.0-beta.1-Windows-x64-extract" --patch "caminho/TriAevum-0.8-menus-HD.patch" --output build/hd-runtime
python installer/build_installer.py --hd-runtime build/hd-runtime --source-zip "caminho/OoT3D_PTBR_TriAevum_v1.0.zip"
```

O artefato recebe o sufixo `_HD`, distinguindo-o do instalador normal. O bundle inclui o executÃƒÂ¡vel genÃƒÂ©rico, duas DLLs do renderer, fontes correspondentes, o patch e os avisos/licenÃƒÂ§as originais. NÃƒÂ£o contÃƒÂ©m ROM, RomFS preparado, plugin privado do tÃƒÂ­tulo, save ou pack PNG. O ZIP tambÃƒÂ©m oferece os fontes e avisos em `runtime-HD/`, fora do executÃƒÂ¡vel do instalador. Os crÃƒÂ©ditos de Henriko Magnifico e do TopScreen continuam pertencendo aos respectivos projetos e packs.

## VerificaÃƒÂ§ÃƒÂ£o sem alteraÃƒÂ§ÃƒÂµes

```powershell
python installer/hd_textures.py --root "pasta/TriAevum" --pack "pasta/pack" --runtime build/hd-runtime --action check
python -m unittest test_hd_integration -v
```

Os testes cobrem instalaÃƒÂ§ÃƒÂ£o/remoÃƒÂ§ÃƒÂ£o/reinstalaÃƒÂ§ÃƒÂ£o, arquivos preexistentes, preservaÃƒÂ§ÃƒÂ£o de preferÃƒÂªncias e saves, hashes incorretos, conteÃƒÂºdo nÃƒÂ£o validado, conflito entre mods, falha de gravaÃƒÂ§ÃƒÂ£o com rollback e caminhos adulterados no recibo. Os testes de integraÃƒÂ§ÃƒÂ£o usam arquivos sintÃƒÂ©ticos em pastas temporÃƒÂ¡rias do projeto.

O runtime corrigido jÃƒÂ¡ foi confirmado pelo usuÃƒÂ¡rio e em capturas de seleÃƒÂ§ÃƒÂ£o de arquivos, HUD e pausa. A integraÃƒÂ§ÃƒÂ£o no instalador foi preparada e validada localmente; nenhuma release foi publicada automaticamente.

## CrÃƒÂ©ditos e limitaÃƒÂ§ÃƒÂµes da v1.2.0

Veja [TEXTURAS_CREDITOS.md](TEXTURAS_CREDITOS.md) para Henriko Magnifico, texturas 4K TopScreen e UI/MENU 4K TRADUZIDA PT-BR + PS5 LAYOUT. As 58 novas correspondÃƒÂªncias passaram no carregador Azahar real usando o RomFS traduzido. A cobertura restante nÃƒÂ£o foi certificada como completa. Uma versÃƒÂ£o HD anterior deve ser removida com seu instalador anterior antes da atualizaÃƒÂ§ÃƒÂ£o.

O EXE atualizado oferece a opÃƒÂ§ÃƒÂ£o `Input.DualSenseWindowsCompatibility` no JSON grÃƒÂ¡fico, desativada por padrÃƒÂ£o. Essa opÃƒÂ§ÃƒÂ£o ÃƒÂ© um contorno de entrada independente da traduÃƒÂ§ÃƒÂ£o HD e nÃƒÂ£o garante sensores/giroscÃƒÂ³pio. NÃƒÂ£o ÃƒÂ© necessÃƒÂ¡rio abrir o jogo por CMD.

## DistribuiÃ§Ã£o simplificada

O ZIP do usuÃ¡rio contÃ©m o instalador, instruÃ§Ãµes, crÃ©ditos e licenÃ§as. Os fontes correspondentes sÃ£o oferecidos separadamente em `OoT3D_PTBR_TriAevum_v1.2.0_Fontes-HD.zip`, na mesma release, sem custo. O runtime tÃ©cnico do Actions permanece em draft interno separado. Os hashes aparecem na descriÃ§Ã£o da release; os arquivos `.sha256` ficam apenas nos artefatos do Actions.

## Aviso da Navi

A integração recompõe o texto `Navi` que falta no atlas HD, apenas no alias da tradução. O PNG original do pack não é alterado. O recurso de composição é próprio da integração e não inclui o atlas dos autores. Um alias antigo que seja uma cópia exata do PNG validado pode ser atualizado com backup; arquivos diferentes são recusados. A remoção restaura o alias preexistente.
