"""Crash/recovery on synthetic RomFS; no game, textures or original QBF needed."""
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
INVALID=0xffffffff

def load():
    spec=importlib.util.spec_from_file_location('recovery_core',ROOT/'installer/text_translation.py')
    core=importlib.util.module_from_spec(spec);spec.loader.exec_module(core)
    return core

def romfs(path, resources):
    directories = ['']
    for name in resources:
        parent = Path(name).parent
        for ancestor in reversed([parent, *parent.parents]):
            text = ancestor.as_posix()
            if text != '.' and text not in directories:
                directories.append(text)
    offsets = {}; directory_size = 0
    for name in directories:
        offsets[name] = directory_size
        directory_size += (24+len(Path(name).name.encode('utf-16-le'))+3)&~3 if name else 24
    file_offsets = {}; file_size = 0
    for name in resources:
        file_offsets[name] = file_size
        file_size += (32+len(Path(name).name.encode('utf-16-le'))+3)&~3
    dirs = bytearray(directory_size); files = bytearray(file_size); payload = bytearray()
    children = lambda parent: [x for x in directories if x and (str(Path(x).parent).replace('\\','/') if str(Path(x).parent)!='.' else '') == parent]
    for name in directories:
        parent = str(Path(name).parent).replace('\\','/') if name else ''
        if parent == '.': parent = ''
        siblings = children(parent); sibling = INVALID
        if name and siblings.index(name)+1 < len(siblings): sibling = offsets[siblings[siblings.index(name)+1]]
        subs = children(name)
        entries = [x for x in resources if (Path(x).parent.as_posix() if Path(x).parent.as_posix()!='.' else '') == name]
        label = Path(name).name.encode('utf-16-le') if name else b''
        struct.pack_into('<6I', dirs, offsets[name], offsets.get(parent,0), sibling,
                         offsets[subs[0]] if subs else INVALID,
                         file_offsets[entries[0]] if entries else INVALID, INVALID, len(label))
        dirs[offsets[name]+24:offsets[name]+24+len(label)] = label
        for i, full in enumerate(entries):
            data = resources[full]; label = Path(full).name.encode('utf-16-le'); pos = file_offsets[full]
            struct.pack_into('<IIQQII',files,pos,offsets[name],file_offsets[entries[i+1]] if i+1<len(entries) else INVALID,len(payload),len(data),INVALID,len(label))
            files[pos+32:pos+32+len(label)] = label; payload.extend(data)
    directory_start = 44; file_hash_start = directory_start+len(dirs); file_start = file_hash_start+4
    data_start = file_start+len(files)
    path.write_bytes(struct.pack('<10I',40,40,4,directory_start,len(dirs),file_hash_start,4,file_start,len(files),data_start)+bytes(4)+dirs+bytes(4)+files+payload)


class Crash(BaseException):pass

