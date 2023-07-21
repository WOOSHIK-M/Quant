from dataclasses import dataclass


@dataclass
class Market:
    """Data class of market code."""

    market: str
    korean_name: str
    english_name: str

    def __repr__(self) -> str:
        """Get representation of this."""
        return f"{self.korean_name} ({self.english_name}, {self.market})"
