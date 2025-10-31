import unittest
from pathlib import Path

class DocsExistTest(unittest.TestCase):
    def test_docs_present(self):
        root = Path(__file__).resolve().parents[1]
        self.assertTrue((root / 'docs' / 'architecture.md').exists())
        self.assertTrue((root / 'docs' / 'theoretical_notes.md').exists())

if __name__ == '__main__':
    unittest.main()
