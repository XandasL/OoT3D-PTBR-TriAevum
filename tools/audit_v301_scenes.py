#!/usr/bin/env python3
"""Read-only audit of 76 translated scene ZAR in the v3.0.1 release.

Requires locally supplied EUR RomFS, v3.0 and v3.0.1 ZIPs.
Validates structural integrity, original nontranslated resources and
the nine reconstructed ZAR hashes. Does not guarantee full gameplay testing.
"""
from __future__ import annotations
import argparse
import hashlib
from collections import Counter
from pathlib import Path
from zipfile import ZipFile
from rebuild_v301_scenes import ROOT, EUR_ROOT, SCENE_SHA256, parse_zar, check_ctxb

def audit(v301: Path, eur: Path, v3: Path):
    counts = Counter()
    with ZipFile(v301) as patched, ZipFile(eur) as original, ZipFile(v3) as old:
        if patched.testzip() is not None:
            raise ValueError("ZIP CRC failed")
        names = sorted(n for n in patched.namelist()
                       if n.startswith(ROOT+"scene/") and n.endswith(".zar"))
        if len(names) != 76:
            raise ValueError(f"Expected 76 scenes, found {len(names)}")
        for path in names:
            filename = path.rsplit("/",1)[-1]
            original_bytes = original.read(EUR_ROOT+"scene/"+filename)
            translated_bytes = patched.read(path)
            meta_a, offsets_a, a = parse_zar(original_bytes)
            meta_b, offsets_b, b = parse_zar(translated_bytes)
            if (meta_a,offsets_a) != (meta_b,offsets_b) or [x[0] for x in a] != [x[0] for x in b]:
                raise ValueError(f"Scene member tables differ: {filename}")
            first_a, first_b = min(x[1] for x in a), min(x[1] for x in b)
            if first_a != first_b:
                raise ValueError(f"Scene data table offset differs: {filename}")
            head_a,head_b = bytearray(original_bytes[:first_a]),bytearray(translated_bytes[:first_b])
            for header,meta,offsets in ((head_a,meta_a,offsets_a),(head_b,meta_b,offsets_b)):
                header[4:8]=b"\0"*4
                for i in range(len(a)):
                    header[meta+i*8:meta+i*8+4]=b"\0"*4
                    header[offsets+i*4:offsets+i*4+4]=b"\0"*4
            if any(x!=y and (x,y)!=(92,47) for x,y in zip(head_a,head_b)):
                raise ValueError(f"Unexpected nonresource ZAR metadata change: {filename}")
            changed = []
            for before,after in zip(a,b):
                name,_,size,data = before
                if after[1]%4:
                    raise ValueError(f"Unaligned resource: {filename}/{name}")
                if name.endswith(".ctxb"):
                    check_ctxb(data)
                    check_ctxb(after[3])
                if data != after[3]:
                    if not name.endswith(("_usen.ctxb","_euen.ctxb")):
                        raise ValueError(f"Unexpected modified resource: {filename}/{name}")
                    if size != 16456 or len(after[3]) not in (16456,49224):
                        raise ValueError(f"Unexpected CTXB size: {filename}/{name}")
                    if check_ctxb(data) != check_ctxb(after[3]):
                        raise ValueError(f"CTXB metadata changed: {filename}/{name}")
                    counts["translated_ctxb"] += 1
                    changed.append(name)
            if len(changed)!=2 or not any(n.endswith("_usen.ctxb") for n in changed) or not any(n.endswith("_euen.ctxb") for n in changed):
                raise ValueError(f"Missing translated CTXB pair: {filename}")
            if filename in SCENE_SHA256:
                if hashlib.sha256(translated_bytes).hexdigest()!=SCENE_SHA256[filename]:
                    raise ValueError(f"Rebuilt scene hash differs: {filename}")
                counts["rebuilt_scenes"] += 1
            elif translated_bytes != old.read(path):
                raise ValueError(f"Previously working scene changed: {filename}")
            else:
                counts["retained_scenes"] += 1
        files = {n for n in patched.namelist() if not n.endswith("/")}
        old_files = {n for n in old.namelist() if not n.endswith("/")}
        if files != old_files:
            raise ValueError("Release file set changed")
        for n in files:
            if n == "LEIA-ME.txt" or n.startswith(ROOT+"scene/"):
                continue
            if patched.read(n)!=old.read(n):
                raise ValueError(f"Unexpected change outside scenes: {n}")
        counts["scenes"] = len(names)
        return dict(counts)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v301-zip",type=Path,required=True)
    p.add_argument("--eur-romfs-zip",type=Path,required=True)
    p.add_argument("--ptbr-v3-zip",type=Path,required=True)
    a=p.parse_args()
    print("OK:",audit(a.v301_zip,a.eur_romfs_zip,a.ptbr_v3_zip))

if __name__ == "__main__":
    main()
