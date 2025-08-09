"""Command-line boxing odds and bet tracking app using only stdlib."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import List

try:  # support running as a module or a script
    from .bet_tracker import Bet, BetTracker
except ImportError:  # pragma: no cover - fallback when executed as a script
    from bet_tracker import Bet, BetTracker

DEFAULT_ODDS_FILE = Path(__file__).with_name("boxing_odds.csv")
DEFAULT_BETS_FILE = Path(__file__).with_name("bets.csv")


def load_odds(path: Path = DEFAULT_ODDS_FILE) -> List[dict]:
    """Load odds rows from a CSV file, parsing times and odds."""
    if not path.exists():
        return []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows: List[dict] = []
        for row in reader:
            row["decimal_odds"] = float(row["decimal_odds"])
            # Parse time if provided; fallback to raw string
            try:
                row["time"] = datetime.fromisoformat(row["time"])
            except Exception:
                row["time"] = row["time"]
            rows.append(row)
        return rows


def upcoming_fights(rows: List[dict]) -> List[dict]:
    """Return upcoming fights sorted by earliest available time."""
    fights: dict[str, datetime] = {}
    for r in rows:
        eid = r["event_id"]
        time = r["time"]
        if eid not in fights or time < fights[eid]:
            fights[eid] = time
    return [{"event_id": eid, "time": fights[eid]} for eid in sorted(fights, key=fights.get)]


def best_odds(rows: List[dict]) -> List[dict]:
    """Return best odds for each fighter in every event."""
    best: dict[tuple[str, str], dict] = {}
    for r in rows:
        key = (r["event_id"], r["fighter"])
        if key not in best or r["decimal_odds"] > best[key]["decimal_odds"]:
            best[key] = {
                "event_id": r["event_id"],
                "time": r["time"],
                "fighter": r["fighter"],
                "bookmaker": r["bookmaker"],
                "decimal_odds": r["decimal_odds"],
            }
    return list(best.values())


def value_bets(rows: List[dict], threshold: float = 0.05) -> List[dict]:
    """Identify value bets where best odds exceed average by ``threshold``."""
    grouped: defaultdict[tuple[str, str], List[dict]] = defaultdict(list)
    for r in rows:
        grouped[(r["event_id"], r["fighter"])].append(r)

    results: List[dict] = []
    for (event_id, fighter), lst in grouped.items():
        odds = [r["decimal_odds"] for r in lst]
        avg_odds = mean(odds)
        best_row = max(lst, key=lambda r: r["decimal_odds"])
        value_pct = (best_row["decimal_odds"] - avg_odds) / avg_odds
        if value_pct >= threshold:
            results.append(
                {
                    "event_id": event_id,
                    "time": best_row["time"],
                    "fighter": fighter,
                    "bookmaker": best_row["bookmaker"],
                    "avg_odds": round(avg_odds, 2),
                    "best_odds": best_row["decimal_odds"],
                    "value_pct": round(value_pct, 2),
                }
            )
    results.sort(key=lambda r: r["value_pct"], reverse=True)
    return results


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Boxing betting utilities")
    parser.add_argument("--odds-file", type=Path, default=DEFAULT_ODDS_FILE, help="Path to odds CSV")
    parser.add_argument("--bets-file", type=Path, default=DEFAULT_BETS_FILE, help="Path to bets CSV")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("fights", help="List upcoming fights")
    sub.add_parser("best", help="Show best available odds")

    value = sub.add_parser("value", help="List potential value bets")
    value.add_argument("--threshold", type=float, default=0.05, help="Minimum value percentage")

    add_bet = sub.add_parser("add-bet", help="Record a bet")
    add_bet.add_argument("fighter")
    add_bet.add_argument("odds", type=float)
    add_bet.add_argument("stake", type=float)
    add_bet.add_argument("bookmaker")
    add_bet.add_argument("--result", choices=["win", "loss"])
    add_bet.add_argument("--payout", type=float)

    sub.add_parser("summary", help="Show bet history and profits")

    return parser.parse_args()


def _format(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.2f}"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def _print_table(rows: List[dict], columns: List[str] | None = None) -> None:
    if not rows:
        print("No data available")
        return
    if columns is None:
        columns = list(rows[0].keys())
    widths = {c: max(len(c), *(len(_format(r.get(c, ""))) for r in rows)) for c in columns}
    header = " ".join(c.ljust(widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for r in rows:
        line = " ".join(_format(r.get(c, "")).ljust(widths[c]) for c in columns)
        print(line)


def main() -> None:
    args = _parse_args()

    if args.command in {"fights", "best", "value"}:
        odds = load_odds(args.odds_file)
        if args.command == "fights":
            _print_table(upcoming_fights(odds), ["event_id", "time"])
        elif args.command == "best":
            _print_table(best_odds(odds), ["event_id", "time", "fighter", "bookmaker", "decimal_odds"])
        elif args.command == "value":
            _print_table(
                value_bets(odds, threshold=args.threshold),
                ["event_id", "time", "fighter", "bookmaker", "avg_odds", "best_odds", "value_pct"],
            )
    elif args.command == "add-bet":
        tracker = BetTracker(args.bets_file)
        bet = Bet(
            datetime.now(),
            args.fighter,
            args.odds,
            args.stake,
            args.bookmaker,
            args.result,
            args.payout,
        )
        tracker.add_bet(bet)
        print("Bet added")
    elif args.command == "summary":
        tracker = BetTracker(args.bets_file)
        _print_table(tracker.summary())


if __name__ == "__main__":  # pragma: no cover
    main()

