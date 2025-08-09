"""Simple bet tracking utilities using only the standard library."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List


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
    """Track bets in a CSV file using only the standard library."""

    def __init__(self, filepath: str | Path | None = None) -> None:
        self.filepath = Path(filepath) if filepath else Path(__file__).with_name("bets.csv")
        self.bets: List[Bet] = []

        if self.filepath.exists():
            with self.filepath.open(newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.bets.append(
                        Bet(
                            datetime.fromisoformat(row["date"]),
                            row["fighter"],
                            float(row["odds"]),
                            float(row["stake"]),
                            row["bookmaker"],
                            row.get("result") or None,
                            float(row["payout"]) if row.get("payout") else None,
                        )
                    )

    def add_bet(self, bet: Bet) -> None:
        """Append a bet to the CSV file and in-memory list."""
        self.bets.append(bet)
        write_header = not self.filepath.exists()
        with self.filepath.open("a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["date", "fighter", "odds", "stake", "bookmaker", "result", "payout"])
            writer.writerow([
                bet.date.isoformat(),
                bet.fighter,
                bet.odds,
                bet.stake,
                bet.bookmaker,
                bet.result or "",
                bet.payout if bet.payout is not None else "",
            ])

    def summary(self) -> List[dict]:
        """Return bet history with individual profits and total."""
        rows: List[dict] = []
        total = 0.0
        for b in self.bets:
            payout = b.payout or 0.0
            profit = payout - b.stake
            total += profit
            rows.append(
                {
                    "date": b.date.strftime("%Y-%m-%d"),
                    "fighter": b.fighter,
                    "odds": b.odds,
                    "stake": b.stake,
                    "bookmaker": b.bookmaker,
                    "result": b.result or "",
                    "payout": payout,
                    "profit": round(profit, 2),
                }
            )
        rows.append({"date": "TOTAL", "profit": round(total, 2)})
        return rows

