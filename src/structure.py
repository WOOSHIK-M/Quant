from dataclasses import dataclass


@dataclass
class Market:
    """Data class of market code."""

    market: str
    korean_name: str
    english_name: str
