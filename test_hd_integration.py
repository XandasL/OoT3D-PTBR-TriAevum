import importlib.util
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib
from PIL import Image

spec = importlib.util.spec_from_file_location('hd', Path(__file__).parent / 'installer/hd_textures.py')
hd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hd)


def png():
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 8, 8, 8, 6, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress((b'\0' + b'\xff' * 32) * 8)) + chunk(b'IEND', b''))


def atlas_png(color=(0, 0, 255, 255), size=(1024, 512)):
    image = Image.new('RGBA', size, color)
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()


def hud_overlay_recipe():
    return {
        'atlas_texture': 'UI/tex1_512x256_1FAF9B5B2ADF6038_13_mip0.png',
        'native_texture': 'UI/tex1_512x256_BB00B25B152582B6_4_mip0.png',
        'face_glyphs': [
            {'name': 'X-to-Triangle', 'source': [158, 142, 16, 16], 'target': [207, 227, 16, 16]},
            {'name': 'Y-to-Square', 'source': [158, 158, 16, 16], 'target': [226, 227, 16, 16]},
            {'name': 'B-to-Circle', 'source': [158, 126, 16, 16], 'target': [363, 225, 16, 16]},
        ],
        'shoulder_glyphs': [
            {'name': 'ZR-to-R1', 'source': [440, 190, 17, 11], 'target': [47, 231, 16, 16], 'preserve_aspect': True},
            {'name': 'ZL-to-L1', 'source': [440, 201, 17, 11], 'target': [245, 227, 16, 16], 'preserve_aspect': True},
        ],
    }


