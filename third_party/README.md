# Local upstream checkout

Run `python scripts/fetch_upstream.py` from the repository root to obtain PERIOD
at the commit in `config/upstream.json`. The downloaded `PERIOD/` directory is
ignored. Do not commit the nested Git repository or downloaded dependencies.
The preserved original license is in `licenses/PERIOD-MIT.txt`.
