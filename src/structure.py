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
        return f"{self.korean_name}_{self.english_name}_{self.market}"

    @staticmethod
    def resolve_key(key: str) -> str:
        """Resolve the given key to get the market code."""
        return key.split("_")[-1]
