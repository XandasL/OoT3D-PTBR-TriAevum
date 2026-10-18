# Build de teste da v1.2.1 — TriAevum beta.1.1

Alvo HD: **TriAevum v0.8.0-beta.1.1, Windows x64**. A tradução comum continua restrita às bases RomFS conhecidas. Os perfis do Forge usam os caminhos reconhecidos pelo instalador.

```powershell
python installer/build_installer.py --prepare-only
python -m unittest test_compat_safety test_hd_integration test_hd_font_discovery -v
python installer/prepare_hd_native_runtime.py --output build/hd-runtime-v1.2.1
python installer/build_installer.py --hd-runtime build/hd-runtime-v1.2.1
```

A beta.1.1 já inclui o resolvedor de texturas da interface. O bundle HD desta branch contém apenas um manifesto e avisos; não incorpora o executável antigo da beta.1c. Na instalação, o componente exige o SHA-256 publicado do `TriAevum.exe` da beta.1.1 e das DLLs dependentes. Somente após validar também a tradução e o RomFS, copia o executável local validado para `TriAevum-PTBR-HD.exe` e cria o perfil/configuração isolados.

O modo nativo evita substituir o plugin, as DLLs ou o runtime atual por binários de versão anterior. O executável original e seus arquivos não são alterados. A referência de código-fonte é a tag oficial beta.1.1: https://github.com/coccofresco/TriAevum/tree/v0.8.0-beta.1.1.

Os builds e autotestes Linux não equivalem a validação funcional dentro do jogo. A build Windows deve ser testada em uma instalação beta.1.1 limpa, com o pack mesclado e validado, antes de se considerar o comportamento HD confirmado.
