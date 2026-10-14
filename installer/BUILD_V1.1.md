# Instalador v1.1 — builds Windows e Linux

Alvo: TriAevum v0.8.0-beta.1. A release do runtime oferece Windows x64, Linux x86_64 AppImage e Linux x86_64 Flatpak. O mesmo instalador Linux opera sobre o perfil persistente dos dois pacotes. Não são gerados ARM, Android ou macOS porque não constam nessa release.

Os fontes/builds v1.0 permanecem preservados. A v1.1 incorpora o núcleo compatível, a tradução completa, preservação da fonte HD e correção dos aliases de til. Nenhuma nova release é criada automaticamente.

Há uma opção de menus/texturas HD para Windows 0.8 no build com `--hd-runtime`. O build padrão permanece sem esse runtime. Consulte [HD_INTEGRACAO.md](HD_INTEGRACAO.md) para instalação, verificação, rollback e composição do bundle validado.

## Windows

Execute `installer/GERAR_V1.1_WINDOWS.bat`, ou num Python 3.12 x64:

```powershell
python -m pip install -r installer/requirements-build.txt
python installer/build_installer.py
```

O build baixa o asset da release v1.0.0, confere seu SHA-256, extrai somente os 112 arquivos de dados (sem executar o EXE) e compara cada hash com `installer/payload-manifest.json`. Também aceita `--payload caminho/citra/romfs` ou `--source-zip caminho.zip`. `scene/fazer` não integra o pacote.

O PyInstaller gera o binário nativo. O próprio binário executa autoteste do payload, conversão QM e inicialização de Tk antes de ser empacotado com LEIA-ME. ZIP, SHA-256 e relatório ficam em `artifacts/`. Nenhum RomFS ou runtime é incorporado.

## GitHub Actions

Workflow: `.github/workflows/build-installer-compat.yml`, disparo automático ao atualizar os fontes nesta branch; quando o workflow estiver registrado na branch padrão, também permite disparo manual em Actions → Build instalador PT-BR 0.8 → Run workflow, escolhendo `compat/triaevum-0.8.0-beta.1`.

Matriz: `windows-2022` e `ubuntu-22.04`, Python 3.12 x64. Linux usa Xvfb para validar Tk e o executável sem monitor. O build Linux usa glibc do Ubuntu 22.04, portanto requer um sistema compatível com essa versão de glibc ou mais recente. Não se trata de AppImage/Flatpak do instalador: é um executável independente para editar o perfil do TriAevum no host.

Cada job produz um artifact com o pacote ZIP, SHA-256 e autoteste. Permissões `contents: read`, sem secrets e sem publicação de releases. Os testes que dependem de RomFS local não distribuem nem baixam ROM; a comparação da QBF nativa real é pulada em CI quando a instalação não está disponível.

## Uso no Linux

Extraia o ZIP e execute:

```sh
chmod +x OoT3D_PTBR_TriAevum_v1.1.0_Linux-x86_64
./OoT3D_PTBR_TriAevum_v1.1.0_Linux-x86_64
```

A GUI tenta detectar o perfil AppImage/Flatpak e permite selecionar a pasta explicitamente. Se ambos existirem, é preciso escolher. Perfis padrão:

- AppImage: `$XDG_DATA_HOME/TriAevum`, normalmente `~/.local/share/TriAevum`.
- Flatpak: `~/.var/app/io.github.coccofresco.TriAevum/data/TriAevum`.

Selecione a pasta contendo `TriAevum.launch.json` e `data`, depois Verificar status. A validação dos hashes continua obrigatória; um build Linux não prova compatibilidade com toda ROM que o Forge aceita. Não use a antiga GUI Flatpak alpha.2c para a 0.8.

Windows: teste no jogo informado pelo usuário; correção final do til ainda exige conferência visual. Linux AppImage/Flatpak: funcionamento no jogo pendente de testes reais. Feche jogo e Forge antes de instalar ou restaurar.

Referências: [release do TriAevum](https://github.com/coccofresco/TriAevum/releases/tag/v0.8.0-beta.1), [PyInstaller e builds por sistema](https://pyinstaller.org/en/stable/operating-mode.html), [runners GitHub](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
