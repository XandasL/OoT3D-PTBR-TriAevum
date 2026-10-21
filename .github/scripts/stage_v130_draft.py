"""Stage verified installer ZIPs from an already successful build, without rebuilding."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[2]
incoming = root / "incoming"
output = root / "output"
output.mkdir(exist_ok=True)
names = [
    "OoT3D_PTBR_TriAevum_v1.3.0_Windows-x64.zip",
    "OoT3D_PTBR_TriAevum_v1.3.0_Linux-x86_64-AppImage.zip",
    "OoT3D_PTBR_TriAevum_v1.3.0_Linux-x86_64-Flatpak.zip",
]
hashes = {}
for filename in names:
    candidates = list(incoming.rglob(filename))
    if len(candidates) != 1:
        raise RuntimeError(f"Expected exactly one {filename}, got {len(candidates)}")
    source = candidates[0]
    content = source.read_bytes()
    actual = hashlib.sha256(content).hexdigest()
    digest_files = list(incoming.rglob(filename + ".sha256"))
    if len(digest_files) != 1 or digest_files[0].read_text(encoding="utf-8").split()[0] != actual:
        raise RuntimeError(f"SHA256 checksum mismatch for {filename}")
    with zipfile.ZipFile(source) as z:
        members = z.namelist()
        if z.testzip() or len(members) != 5 or len(set(members)) != 5:
            raise RuntimeError(f"Unexpected ZIP contents: {filename}")
        if not {"LEIA-ME.txt", "CREDITOS.txt", "Henriko-5.0a-PTBR/pack.json",
                "Henriko-5.0a-PTBR/LEIA-ME.txt"}.issubset(members):
            raise RuntimeError(f"Missing Henriko/LEIA-ME: {filename}")
        binaries = [p for p in members if p not in {
            "LEIA-ME.txt", "CREDITOS.txt", "Henriko-5.0a-PTBR/pack.json",
            "Henriko-5.0a-PTBR/LEIA-ME.txt"}]
        if len(binaries) != 1 or not binaries[0].startswith("OoT3D_PTBR_TriAevum_v1.3.0_"):
            raise RuntimeError(f"Unexpected installer binary: {filename}")
        if "Windows" in filename and not binaries[0].endswith(".exe"):
            raise RuntimeError("Windows executable missing")
        if "Linux" in filename and binaries[0].endswith(".exe"):
            raise RuntimeError("Linux package contains Windows executable")
        pack = json.loads(z.read("Henriko-5.0a-PTBR/pack.json"))
        if not isinstance(pack, dict) or len(pack.get("textures", {})) != 71:
            raise RuntimeError(f"Expected exactly 71 Henriko aliases: {filename}")
        if "HD 64" not in z.read("LEIA-ME.txt").decode("utf-8"):
            raise RuntimeError(f"HD64 instructions missing: {filename}")
    hashes[filename] = actual
    (output / filename).write_bytes(content)

notes = (root / "installer/RELEASE_NOTES_v1.3.0.md").read_text(encoding="utf-8")
lines = ["", "## Integridade dos arquivos (SHA-256)", "",
         "| Pacote | SHA-256 |", "| --- | --- |"]
for filename in names:
    lines.append(f"| \`{filename}\` | \`{hashes[filename]}\` |")
(output / "release-notes.md").write_text(notes + "\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"verified": hashes, "notes": str(output / "release-notes.md")}, indent=2))
