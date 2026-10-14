# Build da v1.2.0

O workflow gera Windows x64 com HD opcional e duas variantes do instalador Linux (AppImage/Flatpak). Linux não inclui o runtime HD Windows. O núcleo e os 112 arquivos de tradução permanecem validados por hash.

```powershell
python installer/build_installer.py --prepare-only
python -m unittest test_compat_safety test_hd_integration -v
python installer/fetch_hd_runtime.py
python installer/build_installer.py --hd-runtime build/hd-runtime-v1.2
```

O bundle genérico é um asset do draft da v1.2.0, fixado por SHA-256 em hd-runtime-download.json. O download exige GITHUB_TOKEN para drafts. Nenhuma credencial é gravada nos artefatos. O bundle inclui os fontes correspondentes, runtime-HD.patch e avisos/licenças; não contém ROM, plugin privado de jogo, saves ou PNGs.

Depois dos testes, o Actions anexa os três ZIPs finais e seus checksums ao draft da 1.2.0. A publicação é manual. [Créditos dos packs](TEXTURAS_CREDITOS.md).

Para aplicar o patch ao arquivo de fontes original (que inclui finais de linha Windows), use: `git apply --ignore-whitespace runtime-HD.patch`. A aplicação foi validada nos 13 arquivos alterados.
