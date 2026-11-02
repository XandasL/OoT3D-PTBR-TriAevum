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
- [x] Original translators' permission is documented in `installer/CREDITOS.txt`, with attribution required; the port author has independently reconfirmed authorization.
- [ ] Include the existing translator credits **inside** the final portable ZIP, not only as a repository reference.
- [ ] Perform a scoped final publication review of the O3RO's game-derived content, distinct from the translators' permission; do not conflate this with the excluded third-party HD textures.
- [x] Classic translation and clean portable ZIP tested by the author on beta.1.2.
- [ ] Run final packager tests after the credits are added.
- [ ] Publish only when permissions and final artifact audit are complete.

No changes to `main` or historical releases.

For a nonredundant status and decision record, see [ESTADO_CONSOLIDADO.md](ESTADO_CONSOLIDADO.md).
