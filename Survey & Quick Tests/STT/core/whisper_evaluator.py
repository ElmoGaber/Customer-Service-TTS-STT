from jiwer import wer

def evaluate_transcript(reference: str, transcript: str):
    """Compute WER score"""
    return wer(reference, transcript)
