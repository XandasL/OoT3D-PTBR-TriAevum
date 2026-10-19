import importlib.util,unittest,struct,tempfile,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('compat',Path(__file__).parent/'installer/Instalador_Traducao_PTBR_OoT3D_V4_compat_test.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
class Safety(unittest.TestCase):
 def test_runtime_and_profile_paths_stay_inside_installation(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as folder, patch.object(c,'BASE',Path(folder)):
   for variable in ('${profile_dir}', '${runtime_dir}'):
    for separator in ('/', '\\'):
     self.assertEqual(c.resolve_profile_path(variable+separator+'data/title.json'),(Path(folder)/'data/title.json').resolve())
    with self.assertRaises(RuntimeError):c.resolve_profile_path(variable+'/../escape')
   with self.assertRaises(RuntimeError):c.resolve_profile_path('${unknown}/data')
 def test_o3tu_replacement_corruption(self):
  raw=b'O3TU'+struct.pack('<IIIQQI',2,1,0,1,2,1)+b'x'
  _,_,n,e=c.parse_o3tu_entries(raw)
  with self.assertRaises(RuntimeError):c.validate_o3tu_complete(raw,e,n)
 def test_o3tu_truncated_profile(self):
  raw=b'O3TU'+struct.pack('<III',2,0,1)
  with self.assertRaises(RuntimeError):c.validate_o3tu_complete(raw,[],1)
 def test_o3tu_extra_bytes(self):
  raw=b'O3TU'+struct.pack('<III',2,0,0)+b'x'
  with self.assertRaises(RuntimeError):c.validate_o3tu_complete(raw,[],0)
 def test_path_escape(self):
  c.BASE=Path(__file__).parent
  with self.assertRaises(RuntimeError):c.contained(c.BASE.parent/'escape')
 def test_romfs_metadata_bounds(self):
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'bad.bin';p.write_bytes(struct.pack('<10I',40,40,4,44,24,68,4,72,32,80))
   with self.assertRaises(RuntimeError):c.index_romfs(p)
 def test_alpha_allowlist_retained(self):
  self.assertIn('011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99',c.KNOWN_BASES)
 def test_qm_truncated(self):
  with self.assertRaises(RuntimeError):c.convert_qm_us_to_eu(b'QM\0\0'+struct.pack('<III',4,2510,0))
 @unittest.skipUnless((Path(__file__).parent.parent/"TriAevum-v0.8.0-beta.1-Windows-x64-extract").is_dir(), "Requer instalação local para comparar fonte nativa real")
 def test_beta_preserves_native_font(self):
  import zipfile
  root=Path(__file__).parent.parent/'TriAevum-v0.8.0-beta.1-Windows-x64-extract'
  with zipfile.ZipFile(next(root.rglob('font_coverage.zip'))) as z:
   manifest=json.loads(z.read('manifest.json'));native=z.read(manifest['fonts'][0]['native_file'])
  item={'source':Path(__file__).parent/'test-input/TraducaoCompleta/citra/romfs/message/us/ltn16.qbf','kind':'raw','target':'message/eu/ltn16.qbf'}
  c.PRESERVED_NATIVE_FONT=native;c.EXPECTED_CLEAN_ROMFS_SHA256=c.BETA_ROMFS_SHA256
  self.assertEqual(c.prepare_payload(item),native)
  c.EXPECTED_CLEAN_ROMFS_SHA256='011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99'
  self.assertEqual(c.prepare_payload(item),item['source'].read_bytes())
 def test_missing_hd_font_reports_expected_path(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   romfs=root/'romfs.bin'
   native=bytearray(28232)
   native[:4]=b'QBF1'
   struct.pack_into('<H',native,4,199)
   romfs.write_bytes(native)
   with patch.object(c,'EXPECTED_CLEAN_ROMFS_SHA256',c.BETA_ROMFS_SHA256), patch.object(c,'locate_o3tu',return_value=root/'pack.o3tu'), patch.object(c,'contained',side_effect=lambda path:path):
    with self.assertRaisesRegex(RuntimeError,'não encontrado') as caught:
     c.validate_hd_font(romfs,{'message/eu/ltn16.qbf':{'absolute':0,'size':28232}})
    self.assertIn('font_coverage.zip',str(caught.exception))
    self.assertIsNone(c.PRESERVED_NATIVE_FONT)
 def test_mismatched_hd_font_reports_incompatible_hash(self):
  from unittest.mock import patch
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder)
   romfs=root/'romfs.bin'
   native=bytearray(28232)
   native[:4]=b'QBF1'
   struct.pack_into('<H',native,4,199)
   romfs.write_bytes(native)
   (root/'font_coverage.zip').write_bytes(b'wrong hash')
   with patch.object(c,'EXPECTED_CLEAN_ROMFS_SHA256',c.BETA_ROMFS_SHA256), patch.object(c,'locate_o3tu',return_value=root/'pack.o3tu'), patch.object(c,'contained',side_effect=lambda path:path):
    with self.assertRaisesRegex(RuntimeError,'incompatível') as caught:
     c.validate_hd_font(romfs,{'message/eu/ltn16.qbf':{'absolute':0,'size':28232}})
    self.assertIn('SHA-256',str(caught.exception))
    self.assertIsNone(c.PRESERVED_NATIVE_FONT)
 def test_beta_font_mapping_change_rejected(self):
  c.EXPECTED_CLEAN_ROMFS_SHA256=c.BETA_ROMFS_SHA256;c.PRESERVED_NATIVE_FONT=b'x'*28232
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'font.qbf';p.write_bytes(b'y'*28232)
   with self.assertRaises(RuntimeError):c.prepare_payload({'source':p,'kind':'raw','target':'message/eu/ltn16.qbf'})
  c.EXPECTED_CLEAN_ROMFS_SHA256='011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99'
 def test_beta_qm_tildes_and_other_languages(self):
  original=(Path(__file__).parent/'test-input/TraducaoCompleta/citra/romfs/message/us/us.qm').read_bytes()
  c.EXPECTED_CLEAN_ROMFS_SHA256='011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99'
  legacy=c.convert_qm_us_to_eu(original)
  c.EXPECTED_CLEAN_ROMFS_SHA256=c.BETA_ROMFS_SHA256
  normalized=c.convert_qm_us_to_eu(original)
  table_end=16+c.EXPECTED_QM_RECORDS*96
  self.assertEqual(normalized[:table_end],legacy[:table_end])
  self.assertEqual(len(normalized),len(legacy))
  changes=0
  for i in range(c.EXPECTED_QM_RECORDS):
   entry=16+i*96+16
   off,size=struct.unpack_from('<II',original,entry+8)
   text=original[off:off+size]
   expected=text
   for before,after in (('ä','ã'),('ö','õ'),('Ä','Ã'),('Ö','Õ')):
    changes+=text.count(before.encode());expected=expected.replace(before.encode(),after.encode())
   self.assertEqual(normalized[off:off+size],expected)
   for slot in (5,7):
    other,n=struct.unpack_from('<II',original,entry+slot*8)
    self.assertEqual(normalized[other:other+n],original[other:other+n])
  self.assertGreater(changes,1000)
  c.EXPECTED_CLEAN_ROMFS_SHA256='011c0b6933f3932c704ff1c6ab562023f407c2929661a6d54ecea1ca81072f99'
 def test_tilde_normalization_rejects_unknown_qm(self):
  with self.assertRaises(RuntimeError):c.normalize_ptbr_tildes(b'unknown',b'unknown')
if __name__=='__main__':unittest.main()
