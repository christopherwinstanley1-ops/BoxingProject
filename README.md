# Boxing Betting Utilities

This project contains scripts for working with boxing betting data.  A new
command-line application `boxing_app.py` provides quick access to:

- **Upcoming fights** based on the collected odds data.
- **Best available odds** for each fighter across bookmakers.
- **Value bets** where the best odds significantly exceed the average market price.

Run the app with:

```bash
python boxingproject/boxing_app.py
```

A simple `BetTracker` utility is also included for recording and reviewing
betting history.  Example usage:

```python
from boxingproject.bet_tracker import Bet, BetTracker
from datetime import datetime

tracker = BetTracker()
tracker.add_bet(Bet(datetime.now(), "Fighter Name", 2.5, 10, "bookmaker"))
print(tracker.summary())
```
