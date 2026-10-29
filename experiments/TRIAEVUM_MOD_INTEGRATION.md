# TriAevum native mod integration proposal — OoT3D PT-BR

**Status:** proposal for discussion with coccofresco; NOT an implemented Forge feature.
**Target tested:** TriAevum `v0.8.0-beta.1.2`.
**Project:** https://github.com/XandasL/OoT3D-PTBR-TriAevum
**Discussion:** https://github.com/coccofresco/TriAevum/issues/100

## Goal

A user installs/enables **OoT3D Brazilian Portuguese** through TriAevum/Forge, choosing between:
- **Classic PT-BR** — translated dialogue and native-resolution interface textures (no HD texture pack needed).
- **HD PT-BR (recommended)** — translated dialogue and separately authored translated HD UI/HUD + TopScreen atlas.

The translation should be independent of a custom executable, standalone installer, and manual launch-profile editing. Existing TriAevum files and executable must not be patched by the mod distribution mechanism.

## Verified evidence from local beta.1.2 tests

| Variant | Result | Notes |
| --- | --- | --- |
| Classic | **Passed in-game**, no HD textures installed | O3RO with **126 RomFS replacement records**, translated dialogue/menu/native UI. |
| HD | **Passed in-game** in the author's earlier setup | O3RO with **95 records**, excludes 28 menu CTXB destinations and 3 logo CTXBs; translated Vanilla UI/HUD PNGs and TopScreen atlas loaded in-game. |
| Independent HD pack | **Prepared locally**, activation profile updated | The separate copied pack has **not been conclusively isolated from previously modified base textures** in an in-game test. Do not claim standalone pack acceptance verified. |

The generator checks 112 source files against `installer/payload-manifest.json`, converts USA message data to EUR form, preserves the native font, and verifies the exact beta.1.2 RomFS SHA-256:
`dae620379c805e96a6187c212dc2b177cf5fdb0c184d526a06ebaeeaa481aa56`.

Local test artifacts (not published): `ptbr-classico-beta12.o3ro` with 126 replacement records (SHA-256 `4b2dc3e7734518200f8bf5483f74f16353da939b3914ab3986f1e20968eed9e3`); `ptbr-hd-beta12.o3ro` with 95 records (SHA-256 `e831239df529d1c97b240216a888519c40ddc1b72adcb2e6fcb20547710e81f4`). Both are tied to the validated base and must NOT be applied blindly to different RomFS builds.

HD work comprises 20 translated Vanilla UI/HUD PNGs plus a TopScreen atlas. The atlas is byte-identical to the translated Vanilla texture `tex1_512x256_1FAF9B5B2ADF6038_13_mip0.png` and can be referenced without storing a second copy.

## Relevant upstream mechanisms

- `tools/triaevum_release/romfs_mods.py`: catalogued optional RomFS mods, `config/romfs_mods.json`, Forge preparation, O3RO generation; **closed `CATALOG` in beta.1.2**, not a generic external-mod-folder scanner.
- `--romfs-overlay`: runtime selects a prepared O3RO. Merely placing an O3RO under `data/mods` does not activate it.
- `--ui-texture-pack`: prepared Vanilla UI/HUD texture tree, including language-specific folders and `common`.
- `--topscreen-ui-atlas-hd`: separate explicit atlas path.
- The user's custom Azahar textures take precedence over Forge's built-in base UI pack where applicable; this does **not** by itself guarantee that HD textures win against altered CTXB hash identities from a full RomFS overlay.
- Forge's original `source.json` texture receipt is integrity-pinned. A copied/edited pack must not be presented as a Forge-verified original.

See upstream `docs/TRIAEVUM_UI_TEXTURE_PACK.md` at the beta.1.2 tag for loader details.

## Requested native integration

1. Provide an official documented external-mod package/manifest format (format and fields **to be chosen by upstream**, not the example below as a presumed standard).
2. Allow the user to enable the PT-BR mod in Forge and choose **Classic** or **HD** (HD recommended), with one prepare/start flow.
3. On preparation, verify source-game identity and generate the variant-appropriate O3RO from verified replacement assets. Never assume the prebuilt beta.1.2 O3RO is portable across game versions.
4. In HD mode, activate translated Vanilla UI/HUD and TopScreen assets via existing texture facilities, taking account of language-specific hash matches and ensuring translated HD assets are shown.
5. Keep user-supplied custom textures highest priority where supported; explicitly define collision/priority rules with other RomFS mods.
6. Do not require replacing/modifying the TriAevum executable or editing the launch profile by hand.
7. Clearly report missing/incompatible files and avoid partially activated mods.

### Compatibility question for coccofresco

Can Forge support a user-provided external mod with **two selectable profiles** that uses both a RomFS overlay and HD texture assets, or is there a preferred way to register such a package with the current Forge catalog? Which upstream metadata/manifest contract should we target?

### Unresolved technical issue: 126 records + HD

The full native overlay replaces 28 menu CTXB paths (US + EUR mirrors) and 3 logo CTXB paths that were excluded from the 95-record HD variant. These can change the texture lookup identities and prevent HD overrides. **Never claim that a full 126-record overlay automatically produces HD-first rendering.** Until confirmed upstream, retain separate Classic (126) and HD (95) profiles; consider a unified base only after proving deterministic texture priority.

## Publishing and licensing

- The original Vanilla UI/HUD 3.2 texture pack is credited to its respective authors and distributed under **CC BY-NC-ND 4.0**. Do **not** publish the altered derivative HD PNGs or bundle the upstream originals without clear permission.
- Do not upload a prebuilt overlay that incorporates third-party translated assets until each asset's license and publication rights have been checked.
- A public repository may include the **documentation, manifests, mapping rules, source-code tools and reproducible tests** without publishing restricted image files.
- A future compliant delivery may require the user's own legally obtained source material and locally generated overlays, or direct authorization for distributing derivatives.

## Acceptance tests for a future Forge integration

- [x] Classic O3RO with 126 records tested in a clean beta.1.2 installation without HD textures.
- [x] HD mode with 95 records and translated visuals tested in the existing working setup.
- [ ] External mod detected and enabled in Forge without an installer/script.
- [ ] HD mode isolated test on clean original Forge texture pack.
- [ ] Full 126-record overlay + HD priority confirmed, or deliberately unsupported.
- [ ] Native/HD selection persists through Forge preparation.
- [ ] User texture priority and compatibility with other enabled mods verified.
- [ ] Permissions for distribution of altered third-party HD assets clarified.
- [ ] Multi-version compatibility/identity checks validated.

## Local development references

- `experiments/build_ptbr_o3ro_beta12.py`
- `experiments/test_ptbr_o3ro_hd_exclusions.py`
- `experiments/prepare_ptbr_hd_mod_beta12.py`
- `experiments/test_prepare_ptbr_hd_mod_beta12.py`
- `experiments/README_MOD_LOCAL_PTBR_HD_BETA12.md`

This document is intended as a concise technical handoff, not a request for the upstream developer to maintain the translation content.
