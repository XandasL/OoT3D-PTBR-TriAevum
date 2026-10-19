"""End-to-end local QBF coverage test using an OFL font in build/open-font."""
import importlib.util
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "installer"))
from prepare_open_font_pack import prepare_local_font_pack


def synthetic_native():
    directory = [(42, 0), (65, 1), (9670, 2)]
    result = bytearray(16 + len(directory) * 8 + 3 * 128)
    result[:4] = b"QBF1"
    struct.pack_into("<HHH", result, 4, len(directory), 3, 42)
    result[12:16] = bytes((4, 16, 16, 2))
    for i, (code, index) in enumerate(directory):
        struct.pack_into("<HH", result, 16 + i * 8, code, index)
        result[16 + i * 8 + 4:16 + i * 8 + 8] = bytes((1, 2, 3, 4))
    return bytes(result)


class OpenFontPackIntegrationTests(unittest.TestCase):
    def test_real_font_produces_triaevum_compatible_pack(self):
        candidates = list((ROOT / "build" / "open-font").glob("*.ttf"))
        if not candidates:
            self.skipTest("A fonte oficial é baixada apenas no pipeline experimental")
        self.assertEqual(len(candidates), 1)
        native = synthetic_native()
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "font_coverage.zip"
            manifest = prepare_local_font_pack(native, candidates[0], archive)
            self.assertEqual(manifest["fonts"][0]["density"], 4)
            with zipfile.ZipFile(archive) as z:
                self.assertEqual(json.loads(z.read("manifest.json"))["format"], "oot3d_qbf_coverage_v1")
                entry = manifest["fonts"][0]
                self.assertEqual(z.read(entry["native_file"]), native)
                hd = z.read(entry["coverage_file"])
                self.assertEqual(hd[:4], b"QBF1")
                self.assertEqual(hd[13:15], bytes((64, 64)))
                self.assertEqual(len(hd), 16 + 3 * 8 + 3 * 2048)
                self.assertEqual(hd[16:40], native[16:40])
                # The generated glyph for A must contain opaque coverage.
                self.assertTrue(any(hd[16 + 24 + 2048:16 + 24 + 4096]))


if __name__ == "__main__":
    unittest.main()