def pause_edge_recipe(source_texture='UI/tex1_512x256_BB00B25B152582B6_4_mip0.png'):
    return {
        'resource': 'menu_item_parts00.ctxb',
        'target_texture': 'UI/menu_item.png',
        'source_texture': source_texture,
        'glyphs': [
            {'name': 'R1-top-edge', 'source': [440, 190, 17, 11], 'target': [233, 8, 16, 10], 'preserve_aspect': True},
            {'name': 'Triangle-edge', 'source': [158, 142, 16, 16], 'target': [238, 65, 12, 12]},
            {'name': 'Square-edge', 'source': [158, 158, 16, 16], 'target': [243, 118, 10, 12]},
            {'name': 'L1-bottom-edge', 'source': [440, 201, 17, 11], 'target': [233, 195, 16, 10], 'preserve_aspect': True},
        ],
    }



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
        self.hd_atlas_relative = 'data/mods/topscreen/fixture/ui_atlas_hd.png'
        self.hd_native_atlas_relative = 'UI/tex1_512x256_BB00B25B152582B6_4_mip0.png'
        self.hd_native_atlas = atlas_png((255, 0, 0, 255))
        self.hd_source_atlas = atlas_png((0, 0, 255, 255))
        self.write(self.root, self.hd_atlas_relative, self.hd_source_atlas)
        self.write(self.root, 'TriAevum.launch.json', hd.encoded_json({
            'format': 'oot3d_native_game_launch_profile_v1',
            'arguments': ['--config', '${profile_dir}/data/config/TriAevum.json',
                          '--save-data', '${profile_dir}/data/savedata',
                          '--topscreen-ui-atlas-hd', '${profile_dir}/' + self.hd_atlas_relative]}))
        self.write(self.root, 'data/savedata/save00.bin', b'untouched-save')
        self.write(self.root, 'romfs.bin', b'translated-romfs')
        self.write(self.root, 'traducao_ptbr_v4_instalada.json', hd.encoded_json({
            'format': 'oot3d_ptbr_full_translation_install_v4', 'original_romfs_sha256': 'clean-beta',
            'translation_files': 112, 'menu_eu_mirrors': 14, 'patch_operations': 126,
            'font_policy': 'preserve_native_hd_normalized_tildes',
            'romfs_path': str(self.root / 'romfs.bin'), 'installed_romfs_sha256': hd.digest(b'translated-romfs')}))
        self.write(self.pack, 'pack.json', hd.encoded_json({'options': {'use_new_hash': False, 'flip_png_files': True}}))
        self.write(self.pack, 'UI/original.png', png())
        self.write(self.pack, self.hd_native_atlas_relative, self.hd_native_atlas)
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
                      'pack_files': {
                          'UI/original.png': hd.digest(png()),
                          self.hd_native_atlas_relative: hd.digest(self.hd_native_atlas),
                      },
                      'aliases': [{'original': 'original.png', 'translated': 'ptbr.png', 'native_size': [2, 2]}],
                      'hud_atlas_overlay': hud_overlay_recipe()}
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

    def test_beta1c_runtime_paths_and_title_plugin_are_preserved(self):
        profile = hd.read_json(self.root / 'TriAevum.launch.json')
        profile['arguments'] = ['--config', '${runtime_dir}/data/config/TriAevum.json',
                                '--title-plugin', '${runtime_dir}/private-plugins/new-title.dll',
                                '--save-data', '${runtime_dir}/data/savedata',
                                '--topscreen-ui-atlas-hd', '${runtime_dir}/' + self.hd_atlas_relative]
        self.write(self.root, 'TriAevum.launch.json', hd.encoded_json(profile))
        self.install()
        actual = hd.read_json(self.root / hd.PROFILE)['arguments']
        self.assertEqual(actual[:2], ['--config', '${profile_dir}/' + hd.CONFIG])
        self.assertEqual(actual[2:6], profile['arguments'][2:6])
        self.assertEqual(actual[6:], ['--topscreen-ui-atlas-hd', '${profile_dir}/' + hd.HUD_ATLAS_PATH])

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

    def test_native_font_tilde_fallback_is_compatible_with_hd_textures(self):
        marker = hd.read_json(self.root / 'traducao_ptbr_v4_instalada.json')
        marker['font_policy'] = 'preserve_native_font_tilde_alias_patch'
        self.write(self.root, 'traducao_ptbr_v4_instalada.json', hd.encoded_json(marker))
        result = self.install(dry_run=True)
        self.assertEqual(result['aliases'], len(hd.recipe()['aliases']))
        self.assertFalse((self.root / hd.EXE).exists())
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

    def test_deploy_without_sources_installs_and_restores(self):
        deploy = hd.prepare_deploy_bundle(self.bundle, self.base / 'deploy', self.rules)
        self.assertFalse((deploy / 'source').exists())
        self.assertIn(hd.SOURCE_DOWNLOAD, (deploy / 'SOURCE_OFFER.md').read_text())
        with self.assertRaises(RuntimeError):hd.validate_bundle(deploy, self.rules)
        hd.install(self.root, self.pack, deploy)
        hd.restore(self.root)
        self.assert_originals()

    def test_deploy_source_reference_and_runtime_are_checked(self):
        deploy = hd.prepare_deploy_bundle(self.bundle, self.base / 'deploy', self.rules)
        manifest = hd.read_json(deploy / 'manifest.json')
        manifest['source_url'] = 'https://example.com/wrong.zip'
        self.write(deploy, 'manifest.json', hd.encoded_json(manifest))
        with self.assertRaises(RuntimeError):hd.validate_bundle(deploy, self.rules, require_sources=False)
        manifest['source_url'] = hd.SOURCE_DOWNLOAD
        self.write(deploy, 'manifest.json', hd.encoded_json(manifest))
        self.write(deploy, hd.EXE, b'corrupted')
        with self.assertRaises(RuntimeError):hd.validate_bundle(deploy, self.rules, require_sources=False)

    def test_missing_or_corrupt_sources_cannot_prepare_deploy(self):
        self.write(self.bundle, 'source/menus-HD.patch', b'corrupted source')
        with self.assertRaises(RuntimeError):hd.prepare_deploy_bundle(self.bundle, self.base / 'deploy', self.rules)
        self.assertFalse((self.base / 'deploy').exists())

    def test_dry_run_does_not_mutate(self):
        self.assertEqual(self.install(dry_run=True)['aliases'], 1)
        self.assertFalse((self.root / hd.RECEIPT).exists())
        self.assertFalse((self.root / hd.EXE).exists())
        self.assert_originals()

    def test_hud_atlas_composite_maps_all_face_and_shoulder_glyphs_and_restores(self):
        self.install()
        args = hd.read_json(self.root / hd.PROFILE)['arguments']
        index = args.index('--topscreen-ui-atlas-hd')
        self.assertEqual(args[index + 1], '${profile_dir}/' + hd.HUD_ATLAS_PATH)
        patched_path = self.root / hd.HUD_ATLAS_PATH
        self.assertTrue(patched_path.is_file())
        with Image.open(patched_path) as decoded:
            image = decoded.convert('RGBA')
            # The blue base survives outside glyph cells; red comes from source atlas.
            self.assertEqual(image.getpixel((10, 10)), (0, 0, 255, 255))
            # Only the verified gameplay HUD cells belong in custom_ui01.
            for x, y in ((214, 234), (233, 234), (370, 233), (55, 239), (253, 235)):
                self.assertEqual(image.getpixel((x * 2, y * 2)), (255, 0, 0, 255))
        hd.restore(self.root)
        self.assertFalse(patched_path.exists())
        self.assertEqual((self.root / self.hd_atlas_relative).read_bytes(), self.hd_source_atlas)

    def test_pack_custom_ui_atlas_composite_is_restored_without_touching_original_atlas(self):
        overlay = self.rules['hud_atlas_overlay']
        atlas_path = self.pack / overlay['atlas_texture']
        self.write(self.pack, overlay['atlas_texture'], atlas_png((0, 0, 255, 255)))
        before = atlas_path.read_bytes()
        self.install()
        with Image.open(atlas_path) as decoded:
            self.assertEqual(decoded.convert('RGBA').getpixel((214 * 2, 234 * 2)), (255, 0, 0, 255))
        self.assertEqual((self.root / self.hd_atlas_relative).read_bytes(), self.hd_source_atlas)
        hd.restore(self.root)
        self.assertEqual(atlas_path.read_bytes(), before)

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
        self.assertFalse((self.root / hd.HUD_ATLAS_PATH).exists())

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


    def test_native_beta11_launcher_copies_exact_runtime_and_restores(self):
        import shutil

        self.rules['runtime_mode'] = hd.NATIVE_RUNTIME_MODE
        self.rules['runtime_files'] = {}
        self.rules['source_files'] = {}
        shutil.rmtree(self.bundle / 'source')
        (self.bundle / hd.EXE).unlink()
        self.write(self.bundle, 'LICENSE_SCOPE.md', b'native runtime only')
        self.write(self.bundle, 'manifest.json', hd.encoded_json({
            'format': 'oot3d_ptbr_hd_runtime_v1',
            'runtime_mode': hd.NATIVE_RUNTIME_MODE,
            'files': {},
            'source_files': {},
            'source_url': hd.SOURCE_DOWNLOAD,
        }))
        original_exe = (self.root / 'TriAevum.exe').read_bytes()

        self.install()

        launcher = self.root / hd.EXE
        self.assertEqual(launcher.read_bytes(), original_exe)
        self.assertEqual((self.root / 'TriAevum.exe').read_bytes(), original_exe)
        self.assert_originals()

        self.assertTrue(hd.restore(self.root))
        self.assertFalse(launcher.exists())
        self.assertEqual((self.root / 'TriAevum.exe').read_bytes(), original_exe)
        self.assert_originals()


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
        overlay = rules['hud_atlas_overlay']
        self.assertIn(overlay['native_texture'], rules['pack_files'])
        self.assertEqual(
            [item['name'] for item in overlay['face_glyphs']],
            ['X-to-Triangle', 'Y-to-Square', 'B-to-Circle'],
        )
        self.assertEqual(
            [item['name'] for item in overlay['shoulder_glyphs']],
            ['ZR-to-R1', 'ZL-to-L1'],
        )
        self.assertNotIn('pause_menu_glyphs', overlay)
        self.assertEqual(overlay['atlas_texture'], 'UI/tex1_512x256_1FAF9B5B2ADF6038_13_mip0.png')
        pause_edge = rules['pause_edge_overlay']
        self.assertEqual(pause_edge['resource'], 'menu_item_parts00.ctxb')
        self.assertEqual(pause_edge['target_texture'], 'UI/tex1_256x256_18DDBB03B81C1D60_13_mip0.png')
        self.assertEqual(
            [item['name'] for item in pause_edge['glyphs']],
            ['R1-top-edge', 'Triangle-edge', 'Square-edge', 'L1-bottom-edge'],
        )
        self.assertIn(pause_edge['target_texture'], rules['pack_files'])
        self.assertIn(pause_edge['source_texture'], rules['pack_files'])

    def test_beta11_native_runtime_is_pinned(self):
        rules = hd.recipe()
        self.assertEqual(rules['target'], 'TriAevum v0.8.0-beta.1.1 Windows x64')
        self.assertEqual(rules['runtime_mode'], hd.NATIVE_RUNTIME_MODE)
        self.assertEqual(
            rules['original_runtime_sha256'],
            '13f934c68d536b09dc580fa28ba54e3967fe6b2058cfe6e918828917455a1357',
        )
        self.assertEqual(rules['runtime_files'], {})
        self.assertEqual(rules['source_files'], {})