class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.c=load();c=self.c
        (self.root/'data/source').mkdir(parents=True);(self.root/'data/mods/native').mkdir(parents=True)
        self.clean=self.root/'data/source/romfs.bin'
        romfs(self.clean,{'message/eu/eu.qm':b'English','message/eu/ltn16.qbf':b'font',
                         'menu/02_eu_english/items.ctxb':b'English texture','scene/test':b'unchanged'})
        self.clean_hash=c.sha256_file(self.clean)
        source={'romfs_image_path':'romfs.bin','romfs_image_file_size':self.clean.stat().st_size,
                'romfs_service_size':self.clean.stat().st_size,'romfs_service_offset':0,
                'code_bin_path':'code.bin','exheader_path':'exheader.bin'}
        (self.clean.parent/'process-manifest.json').write_text(json.dumps({'format':'oot3d_native_process_manifest_v1','source':source}))
        self.launch=self.root/'TriAevum.launch.json'
        self.launch.write_text(json.dumps({'format':'oot3d_native_game_launch_profile_v1','arguments':[
            '--a32-process-manifest','${runtime_dir}/data/source/process-manifest.json',
            '--topscreen-texture-overrides','${runtime_dir}/data/mods/native/atlas.o3tu']}))
        self.original=self.launch.read_bytes();self.pack=self.root/'data/mods/native/font_coverage.zip'
        self.pack.write_bytes(b'user original font')
        patches=[patch.object(c,'BASE',self.root),patch.object(c,'LAUNCH',self.launch),
                 patch.object(c,'MARKER',self.root/'traducao_ptbr_textos.json'),
                 patch.object(c,'CLEAN_SHA256',self.clean_hash),patch.object(c,'assert_closed'),
                 patch.object(c,'FONT_MODE_OPTION','hd'),
                 patch.object(c,'prepared_resources',return_value={'message/eu/eu.qm':b'Portugues',
                    'menu/02_eu_english/items.ctxb':b'Textura PTBR'}),
                 patch.object(c,'make_font',return_value=b'approved HD 128')]
        for p in patches:p.start();self.addCleanup(p.stop)

    def restart(self):
        old=self.c;self.c=load()
        for name in ('BASE','LAUNCH','MARKER','CLEAN_SHA256','FONT_MODE_OPTION',
                     'assert_closed','prepared_resources','make_font'):
            setattr(self.c,name,getattr(old,name))

    def check_original(self):
        self.assertEqual(self.launch.read_bytes(),self.original)
        self.assertEqual(self.pack.read_bytes(),b'user original font')
        self.assertEqual(self.c.sha256_file(self.clean),self.clean_hash)

    def test_install_crashes_resume_or_preserve_original(self):
        # Each phase uses its own fresh install state and a freshly imported core.
        checkpoints=['install_backup','install_copy_start','install_copy_end','install_manifest',
                     'install_prepared','install_font','install_before_launch','install_after_launch',
                     'install_receipt','install_committed']
        for point in checkpoints:
            with self.subTest(point=point):
                with patch.object(self.c,'_checkpoint',side_effect=lambda name: (_ for _ in ()).throw(Crash()) if name==point else None):
                    with self.assertRaises(Crash):self.c.install()
                self.restart();self.c.recover()
                self.assertIsNone(self.c.transactions.pending(self.root))
                if self.c.is_installed():
                    self.c.validate_installed();self.c.restore()
                self.check_original()
                # Recovery is repeatable and a fresh installation is still possible.
                self.restart();self.c.recover()

    def test_restore_crashes_repeat_safely(self):
        for point in ['restore_intent','restore_profile','restore_font','restore_remove_romfs.bin',
                      'restore_remove_process-manifest.json','restore_remove_traducao_ptbr_textos.json',
                      'restore_remove_TriAevum.launch.json.antes_ptbr_textos']:
            with self.subTest(point=point):
                self.c.install()
                with patch.object(self.c,'_checkpoint',side_effect=lambda name: (_ for _ in ()).throw(Crash()) if name==point else None):
                    with self.assertRaises(Crash):self.c.restore()
                self.restart();self.c.recover();self.check_original();self.c.recover()

    def test_font_crashes_resume_and_preserve_user_pack(self):
        self.c.install()
        for point in ['font_intent','font_payload_font_coverage.ptbr-noto.disabled.zip','font_prepared',
                      'font_apply_font_coverage.zip','font_apply_font_coverage.ptbr-noto.json','font_committed']:
            with self.subTest(point=point):
                with patch.object(self.c.fonts,'_checkpoint',side_effect=lambda name: (_ for _ in ()).throw(Crash()) if name==point else None):
                    with self.assertRaises(Crash):self.c.set_font_mode('original')
                self.restart();self.c.recover()
                self.assertEqual(self.pack.read_bytes(),b'user original font')
                self.c.set_font_mode('hd')
        self.c.restore();self.check_original()

    def test_external_profile_edit_refused(self):
        with patch.object(self.c,'_checkpoint',side_effect=lambda n: (_ for _ in ()).throw(Crash()) if n=='install_after_launch' else None):
            with self.assertRaises(Crash):self.c.install()
        self.launch.write_bytes(b'third party profile')
        with self.assertRaises(self.c.transactions.PendingTransaction):self.c.recover()
        self.assertEqual(self.launch.read_bytes(),b'third party profile')

    def test_external_font_edit_refused_before_recovery_writes(self):
        self.c.install()
        with patch.object(self.c.fonts,'_checkpoint',side_effect=lambda n: (_ for _ in ()).throw(Crash()) if n=='font_prepared' else None):
            with self.assertRaises(Crash):self.c.set_font_mode('original')
        self.pack.write_bytes(b'third party font')
        with self.assertRaises(RuntimeError):self.c.recover()
        self.assertEqual(self.pack.read_bytes(),b'third party font')

    def test_process_termination_during_font_commit(self):
        for point in ('font_prepared','font_apply_font_coverage.zip','font_committed'):
            with self.subTest(point=point):
                script = ("import importlib.util,os; from pathlib import Path; "
                          + "s=importlib.util.spec_from_file_location('font',"+repr(str(ROOT/'installer/font_mode.py'))+"); "
                          + "m=importlib.util.module_from_spec(s);s.loader.exec_module(m); "
                          + "m._checkpoint=lambda n: os._exit(91) if n=="+repr(point)+" else None; "
                          + "m.choose(Path("+repr(str(self.pack))+"),'hd',lambda:b'process HD')")
                result=subprocess.run([sys.executable,'-c',script],capture_output=True)
                self.assertEqual(result.returncode,91,result.stderr)
                self.restart();self.c.fonts.recover(self.pack)
                self.assertEqual(self.pack.read_bytes(),b'process HD')
                self.c.fonts.restore_previous(self.pack);self.check_original()

if __name__=='__main__':unittest.main()
