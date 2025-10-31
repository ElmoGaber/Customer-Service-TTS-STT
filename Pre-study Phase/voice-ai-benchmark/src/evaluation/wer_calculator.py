import jiwer
from src.utils.logger_config import get_logger

logger = get_logger("wer_calculator", "logs/benchmark.log")

def calculate_wer(reference_text: str, hypothesis_text: str) -> float:
    """
    Calculates Word Error Rate (WER) between reference and hypothesis strings.
    """
    try:
        transformation = jiwer.Compose([
            jiwer.RemovePunctuation(),
            jiwer.ToLowerCase(),
            jiwer.Strip(),
            jiwer.RemoveMultipleSpaces()
        ])
        wer = jiwer.wer(
            reference_text, 
            hypothesis_text, 
            truth_transform=transformation, 
            hypothesis_transform=transformation
        )
        logger.info(f"WER calculated successfully: {wer:.4f}")
        return round(wer, 4)
    except Exception as e:
        logger.error(f"Error calculating WER: {str(e)}")
        return 1.0
