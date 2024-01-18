from dataclasses import dataclass


@dataclass
class Market:
    """Market data class."""

    market: str
    korean_name: str
    english_name: str

    @property
    def key(self) -> str:
        """Get a key to search."""
        return f"{self.market} ({self.korean_name}, {self.english_name})"
