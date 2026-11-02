# OoT3D PT-BR v2 — portable classic-only release candidate

**Status:** sources consolidated; underlying classic translation and local ZIP tested by the author on TriAevum v0.8.0-beta.1.2. **NOT approved for public release.**

## Scope

Only the classic O3RO (126 replacement records). No modified ChubbyCubby Vanilla UI/HUD, SingleScreen/TopScreen atlas, or legacy Navi overlay. Forge's graphics settings remain unchanged; a user-enabled original HD pack may still show English graphics.

## Local packaging

From this folder:

```powershell
py -3 .\gerar_zip_local.py --classico "E:\path\ptbr-classico-beta12.o3ro" --saida "E:\path\OoT3D-PTBR-v2-LIMPA-TESTE.zip"
```

The local overlay SHA-256 must be `4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3`. The ZIP contains exactly four entries: `Ativar-PTBR.cmd`, `Ativar-PTBR.ps1`, `LEIA-ME.txt` and `data/mods/OoT3D-PTBR/classico.o3ro`. The binary overlay and modified HD images are **not** committed to GitHub.

## Installation (local compatible beta.1.2 setup)

Prepare a legitimate game through Forge; extract the local ZIP to the TriAevum root; run `Ativar-PTBR.cmd`; launch the game. The activator validates the O3RO SHA-256 and sets `--romfs-overlay` in `data/TriAevum.launch.json` while leaving Forge's graphics options untouched. It creates a backup of the profile. Re-running Forge preparation may reset the launch argument. The installer does **not** patch TriAevum.exe or the original RomFS.

## Release gate / rights review

- [x] Classic O3RO with 126 records tested in-game without HD.
- [x] Classic-only ZIP and activator reported working by the author.
- [x] Source tree excludes redistributed HD PNGs and SingleScreen artwork.
- [ ] Verify redistribution permissions for **all game-derived contents embedded in the classic O3RO**. Removing HD PNGs does not grant rights to redistribute the O3RO.
- [ ] Review dependencies and original translation source licenses.
- [ ] Reconfirm version compatibility in a clean beta.1.2 environment before publishing.
- [ ] Publish only when permissions and final artifact audit are complete.

No changes to `main` or historical releases.
