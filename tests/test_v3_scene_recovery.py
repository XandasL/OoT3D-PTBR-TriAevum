"""Synthetic tests for v3.0.1 ZAR reconstruction; no original ROM data."""
import hashlib
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
import rebuild_v301_scenes as scenes

def make_ctxb(length=16456,seed=b"A"):
    output=bytearray(seed*length)
    output[:4]=b"ctxb"
    struct.pack_into("<I",output,4,length)
    struct.pack_into("<I",output,8,1)
    output[24:28]=b"tex "
    struct.pack_into("<I",output,32,1)
    struct.pack_into("<I",output,36,length-72)
    output[40:56]=bytes(range(16))
    return bytes(output)

def make_zar():
    names=["f_usen.ctxb","f_euen.ctxb","model.bin"]
    payloads=[make_ctxb(seed=b"A"),make_ctxb(seed=b"B"),b"model coordinates"]
    header=bytearray(140)
    header[:4]=b"ZAR\1"
    struct.pack_into("<IHHIII",header,4,0,4,3,0x20,0x20,0x80)
    cursor=0x38
    for i,name in enumerate(names):
        data=name.encode("ascii")+b"\0"
        header[cursor:cursor+len(data)]=data
        struct.pack_into("<II",header,0x20+8*i,len(payloads[i]),cursor)
        cursor+=len(data)
    output=header
    for i,data in enumerate(payloads):
        output.extend(b"\0"*(-len(output)%4))
        struct.pack_into("<I",output,0x80+4*i,len(output))
        output.extend(data)
    struct.pack_into("<I",output,4,len(output))
    return bytes(output)

class SceneTests(unittest.TestCase):
    def test_only_two_english_textures_change(self):
        original=make_zar()
        textures={"f_usen.ctxb":make_ctxb(seed=b"P"),
                  "f_euen.ctxb":make_ctxb(49224,seed=b"Q")}
        result=scenes.rebuild_zar(original,textures)
        before=scenes.parse_zar(original)[2]
        after=scenes.parse_zar(result)[2]
        self.assertEqual([x[0] for x in before],[x[0] for x in after])
        self.assertEqual(before[2][3],after[2][3])
        self.assertEqual(after[0][3],textures["f_usen.ctxb"])
        self.assertEqual(after[1][3],textures["f_euen.ctxb"])
        self.assertEqual(len(result),len(original)+32768)
        self.assertEqual(after[1][1]%4,0)

    def test_reject_wrong_texture_metadata(self):
        corrupted=bytearray(make_ctxb(seed=b"P"))
        corrupted[40]^=1
        with self.assertRaisesRegex(ValueError,"metadata"):
            scenes.rebuild_zar(make_zar(),{
                "f_usen.ctxb":bytes(corrupted),
                "f_euen.ctxb":make_ctxb(seed=b"Q")})

    def test_reject_truncated_or_invalid_zar(self):
        original=make_zar()
        with self.assertRaisesRegex(ValueError,"size mismatch"):
            scenes.parse_zar(original[:-1])
        with self.assertRaisesRegex(ValueError,"header"):
            scenes.parse_zar(b"BAD!"+original[4:])

    def test_original_input_unchanged(self):
        original=make_zar()
        expected=hashlib.sha256(original).digest()
        scenes.rebuild_zar(original,{
            "f_usen.ctxb":make_ctxb(seed=b"P"),
            "f_euen.ctxb":make_ctxb(seed=b"Q")})
        self.assertEqual(hashlib.sha256(original).digest(),expected)

if __name__=="__main__":
    unittest.main()
