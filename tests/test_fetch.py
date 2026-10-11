import hashlib
import io
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import fetch_artifact

class FetchTests(unittest.TestCase):
    def test_verified_download_and_hash_failure(self):
        payload=b'verified artifact'
        entry={'file': {'url':'https://example.invalid/file','sha256':hashlib.sha256(payload).hexdigest()}}
        with tempfile.TemporaryDirectory() as tmp, patch.object(fetch_artifact.json,'loads',return_value=entry):
            destination=Path(tmp)/'file'
            with patch.object(fetch_artifact.urllib.request,'urlopen',return_value=io.BytesIO(payload)):
                fetch_artifact.fetch('file',destination)
            self.assertEqual(destination.read_bytes(),payload)
            with patch.object(fetch_artifact.urllib.request,'urlopen',side_effect=AssertionError('Unexpected network')):
                fetch_artifact.fetch('file',destination)
            destination.unlink()
            with patch.object(fetch_artifact.urllib.request,'urlopen',return_value=io.BytesIO(b'wrong')):
                with self.assertRaises(SystemExit):fetch_artifact.fetch('file',destination)
            self.assertFalse(destination.exists())
            self.assertEqual(list(Path(tmp).iterdir()),[])
