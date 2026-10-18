import importlib.util
import tempfile
import unittest
from pathlib import Path

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

    def test_reports_missing_font_pack_with_actionable_message(self):
        topscreen = self.root / "data" / "mods" / "topscreen"
        topscreen.mkdir(parents=True)
        o3tu = topscreen / "atlas_overrides.o3tu"
        o3tu.write_bytes(b"")
        with self.assertRaisesRegex(RuntimeError, "Importe novamente o SingleScreen"):
            core.locate_hd_font_pack(o3tu)


if __name__ == "__main__":
    unittest.main()
