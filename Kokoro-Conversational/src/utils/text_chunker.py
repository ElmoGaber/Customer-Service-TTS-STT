from .config import settings

class TextChunker:
    """A class to handle intelligent text chunking for voice generation."""

    def __init__(self):
        self.current_text = []
        self.found_first_sentence = False
        self.semantic_breaks = {
            "however": 4,
            "therefore": 4,
            "furthermore": 4,
            "moreover": 4,
            "nevertheless": 4,
            "while": 3,
            "although": 3,
            "unless": 3,
            "since": 3,
            "and": 2,
            "but": 2,
            "because": 2,
            "then": 2,
        }
        self.punctuation_priorities = {
            ".": 5,
            "!": 5,
            "?": 5,
            ";": 4,
            ":": 4,
            ",": 3,
            "-": 2,
        }

    def should_process(self, text: str) -> bool:
        if any(text.endswith(p) for p in self.punctuation_priorities):
            return True

        words = text.split()
        target = (
            settings.FIRST_SENTENCE_SIZE
            if not self.found_first_sentence
            else settings.TARGET_SIZE
        )
        return len(words) >= target

    def find_break_point(self, words: list, target_size: int) -> int:
        if len(words) <= target_size:
            return len(words)

        break_points = []

        for i, word in enumerate(words[: target_size + 3]):
            word_lower = word.lower()
            priority = self.semantic_breaks.get(word_lower, 0)
            for punct, punct_priority in self.punctuation_priorities.items():
                if word.endswith(punct):
                    priority = max(priority, punct_priority)
            if priority > 0:
                break_points.append((i, priority, -abs(i - target_size)))

        if not break_points:
            return target_size

        break_points.sort(key=lambda x: (x[1], x[2]), reverse=True)
        return break_points[0][0] + 1

    def process(self, text: str, audio_queue) -> str:
        """Process full text at once instead of chunking small parts."""
        if not text:
            return ""

        text = text.strip()
        if not text:
            return ""

        from .voice import split_into_sentences
        sentences = split_into_sentences(text)

        if not sentences:
            sentences = [text]

        audio_queue.add_sentences(sentences)
        return ""
