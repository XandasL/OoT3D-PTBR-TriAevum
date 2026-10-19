"""Empacota cobertura QBF gerada localmente em font_coverage.zip compatível.

O arquivo gerado contém o QBF nativo fornecido pelo usuário: NUNCA
publique este ZIP nem inclua ROM ou QBF original nos instaladores públicos.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

from build_open_hd_qbf import build_hd_qbf, parse_native


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prepare_local_font_pack(native: bytes, font_path: str | Path,
                            output: str | Path) -> dict:
    entries, _ = parse_native(native)
    coverage = build_hd_qbf(native, font_path)
    native_hash, coverage_hash = sha256(native), sha256(coverage)
    native_asset = f"native/{native_hash}.qbf"
    coverage_asset = f"coverage/{coverage_hash}.qbf"
    mappings = [
        {"code": code, "native_glyph": index, "coverage_glyph": index,
         "native_metrics_hex": native[16 + i * 8 + 4:16 + i * 8 + 8].hex()}
        for i, (code, index) in enumerate(entries)
    ]
    manifest = {
        "format": "oot3d_qbf_coverage_v1",
        "runtime_enabled": True,
        "minimum_output_height": 480,
        "status": "native_atlas_coverage_ready",
        "fonts": [{
            "romfs_path": "message/eu/ltn16.qbf",
            "native_file": native_asset,
            "coverage_file": coverage_asset,
            "native_sha256": native_hash,
            "coverage_sha256": coverage_hash,
            "logical_cell": [16, 16],
            "coverage_cell": [64, 64],
            "density": 4,
            "fallback_code": int.from_bytes(native[8:10], "little"),
            "characters": mappings,
            "replacement_metric_differences": 0,
        }],
        "source": "Locally generated from user's native QBF and open-licensed font",
    }
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(output.name + ".partial")
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED) as archive:
            for name, data in sorted(((native_asset, native), (coverage_asset, coverage))):
                archive.writestr(name, data)
            archive.writestr("manifest.json", json.dumps(
                manifest, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8"))
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return manifest


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gera pacote local de fonte HD Noto Sans")
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--font", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prepare_local_font_pack(args.native.read_bytes(), args.font, args.output)
    print(f"Pacote local gerado: {args.output}")
