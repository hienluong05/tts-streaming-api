import re
from typing import List

class HierarchicalSentenceSplitter:
    # Vietnamese conjunctions suitable for natural breathing pauses
    CONJUNCTIONS = [
        r"\bvà\b", r"\bhoặc\b", r"\bnhưng\b", r"\bsong\b",
        r"\btuy nhiên\b", r"\bmặc dù\b", r"\bvì vậy\b",
        r"\bcho nên\b", r"\bdo đó\b", r"\bbởi vì\b",
        r"\bthế nên\b", r"\bđồng thời\b", r"\bđể\b", r"\brằng\b", r"\bmà\b"
    ]

    def __init__(self, min_chars: int = 40, target_chars: int = 140, max_chars: int = 180):
        self.min_chars = min_chars
        self.target_chars = target_chars
        self.max_chars = max_chars

    def split_sentences(self, text: str) -> List[str]:
        """
        Step 1: Split on true sentence boundaries (protecting abbreviations).
        """
        try:
            from underthesea import sent_tokenize
            return sent_tokenize(text)
        except ImportError:
            # Fallback regex with negative lookbehind for abbreviations and digits
            # Use capturing group to keep delimiters
            pattern = r"(?<!\bTP)(?<!\bGS)(?<!\bTS)(?<!\bBS)(?<!\bMr)(?<!\bMrs)(?<!\d)([.?!]+)(?:\s+|\n+|$)"
            parts = re.split(pattern, text)
            sentences = []
            for i in range(0, len(parts)-1, 2):
                sentences.append(parts[i] + parts[i+1])
            if len(parts) % 2 == 1 and parts[-1].strip():
                sentences.append(parts[-1])
            return [s.strip() for s in sentences if s.strip()]

    def _split_by_delimiters(self, text: str, delimiters: List[str]) -> List[str]:
        """Splits text while preserving delimiters attached to the preceding phrase."""
        pattern = f"({'|'.join(delimiters)})"
        parts = re.split(pattern, text)
        segments = []
        for i in range(0, len(parts) - 1, 2):
            segments.append(parts[i] + parts[i + 1])
        if len(parts) % 2 == 1 and parts[-1].strip():
            segments.append(parts[-1])
        return [s.strip() for s in segments if s.strip()]

    def _split_long_sentence(self, sentence: str) -> List[str]:
        """Hierarchically breaks down a sentence exceeding max_chars."""
        if len(sentence) <= self.max_chars:
            return [sentence]

        # Tier 2: Split by colon, semicolon, dash
        clauses = self._split_by_delimiters(sentence, [r";", r":", r"—", r" - "])
        if all(len(c) <= self.max_chars for c in clauses) and len(clauses) > 1:
            return self._merge_short_segments(clauses)

        # Tier 3: Split by comma
        comma_segments = self._split_by_delimiters(sentence, [r","])
        if all(len(c) <= self.max_chars for c in comma_segments) and len(comma_segments) > 1:
            return self._merge_short_segments(comma_segments)

        # Tier 4: Split before Vietnamese conjunctions
        conj_pattern = f"(\\s+(?:{'|'.join(self.CONJUNCTIONS)})\\s+)"
        conj_parts = re.split(conj_pattern, sentence, flags=re.IGNORECASE)
        if len(conj_parts) > 1:
            rebuilt = []
            curr = conj_parts[0]
            for i in range(1, len(conj_parts), 2):
                conj = conj_parts[i]
                next_part = conj_parts[i + 1] if i + 1 < len(conj_parts) else ""
                if len(curr) + len(conj) + len(next_part) <= self.max_chars:
                    curr += conj + next_part
                else:
                    if curr.strip():
                        rebuilt.append(curr.strip())
                    curr = conj.strip() + " " + next_part
            if curr.strip():
                rebuilt.append(curr.strip())
            return rebuilt

        # Tier 5: Fallback soft word split near target_chars
        words = sentence.split(" ")
        chunks = []
        current_chunk = []
        current_len = 0
        for w in words:
            if current_len + len(w) + 1 > self.target_chars and current_len >= self.min_chars:
                chunks.append(" ".join(current_chunk))
                current_chunk = [w]
                current_len = len(w)
            else:
                current_chunk.append(w)
                current_len += len(w) + 1
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def _merge_short_segments(self, segments: List[str]) -> List[str]:
        """Greedily merges small segments up to target_chars to prevent tiny choppy speech audio."""
        merged = []
        buffer = ""
        for seg in segments:
            if not buffer:
                buffer = seg
            elif len(buffer) + len(seg) + 1 <= self.target_chars:
                buffer += " " + seg
            else:
                merged.append(buffer)
                buffer = seg
        if buffer:
            merged.append(buffer)
        return merged

    def chunk_text(self, text: str) -> List[str]:
        """Entry point: processes full text into optimal streaming TTS chunks."""
        raw_sentences = self.split_sentences(text)
        final_chunks = []
        for s in raw_sentences:
            sub_chunks = self._split_long_sentence(s)
            final_chunks.extend(sub_chunks)
        return final_chunks
