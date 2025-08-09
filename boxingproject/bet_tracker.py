"""Simple bet tracking utilities."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import pandas as pd


@dataclass
class Bet:
    date: datetime
    fighter: str
    odds: float
    stake: float
    bookmaker: str
    result: str | None = None  # 'win' or 'loss'
    payout: float | None = None


class BetTracker:
    """Track bets in a CSV file."""

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath = Path(filepath) if filepath else Path(__file__).with_name("bets.csv")
        if self.filepath.exists():
            self.bets = pd.read_csv(self.filepath)
        else:
            self.bets = pd.DataFrame(columns=[
                "date", "fighter", "odds", "stake", "bookmaker", "result", "payout"
            ])

    def add_bet(self, bet: Bet) -> None:
        row = {
            "date": bet.date.isoformat(),
            "fighter": bet.fighter,
            "odds": bet.odds,
            "stake": bet.stake,
            "bookmaker": bet.bookmaker,
            "result": bet.result,
            "payout": bet.payout,
        }
        self.bets = pd.concat([self.bets, pd.DataFrame([row])], ignore_index=True)
        self.bets.to_csv(self.filepath, index=False)

    def summary(self) -> pd.DataFrame:
        """Return a summary of profits and losses."""
        df = self.bets.copy()
        df["payout"].fillna(0, inplace=True)
        df["profit"] = df["payout"] - df["stake"]
        return df
