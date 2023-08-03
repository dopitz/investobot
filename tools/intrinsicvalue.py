
import config
from tools.alias import Alias
from model.aliases import Aliases
from model.tracker import Tracker as Trackers
import pandas as pd

class IntrinsicValue():
    def run(self):
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('tool', choices=['intrinsic-value'], help=f'Subcommand intrinsic-value')

        ap.add_argument('--watch', default=None, help=f'Ticker symbol on yahoo finance.')
        ap.add_argument('--remove-watch', default=None, help=f'Ticker symbol on yahoo finance.')
        ap.add_argument('--compute', default=None, help=f'Ticker symbol on yahoo finance.')
        ap.add_argument('--ticker', default=None, help=f'Ticker symbol on yahoo finance.')
        ap.add_argument('--margin', type=float, default=0.5, help=f'Ticker symbol on yahoo finance.')
        ap.add_argument('--discount', type=float, default=0.15, help=f'Ticker symbol on yahoo finance.')
        ap.add_argument('--nyears', type=int, default=10, help=f'Ticker symbol on yahoo finance.')

        args = ap.parse_args()

        config.set_config(args)


        from yahooquery import Ticker

        ticker = Ticker(args.ticker)
        cf = ticker.cash_flow(trailing=False).sort_values(by=['asOfDate'])


        print(args.ticker)
        growth = 2
        dividend_yield = ticker.summary_detail[args.ticker]['fiveYearAvgDividendYield']
        pe = ticker.valuation_measures['PeRatio'].dropna().mean()
        print(ticker.valuation_measures['PeRatio'])
        lynch = (growth + dividend_yield) / pe

        print('lynch = (growth + dividend_yield) / pe')
        print(f'{lynch} = ({growth} + {dividend_yield}) / {pe}')


        exit()

        fcf = pd.DataFrame()
        fcf['AsOfDate'] = cf.asOfDate
        fcf['Total'] = cf.FreeCashFlow
        fcf['Rate'] = fcf.Total.diff() / fcf.Total
        fcf['DiscountedRate'] = fcf.Total.diff() / fcf.Total * [pow(1 - args.discount, i - 1) for i in range(len(fcf), 0, -1)]

        fcf_readable = fcf.reset_index(drop=True)
        fcf_readable.Total = fcf_readable.Total.apply(IntrinsicValue.convertMBT)
        print(f'Free Cash Flow of {args.ticker}:')
        print(fcf_readable)
        print('')

        fcf = fcf.dropna()
        growth_est = sum(fcf.DiscountedRate) / sum([pow(1 - args.discount, i - 1) for i in range(len(fcf), 0, -1)])
        growth_est = 0.1
        print(f'estimated growth:   {growth_est:.2f}')


        fcf_est = [cf.FreeCashFlow.iloc[-1]]
        for i in range(0, args.nyears):
            fcf_est.append(fcf_est[-1] * (1 + growth_est) * pow(1 - args.discount, i))
            print(IntrinsicValue.convertMBT(fcf_est[-1]))

        intrinsic_value = sum(fcf_est[1:]) + args.nyears * fcf_est[-1]
        buy_threshold = intrinsic_value * (1 - args.margin)

        print(f'intrensic value:    {IntrinsicValue.convertMBT(intrinsic_value)}')
        print(f'buy threshold:      {IntrinsicValue.convertMBT(buy_threshold)}')

        market_cap = next(iter(ticker.price.values()))['marketCap']
        print(f'market cap:         {IntrinsicValue.convertMBT(market_cap)}')
        print(f'recommendation:     {"BUY" if market_cap < buy_threshold else "-"}')









    def convertMBT(x):
        if x < 1000000:
            return f'{x:.2f}'

        div = 1000000
        mbt = ''
        for n in ['M', 'B', 'T']:
            x = x / div
            div = 1000
            mbt = n
            if x < 1000:
                break
            x = x

        return f'{x:.2f}{mbt}'





    def get_complete_positional_args_options(self, args):
        return None

    def get_complete_watch_args(self, args):
        return ['a', 'b', 'c']


    def get_complete_args(self):
        return {
            '--watch':          (2, [], self.get_complete_watch_args),
            '--remove-watch':   (1, [], None),
            '--compute':        (1, [], None),
        }


