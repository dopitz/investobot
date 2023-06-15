import pandas as pd

from . import DB, aliases

import config

class Tracker(DB):
    def __init__(self):
        super().__init__()
        if not self.has_table('tracker') and not config.DRYRUN:
            self.execute('CREATE TABLE "tracker" ("ISIN" TEXT, "tracker" TEXT, "info_tracker" TEXT)')


    def get_tracker(self, isin: str):
        df = pd.read_sql(f'SELECT * FROM tracker WHERE isin LIKE "{isin}"', self.conn)
        return None if df.empty else df.tracker[0]

    def get_info_tracker(self, isin: str):
        df = pd.read_sql(f'SELECT * FROM tracker WHERE isin LIKE "{isin}"', self.conn)
        return None if df.empty else df.info_tracker[0]

    def get_untracked(self):
        in_aliases = pd.read_sql(f'SELECT ISIN FROM aliases', self.conn).ISIN
        in_tracker = pd.read_sql(f'SELECT ISIN FROM tracker', self.conn).ISIN

        return [isin for isin in in_aliases if isin not in in_tracker]

    def get_untracked(self):
        return list(pd.read_sql(f'SELECT ISIN FROM tracker', self.conn).ISIN)


    def set_tracker(self, isin: str, tracker: str, info_tracker: str = None):
        if not info_tracker:
            info_tracker = tracker

        df = pd.DataFrame({'ISIN': [isin], 'tracker': [tracker], 'info_tracker': [info_tracker]})
        df.to_sql('tracker', self.conn, if_exists='append', index=False)

        aliases.Aliases().make_alias(isin, tracker)
        aliases.Aliases().make_alias(isin, info_tracker)


    def get_prices(self, isin: str, start_date):
        from yahooquery import Ticker as Ticker
        from pandas_datareader import data as pdr
        from datetime import date

        tracker = self.get_tracker(isin)
        print(tracker)
        if not tracker:
            if config.VERBOSE:
                print(f'Can not get prices. ISIN {isin} does not have a tracker set.')
            exit()

        t = Ticker(tracker)
        prices = t.history(period='max', interval='1d', start=start_date)
        # drop unused
        prices = prices.reset_index().drop(columns=['symbol', 'open', 'high', 'low', 'close', 'volume'])

        # re-index and ffill to also have data on weekends and holidays for every ticker
        prices.index = pd.DatetimeIndex(prices.date)
        prices = prices.reindex(pd.date_range(prices.index.min(), date.today()), fill_value=None)
        prices = prices.ffill()
        prices.date = prices.index
        prices = prices.reset_index()

        return prices
