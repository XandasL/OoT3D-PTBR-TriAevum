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
    # Source alpha occupies x=3..10, y=4..12 for each mapped glyph.
    # Spatial provenance, not artwork, is needed for alignment regression.
    directory_end = 16 + len(directory) * 8
    for index in range(3):
        for y in range(4, 13):
            for x in range(3, 11):
                p = directory_end + index * 128 + (y * 16 + x) // 2
                if x % 2:
                    result[p] |= 0x0F
                else:
                    result[p] |= 0xF0
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
                # Global baseline remains stable; no glyph is expanded
                # anisotropically to match a native ink rectangle.
                alpha = [v for byte in hd[16 + 24 + 2048:16 + 24 + 4096]
                         for v in (byte >> 4, byte & 15)]
                locations = [(i % 64, i // 64) for i, v in enumerate(alpha) if v]
                self.assertGreater(len(locations), 0)
                self.assertGreaterEqual(min(x for x, y in locations), 4)
                self.assertLess(max(x for x, y in locations), 64)
                self.assertGreaterEqual(min(y for x, y in locations), 0)
                self.assertLess(max(y for x, y in locations), 64)

    def test_compact_profile_scales_all_glyphs_equally(self):
        from PIL import Image
        from build_open_hd_qbf import _compact_mask, COMPACT_X_SCALE
        a = Image.new("L", (40, 32), 255)
        b = Image.new("L", (10, 32), 255)
        compact_a = _compact_mask(a)
        compact_b = _compact_mask(b)
        self.assertEqual(compact_a.height, a.height)
        self.assertEqual(compact_b.height, b.height)
        self.assertAlmostEqual(compact_a.width / a.width, COMPACT_X_SCALE, delta=.03)
        self.assertLessEqual(abs(compact_b.width / b.width - COMPACT_X_SCALE), 0.5 / b.width)
        self.assertGreater(compact_a.width, compact_b.width)

    def test_uniform_em_keeps_i_narrower_than_m(self):
        from build_open_hd_qbf import build_hd_qbf
        candidates = list((ROOT / "build" / "open-font").glob("*.ttf"))
        if not candidates:
            self.skipTest("Requires official font downloaded by the workflow")
        codes = (65, 72, 105, 109)  # A H i m
        native = bytearray(16 + len(codes) * 8 + len(codes) * 128)
        native[:4] = b"QBF1"
        struct.pack_into("<HHH", native, 4, len(codes), len(codes), 65)
        native[12:16] = bytes((4, 16, 16, 2))
        for idx, code in enumerate(codes):
            struct.pack_into("<HH", native, 16 + idx * 8, code, idx)
            # Deliberately equal native rectangle dimensions for all letters.
            for y in range(4, 12):
                for x in range(3, 10):
                    offset = 16 + len(codes) * 8 + idx * 128 + (16 * y + x) // 2
                    native[offset] |= 0x0F if x % 2 else 0xF0
        hd = build_hd_qbf(bytes(native), candidates[0])
        def ink_box(index):
            start = 16 + len(codes) * 8 + index * 2048
            alphas = [value for byte in hd[start:start + 2048]
                      for value in (byte >> 4, byte & 15)]
            points = [(p % 64, p // 64) for p, v in enumerate(alphas) if v]
            return (min(x for x, y in points), min(y for x, y in points),
                    max(x for x, y in points) + 1, max(y for x, y in points) + 1)
        a, h, i, m = (ink_box(n) for n in range(4))
        self.assertLess(i[2] - i[0], m[2] - m[0])
        self.assertLess(i[2] - i[0], h[2] - h[0])
        self.assertLess(abs((a[3] - a[1]) - (h[3] - h[1])), 8)
        self.assertEqual(a[3], h[3])  # shared typographic baseline



if __name__ == "__main__":
    unittest.main()
