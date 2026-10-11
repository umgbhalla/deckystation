from pathlib import Path
import sys
import tempfile
import unittest
import vdf

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import build_layout
import install_controller

class ControllerTests(unittest.TestCase):
    def test_all_sources_and_dictation_reserved(self):
        data = build_layout.layout()
        text = vdf.dumps(data, pretty=True)
        loaded = vdf.loads(text, mapper=vdf.VDFDict, merge_duplicate_keys=False)
        groups = loaded['controller_mappings'].get_all_for('group')
        self.assertEqual(len(groups), 9)
        self.assertEqual({g['id'] for g in groups}, set(loaded['controller_mappings']['preset']['group_source_bindings']))
        self.assertNotIn('left_bumper', text)
        self.assertNotIn('right_bumper', text)
        self.assertNotIn('key_press Q', text)
        self.assertNotIn('key_press W', text)
        self.assertEqual(text, (ROOT/'config/herdr-controller.vdf').read_text())
        tabs = next(g for g in groups if g['mode']=='switches')['inputs']
        self.assertEqual(len(tabs['button_back_left_upper']['activators']['Full_Press']['bindings'].get_all_for('binding')), 3)

    def test_installer_preserves_other_games_and_backs_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);base=root/'steamapps/common/Steam Controller Configs/1/config'
            base.mkdir(parents=True)
            path=base/'configset_controller_neptune.vdf'
            before=vdf.dumps({'controller_config': {'other-game': {'workshop': '123'}, 'herdr': {'template': 'old'}}}, pretty=True)
            path.write_text(before)
            install_controller.install(root,'1')
            data=install_controller.load(path)
            self.assertEqual(data['controller_config']['other-game']['workshop'],'123')
            self.assertEqual(data['controller_config']['herdr']['autosave'],'1')
            self.assertEqual(next(base.glob('*.backup-*')).read_text(),before)
            self.assertTrue((base/'herdr/controller_neptune.vdf').is_file())

if __name__ == '__main__':
    unittest.main()
