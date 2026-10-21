"""Synthetic regression tests for the optional HD64 A4 coverage profile."""
import importlib.util
from pathlib import Path
import unittest

source = Path(__file__).parent / 'installer' / 'font_atlas_downsample.py'
spec = importlib.util.spec_from_file_location('font_atlas_downsample_test', source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class FontAtlasDownsampleTests(unittest.TestCase):
    def test_white_and_black_preserve_coverage(self):
        black = bytes(128 * 128 // 2)
        white = bytes([0xff]) * (128 * 128 // 2)
        self.assertEqual(mod.half_a4_atlas(black, 1), bytes(64 * 64 // 2))
        self.assertEqual(mod.half_a4_atlas(white, 1), bytes([0xff]) * (64 * 64 // 2))

    def test_2x2_area_average_preserves_edges(self):
        raw = bytearray(128 * 128 // 2)
        raw[0] = 0xF0  # first source row: [15, 0]
        raw[64] = 0x00  # second source row: [0, 0]
        result = mod.half_a4_atlas(raw, 1)
        self.assertEqual(result[0], 0x40)  # round(15/4) = 4
        self.assertTrue(all(v == 0 for v in result[1:]))

    def test_two_glyphs_remain_independent(self):
        glyph_bytes = 128 * 128 // 2
        atlas = bytes(glyph_bytes) + bytes([0xff]) * glyph_bytes
        result = mod.half_a4_atlas(atlas, 2)
        self.assertEqual(result[:2048], bytes(2048))
        self.assertEqual(result[2048:], bytes([0xff]) * 2048)

    def test_rejects_incorrect_size(self):
        with self.assertRaises(ValueError):
            mod.half_a4_atlas(b'bad', 1)
        with self.assertRaises(ValueError):
            mod.half_a4_atlas(bytes(8192), 0)


if __name__ == '__main__':
    unittest.main()
