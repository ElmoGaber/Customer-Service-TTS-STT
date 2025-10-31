import unittest
from pathlib import Path
from src.smoke_tests.stt_test_runner import run_smoke_test


class SmokeTestCase(unittest.TestCase):
    def test_google_placeholder(self):
        p = Path('outputs/samples/test_audio.wav')
        # We expect the placeholder to run without raising
        res = run_smoke_test('google_speech', __import__('src.stt.google_speech', fromlist=['GoogleSpeechSTT']).GoogleSpeechSTT, p)
        self.assertIn('status', res)


if __name__ == '__main__':
    unittest.main()