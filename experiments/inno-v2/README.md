# Inno Setup v2 prototype

Prototype sources for the TriAevum v0.8.0-beta.1.2 PT-BR local test installer.

Download the complete experimental source bundle from the accompanying ChatGPT artifact to obtain the .iss, PowerShell activator and payload staging script. Do not publish the locally generated payload: the edited Vanilla UI/HUD images require redistribution permission.

The installer copies the two validated O3RO files and a locally staged HD pack, then calls the Forge-aware auto-selector for the appropriate mode. No TriAevum.exe/ROMFS modification. This version has **not** been compiled or tested using Inno Setup on Windows yet; verify before release.
