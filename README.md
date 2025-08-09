# Boxing Betting Utilities

This project contains scripts for working with boxing betting data.  The
`boxing_app.py` script is a small all-in-one command-line application that
relies only on Python's standard library, making it easy to run in any
environment (including Visual Studio) where Python 3.10+ is installed.
The odds and bet files default to `boxing_odds.csv` and `bets.csv` in the
project directory, but you can override them with `--odds-file` and
`--bets-file` options.

Features:

* **Upcoming fights** based on the collected odds data
* **Best available odds** for each fighter across bookmakers
* **Value bets** where the best odds significantly exceed the market average
* **Bet tracking** with simple profit/loss summaries

The application exposes several sub-commands:

```bash
# list upcoming fights
python boxingproject/boxing_app.py fights

# show best odds for each fighter
python boxingproject/boxing_app.py best

# highlight potential value bets (10% above average)
python boxingproject/boxing_app.py value --threshold 0.1

# record a bet and view your history
python boxingproject/boxing_app.py add-bet "Fighter" 2.5 10 Bookmaker
python boxingproject/boxing_app.py summary

# specify custom file locations
python boxingproject/boxing_app.py --odds-file data/odds.csv best
python boxingproject/boxing_app.py --bets-file my_bets.csv summary
```

The odds data must be stored in `boxingproject/boxing_odds.csv` by default.
Bet records are saved to `boxingproject/bets.csv` unless a different file is
specified. Times in the odds file should be ISO timestamps so they can be
sorted and displayed cleanly.
