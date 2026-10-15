# Build da v1.2.1

Alvo HD: TriAevum v0.8.0-beta.1c, Windows x64. A tradução comum continua restrita às bases RomFS conhecidas. Os novos perfis do Forge usam `${runtime_dir}`; os perfis anteriores com `${profile_dir}` continuam aceitos, sempre dentro da instalação selecionada.

```powershell
python installer/build_installer.py --prepare-only
python -m unittest test_compat_safety test_hd_integration -v
python installer/fetch_hd_runtime.py
python installer/build_installer.py --hd-runtime build/hd-runtime-v1.2.1
```

O runtime HD deve ser recompilado a partir do arquivo `source/TriAevum-source.zip` da beta.1c e do patch `runtime-HD.patch`. Não reutilize o EXE HD da beta.1: ele perderia as correções recentes do TriAevum e não corresponde ao novo plugin do título.

O Actions recebe somente um bundle genérico fixado por SHA-256, sem ROM, plugin privado, saves ou packs de texturas. O job isolado de download tem a permissão necessária para ler o draft técnico. Os jobs de build mantêm acesso de leitura; o job de anexação atualiza somente a release 1.2.1.

Os três ZIPs de instalação e o ZIP opcional de fontes correspondentes são anexados à release. Os hashes ficam na descrição. Os arquivos `.sha256` e relatórios de autoteste permanecem nos artefatos do Actions. Releases anteriores são preservadas.

Linux inclui somente a tradução comum. O autoteste do instalador Linux não equivale à validação funcional dentro do jogo.
