import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

CORE = Path(__file__).parent / "installer" / "Instalador_Traducao_PTBR_OoT3D_V4_compat_test.py"
SPEC = importlib.util.spec_from_file_location("oot3d_ptbr_core_font_test", CORE)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)


class HdFontDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        core.BASE = self.root

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def make_native_qbf(include_tilde_codepoints=False):
        codes = list(range(32, 127))
        european = [
            code for code in range(0xA1, 0x100)
            if code not in ({0x00C3, 0x00D5, 0x00E3, 0x00F5}
                            if not include_tilde_codepoints else set())
        ]
        codes.extend(european)
        if include_tilde_codepoints:
            codes.extend([0x00C3, 0x00D5, 0x00E3, 0x00F5])
        while len(codes) < 199:
            candidate = 0x0100 + len(codes)
            if candidate not in codes:
                codes.append(candidate)
        codes = codes[:199]
        assert len(codes) == 199 and len(set(codes)) == 199

        width = height = 16
        glyph_count = 208
        glyphs = [[0] * (width * height) for _ in range(glyph_count)]
        code_to_glyph = {code: index for index, code in enumerate(codes)}

        def put(code, x, y, value=15):
            glyphs[code_to_glyph[code]][y * width + x] = value

        # Simple test shapes for the four base vowels and the native '~'.
        for code in (ord('a'), ord('o'), ord('A'), ord('O')):
            for x in range(5, 10):
                put(code, x, 7)
                put(code, x, 12)
            for y in range(8, 12):
                put(code, 5, y)
                put(code, 9, y)
            if code in (ord('A'), ord('O')):
                for x in range(4, 11):
                    put(code, x, 4)
                put(code, 4, 5)
                put(code, 10, 5)

        tilde_code = ord('~')
        for x, y in ((4, 5), (5, 4), (6, 4), (7, 5),
                     (8, 5), (9, 4), (10, 4), (11, 5)):
            put(tilde_code, x, y, 12)

        if include_tilde_codepoints:
            for alias, target, base in (
                (ord('ä'), ord('ã'), ord('a')),
                (ord('ö'), ord('õ'), ord('o')),
                (ord('Ä'), ord('Ã'), ord('A')),
                (ord('Ö'), ord('Õ'), ord('O')),
            ):
                base_pixels = list(glyphs[code_to_glyph[base]])
                for x, y in ((4, 2), (5, 1), (6, 1), (7, 2),
                             (8, 2), (9, 1), (10, 1), (11, 2)):
                    base_pixels[y * width + x] = 12
                glyphs[code_to_glyph[target]] = base_pixels

        header = bytearray(struct.pack(
            "<4sHHIBBBB", b"QBF1", len(codes), glyph_count, 0,
            4, width, height, 4
        ))
        metadata = bytearray()
        for index, code in enumerate(codes):
            metadata.extend(struct.pack("<HHBBH", code, index, 0, 0, 0))

        bitmap_data = bytearray()
        for pixels in glyphs:
            for i in range(0, len(pixels), 2):
                bitmap_data.append(((pixels[i] & 0x0F) << 4) | (pixels[i + 1] & 0x0F))
        return bytes(header + metadata + bitmap_data)

    @staticmethod
    def qbf_glyph(data, codepoint):
        count = struct.unpack_from("<H", data, 4)[0]
        glyph_count = struct.unpack_from("<H", data, 6)[0]
        bpp, width, height = data[12], data[13], data[14]
        table = {}
        for index in range(count):
            offset = 16 + index * 8
            code, glyph = struct.unpack_from("<HH", data, offset)
            table[code] = glyph
        glyph = table[codepoint]
        start = 16 + count * 8 + glyph * (width * height * bpp // 8)
        return data[start:start + (width * height * bpp // 8)]

    @staticmethod
    def write_o3tu(path, entries):
        raw = bytearray(b"O3TU" + struct.pack("<III", 2, len(entries), 0))
        for original_hash, payload in entries:
            replacement_hash = core.fnv1a64(payload)
            raw.extend(struct.pack("<QQI", original_hash, replacement_hash, len(payload)))
            raw.extend(payload)
        path.write_bytes(raw)
        return path

    def test_discovers_forge_imported_font_coverage(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        imported = topscreen / "singlescreen-31-content-key"
        imported.mkdir(parents=True)
        pack = imported / "font_coverage.zip"
        pack.write_bytes(b"test-pack")
        o3tu = topscreen / "active-profile" / "atlas_overrides.o3tu"
        o3tu.parent.mkdir(parents=True)
        o3tu.write_bytes(b"")
        # Windows may represent the same temporary directory using its 8.3
        # short path in one Path and the long path in another.
        self.assertTrue(core.locate_hd_font_pack(o3tu).samefile(pack))

    def test_prefers_known_legacy_pack_when_both_layouts_exist(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        legacy_dir = topscreen / "active-profile"
        imported_dir = topscreen / "imported-profile"
        legacy_dir.mkdir(parents=True)
        imported_dir.mkdir(parents=True)
        o3tu = legacy_dir / "atlas_overrides.o3tu"
        o3tu.write_bytes(b"")
        legacy = legacy_dir / "font_coverage.zip"
        legacy.write_bytes(b"legacy-known")
        (imported_dir / "font_coverage.zip").write_bytes(b"imported")
        original_sha = core.HD_FONT_PACK_SHA256
        try:
            core.HD_FONT_PACK_SHA256 = core.sha256_file(legacy)
            self.assertTrue(core.locate_hd_font_pack(o3tu).samefile(legacy))
        finally:
            core.HD_FONT_PACK_SHA256 = original_sha

    def test_identifies_menu_top_when_another_known_hash_is_present(self):
        # Simulate TopScreen 3.1 containing an additional entry whose original
        # hash is known, but whose replacement is not the English menu_top.
        english_payload = b"expected English menu_top payload"
        other_payload = b"another valid override payload"
        original_fnv = core.fnv1a64
        other_replacement = 0x123456789ABCDEF0

        def test_fnv(data):
            if data == english_payload:
                return core.O3TU_ENGLISH_REPLACEMENT_HASH
            if data == other_payload:
                return other_replacement
            return original_fnv(data)

        entries = (
            (core.O3TU_OLD_ORIGINAL_HASH, core.O3TU_ENGLISH_REPLACEMENT_HASH, english_payload),
            (core.O3TU_PTBR_ORIGINAL_HASH, other_replacement, other_payload),
        )
        raw = bytearray(b"O3TU" + struct.pack("<III", 2, len(entries), 1))
        for original, replacement, payload in entries:
            raw.extend(struct.pack("<QQI", original, replacement, len(payload)))
            raw.extend(payload)

        name = b"Base"
        profile_data = b"profile texture"
        raw.extend(struct.pack(
            "<IHHB3xIQ", len(name), 1, 1, 0, len(profile_data),
            original_fnv(profile_data)
        ))
        raw.extend(name)
        raw.extend(profile_data)

        path = self.root / "atlas_overrides.o3tu"
        path.write_bytes(raw)
        with patch.object(core, "fnv1a64", side_effect=test_fnv):
            _, entry = core.inspect_topscreen(path)

        self.assertEqual(entry["original"], core.O3TU_OLD_ORIGINAL_HASH)
        self.assertEqual(entry["replacement"], core.O3TU_ENGLISH_REPLACEMENT_HASH)

    def test_accepts_version_specific_menu_top_replacement(self):
        # The newer TriAevum pack can use a different replacement asset hash.
        # The active source texture identity is the reliable selector.
        path = self.root / "atlas_overrides.o3tu"
        replacement = b"SingleScreen 3.1 menu_top replacement"
        self.write_o3tu(path, [(core.O3TU_OLD_ORIGINAL_HASH, replacement)])

        _, entry = core.inspect_topscreen(
            path, expected_original_hash=core.O3TU_OLD_ORIGINAL_HASH
        )
        self.assertEqual(entry["original"], core.O3TU_OLD_ORIGINAL_HASH)
        self.assertEqual(entry["replacement"], core.fnv1a64(replacement))
        self.assertNotEqual(entry["replacement"], core.O3TU_ENGLISH_REPLACEMENT_HASH)

    def test_missing_menu_top_override_is_a_safe_noop(self):
        path = self.root / "atlas_overrides.o3tu"
        replacement = b"An unrelated valid override"
        unrelated_original = 0x1020304050607080
        self.write_o3tu(path, [(unrelated_original, replacement)])
        before = path.read_bytes()
        backup = self.root / "atlas_overrides.o3tu.antes_traducao_ptbr_v4"

        _, entry = core.inspect_topscreen(
            path, expected_original_hash=core.O3TU_OLD_ORIGINAL_HASH,
            allow_missing=True
        )
        self.assertIsNone(entry)

        mode, index = core.patch_topscreen_to_ptbr(path, backup)
        self.assertEqual(mode, "not_present")
        self.assertIsNone(index)
        self.assertFalse(backup.exists())
        self.assertEqual(path.read_bytes(), before)

    def test_rejects_preexisting_ptbr_gate_without_installed_marker(self):
        path = self.root / "atlas_overrides.o3tu"
        self.write_o3tu(path, [(core.O3TU_PTBR_ORIGINAL_HASH, b"existing PT-BR override")])
        with self.assertRaisesRegex(RuntimeError, "já contém o hash-gate PT-BR"):
            core.inspect_topscreen(
                path, expected_original_hash=core.O3TU_OLD_ORIGINAL_HASH,
                allow_missing=True
            )

    def test_patches_only_original_hash_for_version_specific_replacement(self):
        path = self.root / "atlas_overrides.o3tu"
        backup = self.root / "atlas_overrides.o3tu.antes_traducao_ptbr_v4"
        replacement = b"SingleScreen 3.1 menu_top replacement"
        self.write_o3tu(path, [(core.O3TU_OLD_ORIGINAL_HASH, replacement)])
        original = path.read_bytes()

        mode, index = core.patch_topscreen_to_ptbr(path, backup)
        self.assertEqual(mode, "patched")
        self.assertEqual(index, 0)
        self.assertEqual(backup.read_bytes(), original)

        _, entry = core.inspect_topscreen(
            path, expected_original_hash=core.O3TU_PTBR_ORIGINAL_HASH
        )
        self.assertEqual(entry["original"], core.O3TU_PTBR_ORIGINAL_HASH)
        self.assertEqual(entry["payload"], replacement)
        self.assertEqual(entry["replacement"], core.fnv1a64(replacement))

    def test_optional_lookup_returns_none_when_hd_pack_is_absent(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        topscreen.mkdir(parents=True)
        o3tu = topscreen / "atlas_overrides.o3tu"
        o3tu.write_bytes(b"test-o3tu")
        self.assertIsNone(core.locate_hd_font_pack(o3tu, required=False))
        with self.assertRaisesRegex(RuntimeError, "ativar fontes HD"):
            core.locate_hd_font_pack(o3tu)

    def test_beta_without_hd_pack_keeps_native_font_and_alias_mode(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        topscreen.mkdir(parents=True)
        (topscreen / "atlas_overrides.o3tu").write_bytes(b"test-o3tu")
        native = self.make_native_qbf(include_tilde_codepoints=False)
        romfs = self.root / "romfs.bin"
        romfs.write_bytes(native)
        old_digest = core.EXPECTED_CLEAN_ROMFS_SHA256
        old_native = core.PRESERVED_NATIVE_FONT
        old_layout = core.NATIVE_FONT_LAYOUT
        old_enabled = core.HD_FONT_COVERAGE_ENABLED
        try:
            core.EXPECTED_CLEAN_ROMFS_SHA256 = core.BETA_ROMFS_SHA256
            # The active beta.1.1 O3TU path is read from the launch profile;
            # inject the temporary fixture directly for this focused font test.
            with patch.object(core, "locate_o3tu", return_value=topscreen / "atlas_overrides.o3tu"):
                core.validate_hd_font(
                    romfs, {"message/eu/ltn16.qbf": {"absolute": 0, "size": len(native)}}
                )
            patched = core.PRESERVED_NATIVE_FONT
            self.assertIsNotNone(patched)
            self.assertNotEqual(patched, native)
            self.assertEqual(len(patched), len(native))
            self.assertEqual(patched[:1608], native[:1608])
            self.assertEqual(core.NATIVE_FONT_LAYOUT, native)
            self.assertFalse(core.HD_FONT_COVERAGE_ENABLED)

            # The aliased characters should now use newly composed tilde
            # accents, without changing the base vowels or unrelated glyphs.
            for alias, base in (
                (ord('ä'), ord('a')), (ord('ö'), ord('o')),
                (ord('Ä'), ord('A')), (ord('Ö'), ord('O'))
            ):
                alias_bitmap = self.qbf_glyph(patched, alias)
                base_bitmap = self.qbf_glyph(native, base)
                self.assertNotEqual(alias_bitmap, self.qbf_glyph(native, alias))
                self.assertNotEqual(alias_bitmap, base_bitmap)
            self.assertEqual(self.qbf_glyph(patched, ord('Z')), self.qbf_glyph(native, ord('Z')))
        finally:
            core.EXPECTED_CLEAN_ROMFS_SHA256 = old_digest
            core.PRESERVED_NATIVE_FONT = old_native
            core.NATIVE_FONT_LAYOUT = old_layout
            core.HD_FONT_COVERAGE_ENABLED = old_enabled

    def test_native_qbf_uses_existing_real_tilde_glyphs_when_available(self):
        native = self.make_native_qbf(include_tilde_codepoints=True)
        patched = core.patch_native_font_tilde_aliases(native)
        self.assertEqual(len(patched), len(native))
        for alias, target in (
            (ord('ä'), ord('ã')), (ord('ö'), ord('õ')),
            (ord('Ä'), ord('Ã')), (ord('Ö'), ord('Õ'))
        ):
            self.assertEqual(
                self.qbf_glyph(patched, alias),
                self.qbf_glyph(native, target)
            )

    def test_reports_missing_font_pack_with_actionable_message(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        topscreen.mkdir(parents=True)
        o3tu = topscreen / "atlas_overrides.o3tu"
        o3tu.write_bytes(b"")
        with self.assertRaisesRegex(RuntimeError, "ativar fontes HD"):
            core.locate_hd_font_pack(o3tu)


if __name__ == "__main__":
    unittest.main()
