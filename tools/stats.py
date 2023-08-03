import json
import config
from tools.alias import Alias
from model.aliases import Aliases
from model.tracker import Tracker
import model.documents as documents
import pandas as pd

yoy_days = 365

class Stats(Alias):
    def run(self):
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('tool', choices=['stats'], help=f'Subcommand stats')

        ap.add_argument('name', nargs="*", help=f'ISIN or alias identifying a security.')

        ap.add_argument('--verbose', '-v', action='store_true', default=False, help='Verbose printing.')
        ap.add_argument('--weak-match', action='store_true', default=False, help='Enables weak matching of isin and alias for <name>')

        args = ap.parse_args()

        config.set_config(args)


        if not args.name:
            isins = Tracker().get_tracked()
            names = [Aliases().get_favourite(n) for n in isins]
            args.name = [n if n else i for n,i in zip(names, isins)]

        df = self.__get_docs(args)

        start_date = self.__get_startdate(df)

        df = self.__get_prices(df, start_date)

        self.__make_charts(df)


    def __get_docs(self, args):
        df = {}
        for n in args.name:
            name = Aliases().match_name(n, args.weak_match)
            if len(name) != 1:
                print('Can not set tracker')
                print('Parameter passed to <name> does not identify a unique ISIN')
                print(f'Possible matches are:')
                self._Alias__print_names(Aliases().match_name(n, True))
                return

            isin = next(iter(name))

            docs = documents.Documents().get(isin)

            isin_div = Aliases().get_dividend_cash(isin)
            if isin_div:
                docs_div = documents.Documents().get(isin_div)
                docs = pd.concat([docs, docs_div.loc[docs_div.Type == documents.DocType.DIVIDEND]])

            df[n] = (isin, docs)

        return df

    def __get_startdate(self, df):
        start_date = df[next(iter(df))][1].ApplicationDate.min()
        for isin, docs in df.values():
            start_date = min(start_date, docs.ApplicationDate.min())
        return start_date

    def __get_prices(self, df, start_date):
        from model.estimate_provision import estimate_cost

        summary = pd.DataFrame()
        for n in df:
            isin, docs = df[n]

            prices = Tracker().get_prices(isin, start_date)
            prices['expenses'] = documents.get_expenses(docs, start_date).expenses
            prices['nominal'] = documents.get_nominal(docs, start_date).nominal
            prices['dividends'] = documents.get_dividends(docs, start_date).dividends
            prices['invest_value'] = prices.nominal * prices.adjclose
            prices['net_value'] = prices.invest_value + prices.dividends
            prices['estimate_sell_fees'] = prices.net_value.apply(estimate_cost)
            prices['estimate_sell_taxes'] = ((prices.net_value - prices.expenses) * 0.305).clip(lower=0)
            prices['net_value_adjusted'] = prices.net_value - prices.estimate_sell_fees - prices.estimate_sell_taxes
            prices['fees'] = documents.get_fees(docs, start_date).fees
            prices['taxes'] = documents.get_taxes(docs, start_date).taxes


            df[n] = prices

            if summary.empty:
                summary['date'] = prices.date

            for col in ['expenses', 'dividends', 'invest_value', 'net_value', 'estimate_sell_fees', 'estimate_sell_taxes', 'net_value_adjusted', 'fees', 'taxes']:
                summary[col] = prices[col] if col not in summary else summary[col] + prices[col]

        if len(df) > 1:
            df['summary'] = summary

        for n, prices in df.items():
            prices['ddividends'] = prices.dividends.diff()
            prices['dfees'] = prices.fees.diff()
            prices['dtaxes'] = prices.taxes.diff()

            prices['performance'] = prices.net_value - prices.expenses
            prices['performance_percent'] = 100 / prices.expenses * prices.performance
            prices['performance_yoy'] = prices.net_value.diff(yoy_days) - prices.expenses.diff(yoy_days)
            prices['performance_yoy_percent'] = 100 / prices.expenses.rolling(yoy_days).mean() * prices.performance_yoy

            prices['performance_adjusted'] = prices.net_value_adjusted - prices.expenses
            prices['performance_adjusted_percent'] = 100 / prices.expenses * prices.performance_adjusted
            prices['performance_adjusted_yoy'] = prices.net_value_adjusted.diff(yoy_days) - prices.expenses.diff(yoy_days)
            prices['performance_adjusted_yoy_percent'] = 100 / prices.expenses.rolling(yoy_days).mean() * prices.performance_adjusted_yoy

            prices['year'] = prices.date.apply(lambda x: x.year)
            dividend_yield_sum = 0
            dividend_yield_sum_percent = 0
            count = 0
            g = prices.groupby('year')
            for y in g.groups:
                gy = g.get_group(y)
                count = count + 1

                dividend_yield = gy.ddividends.loc[prices.year == y].sum()
                dividend_yield_percent = (100 / gy.expenses * gy.ddividends).loc[prices.year == y].sum()

                dividend_yield_sum = dividend_yield_sum + dividend_yield
                dividend_yield_sum_percent = dividend_yield_sum_percent + dividend_yield_percent

                prices.loc[prices.year == y, 'dividend_yield'] = dividend_yield
                prices.loc[prices.year == y, 'dividend_yield_percent'] = dividend_yield_percent
                prices.loc[prices.year == y, 'dividend_yield_yearly_avg'] = dividend_yield_sum / count
                prices.loc[prices.year == y, 'dividend_yield_yearly_avg_percent'] = dividend_yield_sum_percent / count

        return df

    def __make_charts(self, df):
        from plotly.subplots import make_subplots
        import plotly.graph_objects as go

        for n, prices in df.items():

            fig = make_subplots(
                rows=1, cols=2,
                column_widths=[5,1],
            )

            prices['hovertext'] =   '<br>-------------------------------------------------------------------' + \
                                    '<br>net value' + \
                                    '<br>     investment value (inc. fees and taxes)   : ' + prices.invest_value.apply(         lambda x: f'{x:8.2f}') + \
                                    '<br>     cum. dividends                           : ' + prices.dividends.apply(            lambda x: f'{x:8.2f}') + \
                                    '<br>    (cum. fees)                               : ' + prices.fees.apply(                 lambda x: f'         ({-x:8.2f})') + \
                                    '<br>    (cum. taxes)                              : ' + prices.taxes.apply(                lambda x: f'         ({-x:8.2f})') + \
                                    '<br>                                               --------------------' + \
                                    '<br>                                                ' + prices.net_value.apply(            lambda x: f'{x:8.2f}') + \
                                    '<br>-------------------------------------------------------------------' + \
                                    '<br>net value (adjusted)' + \
                                    '<br>      estimated fees (sell)                   : ' + prices.estimate_sell_fees.apply(   lambda x: f'         {-x:8.2f}') + \
                                    '<br>      estimated taxes (sell)                  : ' + prices.estimate_sell_taxes.apply(  lambda x: f'         {-x:8.2f}') + \
                                    '<br>                                               --------------------' + \
                                    '<br>                                                ' + prices.net_value_adjusted.apply(   lambda x: f'{x:8.2f}') + \
                                    '<br><br>-------------------------------------------------------------------' + \
                                    '<br>performance                                   : ' + prices.performance.apply(     lambda x: f'{x:8.2f}') + prices.performance_percent.apply(          lambda x: f' ({x:5.2f}%)') + \
                                    '<br>            y.o.y.                            : ' + prices.performance_yoy.apply( lambda x: f'{x:8.2f}') + prices.performance_yoy_percent.apply( lambda x: f' ({x:5.2f}%)') + \
                                    '<br>-------------------------------------------------------------------' + \
                                    '<br>performance (adjusted)                        : ' + prices.performance_adjusted.apply(     lambda x: f'{x:8.2f}') + prices.performance_adjusted_percent.apply(          lambda x: f' ({x:5.2f}%)') + \
                                    '<br>            y.o.y.                            : ' + prices.performance_adjusted_yoy.apply( lambda x: f'{x:8.2f}') + prices.performance_adjusted_yoy_percent.apply( lambda x: f' ({x:5.2f}%)') + \
                                    '<br><br>-------------------------------------------------------------------' + \
                                    '<br>dividend yield ' + prices.year.apply(str) + '                           : ' + prices.dividend_yield.apply(       lambda x: f'{x:8.2f}') + prices.dividend_yield_percent.apply(       lambda x: f' ({x:5.2f}%)') + \
                                    '<br>               p.a. average until today       : ' + prices.dividend_yield_yearly_avg.apply(lambda x: f'{x:8.2f}') + prices.dividend_yield_yearly_avg_percent.apply(lambda x: f' ({x:5.2f}%)') + \
                                    '<br>-------------------------------------------------------------------' + \
                (prices.ddividends + prices.dfees + prices.dtaxes).apply(lambda x: '<br>Single day payments:' if x else '') + \
                prices.ddividends.apply(lambda x: '' if x == 0 else f'<br>     dividends:                                 {x:8.2f}') + \
                prices.dfees.apply(     lambda x: '' if x == 0 else f'<br>     fees:                                                {-x:8.2f}') + \
                prices.dtaxes.apply(    lambda x: '' if x == 0 else f'<br>     taxes:                                               {-x:8.2f}')

            

            fig.add_trace(go.Scatter(
                x=prices.date,
                y=prices.expenses,
                marker_color='blue',
                hovertext=prices.hovertext,
                name=f'expenses'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=prices.date,
                y=prices.net_value,
                marker_color='green',
                hoverinfo='none',
                name=f'net value'
            ), row=1, col=1)

            fig.add_trace(go.Scatter(
                x=prices.date,
                y=prices.net_value_adjusted,
                fill='tonexty',
                fillcolor='rgba(255,0,0,0.1)',
                marker_color='red',
                hoverinfo='none',
                name=f'net value (including est. fees and tax)'
            ), row=1, col=1)

            fig.add_trace(go.Bar(
                x=prices.date,
                y=prices.ddividends,
                marker_color='green',
                hoverinfo='none',
                name=f'dividends'
            ))
            fig.add_trace(go.Bar(
                x=prices.date,
                y=-prices.dtaxes,
                marker_color='red',
                hoverinfo='none',
                name=f'taxes'
            ))
            fig.add_trace(go.Bar(
                x=prices.date,
                y=-prices.dfees,
                marker_color='tomato',
                hoverinfo='none',
                name=f'fees'
            ))

            fig.add_trace(go.Scatter(x=[0,1,1,0], y=[0,0,1,1], fill='toself', fillcolor='white'), row=1, col=2)

            fig.add_annotation({
                'font': {
                    'family':'Courier New, Droid Sans Mono',
                    'size':16,
                },
                'text': prices.hovertext.iloc[-1],
                'align':'left',
            },row=1,col=2)
                
                
            fig.update_xaxes(range=[0.1,0.9],showticklabels=False, row=1, col=2)
            fig.update_yaxes(range=[0.1,0.9],showticklabels=False, row=1, col=2)

            fig.update_traces(hovertemplate=None)
            fig.update_layout(
                title_text=n,
                dragmode='pan',
                hovermode='x unified',
                hoverlabel=dict(
                    font_size=16,
                    font_family="Courier New, Droid Sans Mono"
                )
            )
            fig.show(
                config={
                    "scrollZoom": True,
                    "modeBarButtonsToAdd": ["drawrect", "eraseshape"],
                    "modeBarButtonsToRemove": ["select", "lasso2d"],
                }
            )






    def get_complete_positional_args_options(self, args):
        if len(args) > 1:
            return None

        name = args[-1] if args else ''
        names = Aliases().match_name(name, True)

        return list(names.keys()) + self._Alias__flatten_aliases(names)

    def get_complete_args(self):
        return {
            '--verbose':    (0, [], None),
        }

