# Build da v1.2.0

O workflow gera Windows x64 com HD opcional e duas variantes do instalador Linux (AppImage/Flatpak). Linux nÃ£o inclui o runtime HD Windows. O nÃºcleo e os 112 arquivos de traduÃ§Ã£o permanecem validados por hash.

```powershell
python installer/build_installer.py --prepare-only
python -m unittest test_compat_safety test_hd_integration -v
python installer/fetch_hd_runtime.py
python installer/build_installer.py --hd-runtime build/hd-runtime-v1.2
```

O bundle genÃ©rico Ã© um asset do draft da v1.2.0, fixado por SHA-256 em hd-runtime-download.json. O download exige GITHUB_TOKEN para drafts. Nenhuma credencial Ã© gravada nos artefatos. O bundle inclui os fontes correspondentes, runtime-HD.patch e avisos/licenÃ§as; nÃ£o contÃ©m ROM, plugin privado de jogo, saves ou PNGs.

Depois dos testes, o Actions anexa os trÃªs ZIPs finais e seus checksums ao draft da 1.2.0. A publicaÃ§Ã£o Ã© manual. [CrÃ©ditos dos packs](TEXTURAS_CREDITOS.md).

Para aplicar o patch ao arquivo de fontes original (que inclui finais de linha Windows), use: `git apply --ignore-whitespace runtime-HD.patch`. A aplicaÃ§Ã£o foi validada nos 13 arquivos alterados.

## Distribuição simplificada

O ZIP do usuário contém o instalador, instruções, créditos e licenças. Os fontes correspondentes são oferecidos separadamente em `OoT3D_PTBR_TriAevum_v1.2.0_Fontes-HD.zip`, na mesma release, sem custo. O runtime técnico do Actions permanece em draft interno separado. Os hashes aparecem na descrição da release; os arquivos `.sha256` ficam apenas nos artefatos do Actions.
