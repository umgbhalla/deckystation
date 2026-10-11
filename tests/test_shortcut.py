from pathlib import Path
import tempfile
import sys
import unittest
import vdf
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import install_shortcut

class ShortcutTests(unittest.TestCase):
    def test_preserve_existing_and_no_duplicate_on_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'userdata/1/config/shortcuts.vdf';path.parent.mkdir(parents=True)
            previous={'shortcuts':{'0':{'AppName':'Existing game','appid':123,'tags':{'0':'Keep'}}}}
            path.write_bytes(vdf.binary_dumps(previous))
            install_shortcut.install(root,'1',Path('/home/deck'))
            with path.open('rb') as stream:
                data=vdf.binary_load(stream)
            self.assertEqual(data['shortcuts']['0'],previous['shortcuts']['0'])
            self.assertEqual(data['shortcuts']['1']['appid']&0xffffffff,2380454464)
            first=path.read_bytes()
            install_shortcut.install(root,'1',Path('/home/deck'))
            self.assertEqual(first,path.read_bytes())
            self.assertEqual(next(path.parent.glob('*.backup-*')).read_bytes(),vdf.binary_dumps(previous))
