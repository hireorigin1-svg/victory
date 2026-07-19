import hashlib
import math


def vectorize_text(text: str, width: int = 32) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [round(byte / 255, 6) for byte in digest[:width]]


def cosine(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
