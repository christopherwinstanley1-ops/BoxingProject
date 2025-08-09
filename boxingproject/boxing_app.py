"""Simple command-line boxing odds app.

This module loads boxing odds data from a CSV file and provides
utilities for:
    * Listing upcoming fights
    * Finding the best available odds for each fighter
    * Highlighting potential value bets (odds notably above average)

The data source is expected to be `boxing_odds.csv` located in the same
folder as this script.  The CSV is produced by the existing data
collection notebooks and scripts in this repository.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

ODDS_FILE = Path(__file__).with_name("boxing_odds.csv")


def load_odds() -> pd.DataFrame:
    """Load odds data from ``boxing_odds.csv``.

    Returns
    -------
    pandas.DataFrame
        DataFrame containing the raw odds data.
    """
    return pd.read_csv(ODDS_FILE)


def upcoming_fights(df: pd.DataFrame) -> pd.DataFrame:
    """Return upcoming fight times and identifiers.

    Parameters
    ----------
    df:
        Raw odds DataFrame.
    """
    fights = df[["event_id", "time"]].drop_duplicates()
    fights["time"] = pd.to_datetime(fights["time"])
    return fights.sort_values("time")


def best_odds(df: pd.DataFrame) -> pd.DataFrame:
    """Return the best odds for each fighter in every event.

    Parameters
    ----------
    df:
        Raw odds DataFrame.
    """
    ordered = df.sort_values("decimal_odds", ascending=False)
    best = (
        ordered.groupby(["event_id", "fighter", "time"], as_index=False)
        .first()
        [["event_id", "time", "fighter", "bookmaker", "decimal_odds"]]
    )
    best["time"] = pd.to_datetime(best["time"])
    return best


def value_bets(df: pd.DataFrame, threshold: float = 0.05) -> pd.DataFrame:
    """Identify potential value bets.

    A value bet is defined here as a fighter whose best available odds
    are at least ``threshold`` (5% by default) above the average odds
    offered across bookmakers.
    """
    grouped = df.groupby(["event_id", "fighter"])
    avg = grouped["decimal_odds"].mean().rename("avg_odds")
    best = grouped["decimal_odds"].max().rename("best_odds")
    best_bm = df.loc[grouped["decimal_odds"].idxmax(), ["event_id", "fighter", "bookmaker"]]

    merged = (
        pd.concat([avg, best], axis=1)
        .reset_index()
        .merge(best_bm, on=["event_id", "fighter"])
    )
    merged["value_pct"] = (merged["best_odds"] - merged["avg_odds"]) / merged["avg_odds"]
    return merged[merged["value_pct"] >= threshold].sort_values("value_pct", ascending=False)


def main() -> None:
    """Simple CLI entry-point."""
    df = load_odds()
    print("Upcoming fights:")
    print(upcoming_fights(df), end="\n\n")

    print("Best odds:")
    print(best_odds(df), end="\n\n")

    print("Value bets:")
    print(value_bets(df))


if __name__ == "__main__":
    main()
