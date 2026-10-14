import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

spec = importlib.util.spec_from_file_location('hd', Path(__file__).parent / 'installer/hd_textures.py')
hd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hd)


def png():
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 8, 8, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress((b'\0' + b'\xff' * 32) * 8)) + chunk(b'IEND', b''))


class HDIntegration(unittest.TestCase):
    def setUp(self):
        test_root = Path(__file__).resolve().parent / 'build/hd-tests'
        test_root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=test_root)
        if not Path(self.temp.name).resolve().is_relative_to(test_root.resolve()):
            raise RuntimeError('Pasta temporária dos testes fora do workspace.')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'game'
        self.pack = self.base / 'pack'
        self.bundle = self.base / 'bundle'
        self.root.mkdir(); self.pack.mkdir(); self.bundle.mkdir()
        self.write(self.root, 'TriAevum.exe', b'original-runtime')
        self.write(self.root, 'shaderc_shared.dll', b'original-dll')
        self.write(self.root, 'data/config/TriAevum.json', hd.encoded_json({
            'CVars': {'': {'Example': 3}}, 'Graphics': {'Custom': 42}}))
        self.write(self.root, 'TriAevum.launch.json', hd.encoded_json({
            'format': 'oot3d_native_game_launch_profile_v1',
            'arguments': ['--config', '${profile_dir}/data/config/TriAevum.json', '--save-data', '${profile_dir}/data/savedata']}))
        self.write(self.root, 'data/savedata/save00.bin', b'untouched-save')
        self.write(self.root, 'romfs.bin', b'translated-romfs')
        self.write(self.root, 'traducao_ptbr_v4_instalada.json', hd.encoded_json({
            'format': 'oot3d_ptbr_full_translation_install_v4', 'original_romfs_sha256': 'clean-beta',
            'translation_files': 112, 'menu_eu_mirrors': 14, 'patch_operations': 126,
            'font_policy': 'preserve_native_hd_normalized_tildes',
            'romfs_path': str(self.root / 'romfs.bin'), 'installed_romfs_sha256': hd.digest(b'translated-romfs')}))
        self.write(self.pack, 'pack.json', hd.encoded_json({'options': {'use_new_hash': False, 'flip_png_files': True}}))
        self.write(self.pack, 'UI/original.png', png())
        self.write(self.bundle, hd.EXE, b'patched-runtime')
        self.write(self.bundle, 'source/TriAevum-source.zip', b'upstream-source')
        self.write(self.bundle, 'source/menus-HD.patch', b'local-patch')
        for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'SOURCE_OFFER.md'):
            self.write(self.bundle, name, b'notices')
        self.rules = {'original_runtime_sha256': hd.digest(b'original-runtime'), 'clean_romfs_sha256': 'clean-beta',
                      'original_dependencies': {'shaderc_shared.dll': hd.digest(b'original-dll')},
                      'runtime_files': {hd.EXE: hd.digest(b'patched-runtime')},
                      'source_files': {'source/TriAevum-source.zip': hd.digest(b'upstream-source'),
                                       'source/menus-HD.patch': hd.digest(b'local-patch')},
                      'pack_files': {'UI/original.png': hd.digest(png())},
                      'aliases': [{'original': 'original.png', 'translated': 'ptbr.png', 'native_size': [2, 2]}]}
        self.write(self.bundle, 'manifest.json', hd.encoded_json({'format': 'oot3d_ptbr_hd_runtime_v1', 'files': self.rules['runtime_files']}))
        self.recipe_patch = patch.object(hd, 'recipe', return_value=self.rules)
        self.recipe_patch.start(); self.addCleanup(self.recipe_patch.stop)
        self.closed_patch = patch.object(hd, 'assert_closed')
        self.closed_patch.start(); self.addCleanup(self.closed_patch.stop)
        self.originals = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    @staticmethod
    def write(root, name, data):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def install(self, **kwargs):
        return hd.install(self.root, self.pack, self.bundle, **kwargs)

    def assert_originals(self):
        for name, data in self.originals.items():
            self.assertEqual((self.root / name).read_bytes(), data, name)

    def test_install_restore_keeps_originals_and_preferences(self):
        self.install()
        self.assert_originals()
        config = hd.read_json(self.root / hd.CONFIG)
        self.assertEqual(config['Graphics']['Custom'], 42)
        self.assertEqual(config['CVars']['']['Example'], 3)
        config['Graphics']['Custom'] = 99
        self.write(self.root, hd.CONFIG, hd.encoded_json(config))
        self.assertTrue(hd.restore(self.root))
        self.assert_originals()
        self.assertFalse((self.root / hd.EXE).exists())
        self.assertFalse((self.pack / 'UI/PTBR_HASHES/ptbr.png').exists())
        self.assertEqual(hd.read_json(self.root / hd.CONFIG)['Graphics']['Custom'], 99)
        self.install()
        self.assertEqual(hd.read_json(self.root / hd.CONFIG)['Graphics']['Custom'], 99)

    def test_existing_alias_is_not_owned(self):
        self.write(self.pack, 'UI/PTBR_HASHES/ptbr.png', png())
        self.install(); hd.restore(self.root)
        self.assertEqual((self.pack / 'UI/PTBR_HASHES/ptbr.png').read_bytes(), png())

    def test_conflict_rejected_before_writing(self):
        self.write(self.pack, 'UI/PTBR_HASHES/ptbr.png', b'another-mod')
        with self.assertRaises(RuntimeError): self.install()
        self.assert_originals()
        self.assertFalse((self.root / hd.EXE).exists())

    def test_untranslated_or_changed_pack_rejected(self):
        self.write(self.pack, 'UI/original.png', b'changed-image')
        with self.assertRaises(RuntimeError): self.install()
        self.assertFalse((self.root / hd.RECEIPT).exists())
        self.assert_originals()

    def test_wrong_runtime_or_romfs_rejected(self):
        self.write(self.root, 'TriAevum.exe', b'new-version')
        with self.assertRaises(RuntimeError): self.install()
        self.write(self.root, 'TriAevum.exe', b'original-runtime')
        self.write(self.root, 'romfs.bin', b'changed-romfs')
        with self.assertRaises(RuntimeError): self.install()
        self.assertFalse((self.root / hd.RECEIPT).exists())

    def test_legacy_font_policy_rejected(self):
        marker = hd.read_json(self.root / 'traducao_ptbr_v4_instalada.json')
        marker['font_policy'] = 'replace_original_font'
        self.write(self.root, 'traducao_ptbr_v4_instalada.json', hd.encoded_json(marker))
        with self.assertRaises(RuntimeError): self.install()
        self.assertFalse((self.root / hd.EXE).exists())

    def test_corrupted_bundle_rejected(self):
        self.write(self.bundle, hd.EXE, b'corrupt-exe')
        with self.assertRaises(RuntimeError): self.install()
        self.assert_originals()

    def test_dry_run_does_not_mutate(self):
        self.assertEqual(self.install(dry_run=True)['aliases'], 1)
        self.assertFalse((self.root / hd.RECEIPT).exists())
        self.assertFalse((self.root / hd.EXE).exists())
        self.assert_originals()

    def test_duplicate_config_flag_rejected(self):
        profile = hd.read_json(self.root / 'TriAevum.launch.json')
        profile['arguments'] += ['--config', 'other.json']
        self.write(self.root, 'TriAevum.launch.json', hd.encoded_json(profile))
        with self.assertRaises(RuntimeError): self.install()
        self.assertFalse((self.root / hd.EXE).exists())

    def test_write_failure_rolls_back(self):
        atomic = hd.atomic_write
        def failing(path, data):
            if path.name == hd.PROFILE: raise OSError('simulated disk failure')
            atomic(path, data)
        with patch.object(hd, 'atomic_write', side_effect=failing):
            with self.assertRaises(OSError): self.install()
        self.assert_originals()
        self.assertFalse((self.root / hd.EXE).exists())
        self.assertFalse((self.pack / 'UI/PTBR_HASHES/ptbr.png').exists())
        self.assertFalse((self.root / hd.RECEIPT).exists())

    def test_existing_config_is_recovered_after_final_write_failure(self):
        before = hd.encoded_json({'Graphics': {'Favorite': 123}})
        self.write(self.root, hd.CONFIG, before)
        atomic = hd.atomic_write
        def failing(path, data):
            if path.name == 'installation.json' and b'"state": "installed"' in data:
                raise OSError('simulated final commit failure')
            atomic(path, data)
        with patch.object(hd, 'atomic_write', side_effect=failing):
            with self.assertRaises(OSError): self.install()
        self.assertEqual((self.root / hd.CONFIG).read_bytes(), before)
        self.assertFalse((self.root / hd.EXE).exists())

    def test_changed_owned_file_blocks_restore_before_removing_anything(self):
        self.install()
        self.write(self.root, hd.EXE, b'user-update')
        with self.assertRaises(RuntimeError): hd.restore(self.root)
        self.assertTrue((self.root / hd.PROFILE).exists())
        self.assertTrue((self.pack / 'UI/PTBR_HASHES/ptbr.png').exists())
        self.assert_originals()

    def test_receipt_path_escape_is_rejected(self):
        self.install()
        state = hd.read_json(self.root / hd.RECEIPT)
        state['files'][0]['path'] = '../../outside.exe'
        self.write(self.root, hd.RECEIPT, hd.encoded_json(state))
        with self.assertRaises(RuntimeError): hd.restore(self.root)
        self.assertTrue((self.root / hd.EXE).exists())

    def test_lexical_parent_escape_is_rejected(self):
        with self.assertRaises(RuntimeError): hd.bounded(self.root, '../outside.bin')


    def enable_navi_fixture(self):
        actual = hd.read_json(hd.HERE / 'hd-recipe.json')['navi_repair']
        self.rules['navi_repair'] = dict(actual, source='original.png', translated='ptbr.png',
                                        image_size=[8, 8], box=[2, 2, 4, 4])

    def test_navi_upgrade_restores_preexisting_alias(self):
        self.enable_navi_fixture()
        target = self.pack / 'UI/PTBR_HASHES/ptbr.png'
        self.write(self.pack, 'UI/PTBR_HASHES/ptbr.png', png())
        self.install()
        self.assertNotEqual(target.read_bytes(), png())
        hd.restore(self.root)
        self.assertEqual(target.read_bytes(), png())

    def test_navi_upgrade_rolls_back_after_later_failure(self):
        self.enable_navi_fixture()
        target = self.pack / 'UI/PTBR_HASHES/ptbr.png'
        self.write(self.pack, 'UI/PTBR_HASHES/ptbr.png', png())
        original_write = hd.atomic_write
        def fail_profile(path, data):
            if path.name == hd.PROFILE:
                raise OSError('simulated profile write failure')
            return original_write(path, data)
        with patch.object(hd, 'atomic_write', side_effect=fail_profile):
            with self.assertRaises(OSError): self.install()
        self.assertEqual(target.read_bytes(), png())
        self.assertFalse((self.root / hd.EXE).exists())

    def test_navi_changes_only_its_slot(self):
        self.enable_navi_fixture()
        from PIL import Image, ImageChops
        import io
        before = Image.open(io.BytesIO(png())).convert('RGBA')
        after = Image.open(io.BytesIO(hd.repair_navi_hud(png(), self.rules))).convert('RGBA')
        changed = ImageChops.difference(before, after).getbbox()
        self.assertIsNotNone(changed)
        self.assertTrue(2 <= changed[0] < changed[2] <= 4 and 2 <= changed[1] < changed[3] <= 4)

    def test_navi_does_not_overwrite_unknown_alias(self):
        self.enable_navi_fixture()
        self.write(self.pack, 'UI/PTBR_HASHES/ptbr.png', png() + b'unknown edit')
        with self.assertRaises(RuntimeError): self.install()
        self.assertFalse((self.root / hd.EXE).exists())


if __name__ == '__main__':
    unittest.main()

class HDRecipeV12(unittest.TestCase):
    def test_recipe_has_71_unique_validated_aliases(self):
        rules = hd.recipe()
        self.assertEqual(len(rules['aliases']), 71)
        self.assertEqual(len({a['translated'] for a in rules['aliases']}), 71)
        self.assertEqual(len(rules['pack_files']), 75)
        for alias in rules['aliases']:
            self.assertIn('UI/' + alias['original'], rules['pack_files'])
            self.assertEqual(len(rules['pack_files']['UI/' + alias['original']]), 64)

    def test_corresponding_runtime_patch_is_pinned(self):
        rules = hd.recipe()
        patch_path = Path(__file__).parent / 'installer/runtime-HD.patch'
        self.assertEqual(hd.digest(patch_path.read_bytes()), rules['source_files']['source/menus-HD.patch'])
