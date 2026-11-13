#!/usr/bin/env python3
"""Rebuild the 9 repaired scene ZAR from the v3.0 ZIP and original EUR RomFS.

No ROM or translated binary resources are embedded in the repository.
Inputs are read-only; each repaired ZAR must match the published v3.0.1 SHA-256.
"""
from __future__ import annotations
import argparse
import hashlib
import struct
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = "data/mods/custom-romfs/"
EUR_ROOT = "RomFS_Extraida_EUR/"
V3_SHA256 = "5db68dd5ce2d4633028ccbe63e0487446c5dccfe39bd4f27081e450796aece23"
SCENE_SHA256 = {
    "ganontika.zar": "cd0b5ac10d25677246841321ce5bb11ab718d7a8f9145efbfa93a0e275dfa1d7",
    "ganontika_dd.zar": "cd0b5ac10d25677246841321ce5bb11ab718d7a8f9145efbfa93a0e275dfa1d7",
    "ganon_tou.zar": "0a404bb2a06b93329b0e9d91010bd5f0a250791416abd7b8d8a37a2714c12dcb",
    "gerudoway.zar": "5f7a6aba1af69073a6422b2b19aebef5cc561d497d1715246cbf2301f12598cf",
    "hut.zar": "7a3a7909431abb723070adf7734249d9054f03938778d05d724462a5ce196806",
    "kinsuta.zar": "2da994a06d668d2f417c82155e57de11693c092e1134a2b01fde4a4ba2274d25",
    "spot05.zar": "0ee171ddb4dcf33bf7f7d2de18b09e72cbd67f809febffd101da0dc4305af396",
    "spot18.zar": "096a8c57362dd5fa3ad5419f8efe9532037b611bdc16e0d2c499dc41dcc0ea9c",
    "turibori.zar": "f5ed227a32a5836433a5a856480542a33ad37a1d72d07b163c280178fe8c68d0",
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def parse_zar(data: bytes, *, allow_truncated=False):
    if len(data) < 28 or data[:4] != b"ZAR\x01":
        raise ValueError("Invalid ZAR header")
    declared, _, count, _, meta, offsets = struct.unpack_from("<IHHIII", data, 4)
    if not allow_truncated and declared != len(data):
        raise ValueError("ZAR declared size mismatch")
    if not 1 <= count <= 500 or meta + count * 8 > len(data) or offsets + count * 4 > len(data):
        raise ValueError("Invalid ZAR file tables")
    members = []
    for i in range(count):
        size, name_offset = struct.unpack_from("<II", data, meta + 8*i)
        offset = struct.unpack_from("<I", data, offsets + 4*i)[0]
        if name_offset >= len(data):
            raise ValueError("Invalid ZAR filename offset")
        end = data.find(b"\0", name_offset, min(name_offset+250, len(data)))
        if end < 0:
            raise ValueError("Missing ZAR filename terminator")
        name = data[name_offset:end].decode("ascii").replace("\\", "/")
        payload = data[offset:offset+size] if offset + size <= len(data) else None
        if payload is None and not allow_truncated:
            raise ValueError("Truncated ZAR member")
        members.append((name, offset, size, payload))
    if len({m[0] for m in members}) != count:
        raise ValueError("Duplicate ZAR member names")
    return meta, offsets, members

def check_ctxb(data: bytes):
    if (len(data) < 72 or data[:4] != b"ctxb" or
        struct.unpack_from("<I", data, 4)[0] != len(data) or
        data[24:28] != b"tex " or
        struct.unpack_from("<I", data, 8)[0] != 1 or
        struct.unpack_from("<I", data, 32)[0] != 1 or
        struct.unpack_from("<I", data, 36)[0] != len(data)-72):
        raise ValueError("Invalid CTXB container")
    return data[40:56]

def translated_textures(stem, old: ZipFile):
    def read(file): return old.read(ROOT+"scene/"+file)
    if stem in ("ganontika.zar", "ganontika_dd.zar"):
        damaged = read("ganon_tou.zar")
        position = damaged.find(b"ZAR\x01")
        if position != 121440:
            raise ValueError("Unexpected misplaced Ganontika ZAR location")
        _, _, members = parse_zar(damaged[position:position+187160])
    elif stem == "ganon_tou.zar":
        _, _, members = parse_zar(read("ganontika.zar"), allow_truncated=True)
    else:
        _, _, members = parse_zar(read(stem))
    textures = {name: payload for name, _, _, payload in members
                if name.endswith(("_usen.ctxb", "_euen.ctxb"))}
    if (len(textures) != 2 or not any(n.endswith("_usen.ctxb") for n in textures)
            or not any(n.endswith("_euen.ctxb") for n in textures)):
        raise ValueError("Expected exactly two English CTXB")
    for payload in textures.values():
        if payload is None or len(payload) not in (16456, 49224):
            raise ValueError("Missing or malformed translated CTXB")
        check_ctxb(payload)
    return textures

def rebuild_zar(original: bytes, textures: dict[str, bytes]) -> bytes:
    meta, offsets, members = parse_zar(original)
    if set(textures)-{n for n,_,_,_ in members} or len(textures) != 2:
        raise ValueError("Translated texture paths do not match original")
    first = min(offset for _,offset,_,_ in members)
    if first != offsets + 4*len(members):
        raise ValueError("Unsupported ZAR data layout")
    out = bytearray(original[:first])
    for i, (name, _, size, payload) in enumerate(members):
        replacement = textures.get(name, payload)
        if name in textures:
            if (size != 16456 or check_ctxb(payload) != check_ctxb(replacement)
                    or len(replacement) not in (16456, 49224)):
                raise ValueError("Unexpected translated CTXB metadata")
        out.extend(b"\0" * (-len(out) % 4))
        struct.pack_into("<I", out, offsets+4*i, len(out))
        struct.pack_into("<I", out, meta+8*i, len(replacement))
        out.extend(replacement)
    struct.pack_into("<I", out, 4, len(out))
    result = bytes(out)
    _,_,verified = parse_zar(result)
    for before,after in zip(members,verified):
        name,_,_,payload = before
        if after[0] != name or after[3] != textures.get(name,payload):
            raise ValueError("ZAR post-build content mismatch")
    return result

def recover_scenes(eur: ZipFile, v3: ZipFile):
    rebuilt = {}
    for filename, expected in SCENE_SHA256.items():
        original = eur.read(EUR_ROOT+"scene/"+filename)
        data = rebuild_zar(original, translated_textures(filename,v3))
        if digest(data) != expected:
            raise ValueError(f"Output differs from published v3.0.1: {filename}")
        rebuilt[ROOT+"scene/"+filename] = data
    return rebuilt

def write_package(v3_path: Path, eur_path: Path, readme: Path, output: Path):
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    if hashlib.sha256(v3_path.read_bytes()).hexdigest() != V3_SHA256:
        raise ValueError("v3.0 ZIP does not match the validated release")
    instructions = readme.read_bytes()
    if not instructions or b"Custom RomFS" not in instructions:
        raise ValueError("Invalid v3.0.1 LEIA-ME")
    with ZipFile(v3_path) as old, ZipFile(eur_path) as eur:
        rebuilt = recover_scenes(eur, old)
        members = [i for i in old.infolist() if not i.is_dir()]
        if len(members) != 128 or len({i.filename for i in members}) != 128:
            raise ValueError("Unexpected v3.0 file count")
        with output.open("xb") as stream, ZipFile(stream,"w",ZIP_DEFLATED,compresslevel=8) as dest:
            for info in old.infolist():
                if info.is_dir(): dest.writestr(info,b"")
                elif info.filename in rebuilt: dest.writestr(info,rebuilt[info.filename])
                elif info.filename == "LEIA-ME.txt": dest.writestr(info,instructions)
                else: dest.writestr(info,old.read(info.filename))
    with ZipFile(output) as z:
        if z.testzip() is not None:
            raise ValueError("Built ZIP failed CRC")
    return len(rebuilt)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ptbr-v3-zip",type=Path,required=True)
    p.add_argument("--eur-romfs-zip",type=Path,required=True)
    p.add_argument("--readme",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print("Rebuilt scenes:",write_package(a.ptbr_v3_zip,a.eur_romfs_zip,a.readme,a.output))
    print("Overall ZIP SHA-256 may change with ZIP compression/metadata.")

if __name__=="__main__":
    main()
