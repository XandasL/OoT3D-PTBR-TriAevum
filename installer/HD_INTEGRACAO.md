# Opção de menus HD no instalador

A integração acrescenta um componente opcional à v1.2.0. A tradução normal mantém seu núcleo, payload e validações. A opção HD aceita somente o **TriAevum v0.8.0-beta.1 Windows x64 testado**, conferindo o SHA-256 do executável original, de suas dependências e do RomFS traduzido. Exige a tradução completa e a política de preservação da fonte HD com os acentos normalizados. Linux e alpha.2c continuam utilizando a tradução normal.

## Uso

1. Instale a tradução normalmente e confira o jogo.
2. Feche o jogo e o Forge.
3. No instalador com o componente HD incluído, clique em **Adicionar texturas HD (Windows 0.8)**.
4. Selecione o pacote 4K mesclado com os PNGs traduzidos e TopScreen que foi validado. É possível selecionar a pasta que contém `pack.json` ou uma pasta superior contendo um único pack.
5. Abra **TriAevum-PTBR-HD.exe** na pasta do jogo.

O instalador verifica os hashes dos 75 PNGs relevantes. O pack original em inglês ou outro conjunto de imagens não é aceito automaticamente: mapear esses PNGs para hashes PT-BR poderia recolocar palavras em inglês nos menus. Uma variante de pack exige receita e validação próprias. O pacote de texturas continua externo; nenhum PNG 4K é embutido no instalador.

## Arquivos e restauração

- O executável original, o perfil original, as configurações originais, o RomFS, o O3TU e os saves não são modificados pela opção HD.
- São acrescentados o executável e o perfil `TriAevum-PTBR-HD`, além de uma configuração própria em `data/config/TriAevum-PTBR-HD.json`.
- As duas dependências opcionais do build testado são acrescentadas somente se ausentes. Se uma DLL já existe com conteúdo diferente, a operação inteira é recusada.
- Os 71 aliases (13 menus + 58 áreas, bosses e outros gráficos) ficam em `UI/PTBR_HASHES` no pack selecionado. Arquivos já existentes e idênticos são registrados como não pertencentes à instalação e preservados ao remover o HD.
- O recibo de transação fica em `data/mods/ptbr-hd/installation.json`. Uma falha de gravação retorna os arquivos ao estado anterior. Uma instalação interrompida pode ser revertida pelo mesmo comando de remoção.
- **Remover suporte HD** desfaz apenas as alterações pertencentes ao componente. A configuração HD é mantida para preservar preferências; fica inativa após a remoção de seu lançador. Se um arquivo pertencente à instalação tiver sido modificado, a remoção para antes de apagar outros arquivos.
- **Restaurar original** remove primeiro o componente HD registrado e então chama a restauração existente da tradução. Se essa segunda etapa falhar, a tradução continua instalada com seus backups; o HD já removido pode ser reinstalado depois.

O atlas de dicas em vídeo `menu_hint_movie_parts00.ctxb` não possui PNG correspondente no pack e usa a resolução nativa. A fonte do perfil TopScreen permanece em 1024×256; 16 dos 17 atlas verificados aumentam a resolução.

## Build opcional

O build padrão permanece sem runtime HD. A receita está em `hd-recipe.json`; não há download ou atualização automática do runtime corrigido. Para preparar o bundle a partir do executável já testado:

```powershell
python installer/prepare_hd_runtime.py --executable "caminho/TriAevum-TexturasHD.exe" --upstream "caminho/TriAevum-v0.8.0-beta.1-Windows-x64-extract" --patch "caminho/TriAevum-0.8-menus-HD.patch" --output build/hd-runtime
python installer/build_installer.py --hd-runtime build/hd-runtime --source-zip "caminho/OoT3D_PTBR_TriAevum_v1.0.zip"
```

O artefato recebe o sufixo `_HD`, distinguindo-o do instalador normal. O bundle inclui o executável genérico, duas DLLs do renderer, fontes correspondentes, o patch e os avisos/licenças originais. Não contém ROM, RomFS preparado, plugin privado do título, save ou pack PNG. O ZIP também oferece os fontes e avisos em `runtime-HD/`, fora do executável do instalador. Os créditos de Henriko Magnifico e do TopScreen continuam pertencendo aos respectivos projetos e packs.

## Verificação sem alterações

```powershell
python installer/hd_textures.py --root "pasta/TriAevum" --pack "pasta/pack" --runtime build/hd-runtime --action check
python -m unittest test_hd_integration -v
```

Os testes cobrem instalação/remoção/reinstalação, arquivos preexistentes, preservação de preferências e saves, hashes incorretos, conteúdo não validado, conflito entre mods, falha de gravação com rollback e caminhos adulterados no recibo. Os testes de integração usam arquivos sintéticos em pastas temporárias do projeto.

O runtime corrigido já foi confirmado pelo usuário e em capturas de seleção de arquivos, HUD e pausa. A integração no instalador foi preparada e validada localmente; nenhuma release foi publicada automaticamente.

## Créditos e limitações da v1.2.0

Veja [TEXTURAS_CREDITOS.md](TEXTURAS_CREDITOS.md) para Henriko Magnifico, texturas 4K TopScreen e UI/MENU 4K TRADUZIDA PT-BR + PS5 LAYOUT. As 58 novas correspondências passaram no carregador Azahar real usando o RomFS traduzido. A cobertura restante não foi certificada como completa. Uma versão HD anterior deve ser removida com seu instalador anterior antes da atualização.

O EXE atualizado oferece a opção `Input.DualSenseWindowsCompatibility` no JSON gráfico, desativada por padrão. Essa opção é um contorno de entrada independente da tradução HD e não garante sensores/giroscópio. Não é necessário abrir o jogo por CMD.
