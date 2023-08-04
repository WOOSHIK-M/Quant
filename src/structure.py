from dataclasses import dataclass
from pathlib import Path

DATA_PATH = Path("data")
DATA_PATH.mkdir(exist_ok=True, parents=True)


@dataclass
class Market:
    """Data class of market code."""

    market: str
    korean_name: str
    english_name: str

    def __repr__(self) -> str:
        """Get representation of this."""
        return f"{self.korean_name} ({self.english_name}, {self.market})"


@dataclass
class ChartProperty:
    """The properties of ohclv chart."""

    market_code: str = "KRW-BTC"
    unit: str = "days"
    sub_unit: int = 60

    @property
    def fname(self) -> Path:
        """Get the save file name."""
        return DATA_PATH / f"{self.market_code}_{self.unit}_{self.sub_unit}.pkl"
