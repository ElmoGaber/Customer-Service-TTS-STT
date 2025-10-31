from src.smoke_tests.stt_test_runner import main
from pathlib import Path
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', type=str, default='outputs/samples/test_audio.wav')
    args = parser.parse_args()
    main(Path(args.sample))
