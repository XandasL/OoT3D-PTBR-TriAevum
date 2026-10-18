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
        native = bytearray(28232)
        native[:4] = b"QBF1"
        struct.pack_into("<H", native, 4, 199)
        romfs = self.root / "romfs.bin"
        romfs.write_bytes(native)
        old_digest = core.EXPECTED_CLEAN_ROMFS_SHA256
        old_native = core.PRESERVED_NATIVE_FONT
        old_enabled = core.HD_FONT_COVERAGE_ENABLED
        try:
            core.EXPECTED_CLEAN_ROMFS_SHA256 = core.BETA_ROMFS_SHA256
            # The active beta.1.1 O3TU path is read from the launch profile;
            # inject the temporary fixture directly for this focused font test.
            with patch.object(core, "locate_o3tu", return_value=topscreen / "atlas_overrides.o3tu"):
                core.validate_hd_font(
                    romfs, {"message/eu/ltn16.qbf": {"absolute": 0, "size": len(native)}}
                )
            self.assertEqual(core.PRESERVED_NATIVE_FONT, bytes(native))
            self.assertFalse(core.HD_FONT_COVERAGE_ENABLED)
        finally:
            core.EXPECTED_CLEAN_ROMFS_SHA256 = old_digest
            core.PRESERVED_NATIVE_FONT = old_native
            core.HD_FONT_COVERAGE_ENABLED = old_enabled

    def test_reports_missing_font_pack_with_actionable_message(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        topscreen.mkdir(parents=True)
        o3tu = topscreen / "atlas_overrides.o3tu"
        o3tu.write_bytes(b"")
        with self.assertRaisesRegex(RuntimeError, "ativar fontes HD"):
            core.locate_hd_font_pack(o3tu)


if __name__ == "__main__":
    unittest.main()
