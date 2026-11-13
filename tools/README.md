# Ferramentas de manutenção da v3.0

Esta pasta documenta como reconstruir e conferir os arquivos de mensagens da tradução **Echoes of Time (TriAevum) v3.0**, compatível com ROMs **USA e EUR** no TriAevum v0.8.0-beta.2.

As ferramentas são **offline** e não alteram o jogo instalado, a RomFS, o Forge ou seus saves.

## Reconstruir o arquivo universal `eu.qm`

O resultado foi comparado byte a byte com o `eu.qm` da v3.0 testada nas duas regiões.

Requisitos (obtidos separadamente pelo mantenedor):
- ZIP funcional da tradução Custom RomFS anterior, contendo `data/mods/custom-romfs/message/eu/eu.qm` (v2, SHA-256 `f2c97990...`);
- extração da **RomFS europeia** do próprio jogo, compactada com `RomFS_Extraida_EUR/message/eu/eu.qm` (SHA-256 `5b5addf7...`);
- Python 3.10+ (apenas biblioteca padrão).

Execute na raiz do repositório:

```powershell
python tools/build_v3_universal_qm.py --eur-romfs-zip "RomFS_Extraida_EUR.zip" --ptbr-v2-zip "OoT3D-PTBR-Custom-RomFS-TriAevum-beta2.zip" --output "eu-v3.qm"
```

A rotina valida os hashes das entradas, preserva os demais idiomas da EUR, injeta os textos PT-BR nas posições de inglês 1 e 2 e impede sobrescrever o arquivo de saída.

**SHA-256 esperado de `eu-v3.qm`:** `2c01f578280f331befa6683eb2c18e27c8538b80df9536344c4c9cacc7c8866d`.

O `eu-v3.qm` deve substituir `data/mods/custom-romfs/message/eu/eu.qm` no pacote de distribuição. Os outros 125 recursos permanecem iguais aos da versão funcional anterior. Nenhuma RomFS ou arquivo original do jogo é armazenado neste repositório.

## Validar o pacote v3.0

```powershell
python tools/verify_v3_package.py "OoT3D_PTBR_TriAevum_v3.0.zip" --exact-release
```

Confere integridade do ZIP, estrutura Custom RomFS, contagem e tipos dos 126 arquivos, manifesto e hash do `eu.qm`. A opção `--exact-release` compara também o hash do **ZIP exato testado**. Para conferir um ZIP recompacotado com os mesmos recursos, omita a opção.

**SHA-256 do ZIP v3.0 testado:** `5db68dd5ce2d4633028ccbe63e0487446c5dccfe39bd4f27081e450796aece23`.

## Testes automatizados

```powershell
python -m unittest discover -s tests -p "test_v3_*.py" -v
```

Os testes são sintéticos e não incluem dados protegidos do jogo.

## Histórico

Os instaladores de v1.x e os ativadores/O3RO de v2.0 continuam sendo componentes **legados**, mantidos para referência. Eles **não são necessários na v3.0**. Use a documentação da release correspondente caso precise recompilar uma versão anterior.

**Observação:** os recursos de tradução são distribuídos no ZIP da release, separadamente do código-fonte gerado automaticamente pelo GitHub.
