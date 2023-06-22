import pandas as pd

from . import DB

import config

class Aliases(DB):
    def __init__(self):
        super().__init__()
        if not self.has_table('aliases') and not config.DRYRUN:
            self.execute('CREATE TABLE "aliases" ("ISIN" TEXT, "alias" TEXT)')

        if not self.has_table('alias_favourites') and not config.DRYRUN:
            self.execute('CREATE TABLE "alias_favourites" ("ISIN" TEXT, "alias" TEXT)')

        if not self.has_table('dividend_cash') and not config.DRYRUN:
            self.execute('CREATE TABLE "dividend_cash" ("ISIN" TEXT, "ISIN_DIV" TEXT)')


    def match_name(self, name: str, weak_match: bool = False):
        if weak_match:
            name = f'%{name}%'

        df = pd.read_sql(f'SELECT * from aliases WHERE alias LIKE "{name}" OR isin LIKE "{name}"', self.conn)
        d = {}
        for i, row in df.iterrows():
            if row.ISIN not in d:
                d[row.ISIN] = [row.alias]
            else:
                d[row.ISIN].append(row.alias)

        return d

    def get_favourite(self, name: str):
        names = self.match_name(name)
        if len(names) == 1:
            df = pd.read_sql(f'SELECT * from alias_favourites WHERE ISIN LIKE "{next(iter(names))}"', self.conn)
            if not df.empty:
                return df.alias[0]
        return None

    

    def make_alias(self, isin: str, alias: str):
        other = self.match_name(alias)
        if other:
            if config.VERBOSE:
                if next(iter(other)) != isin:
                    print(f'ISIN {isin}: Could not make alias "{alias}". Alias is already used by isin "{next(iter(other))}"')
            return

        df = pd.DataFrame({'ISIN': [isin], 'alias': [alias]})
        df.to_sql('aliases', self.conn, if_exists='append', index=False)

    def make_favourite(self, alias: str):
        isin = self.match_name(alias)
        if len(isin) != 1:
            if config.VERBOSE:
                print(f'Alias {alias}: Could not make favourite. Alias does not exist or is ambiguous')
            return

        df = pd.DataFrame({'ISIN': [next(iter(isin))], 'alias': [alias]})
        df.to_sql('alias_favourites', self.conn, if_exists='append', index=False)

    def delete_alias(self, alias: str):
        self.execute(f'DELETE FROM aliases WHERE alias LIKE "{alias}"')



    def set_dividend_cash(self, isin: str, isin_div: str):
        df = pd.DataFrame({'ISIN': [isin], 'ISIN_DIV': [isin_div]})
        df.to_sql('dividend_cash', self.conn, if_exists='append', index=False)

    def get_dividend_cash(self, isin: str):
        df = pd.read_sql(f'SELECT * FROM dividend_cash WHERE ISIN LIKE "{isin}"', self.conn)
        if not df.empty:
            return df.ISIN_DIV[0]
        return None

    def delete_dividend_cash_isin(self, isin: str):
        self.execute(f'DELETE FROM dividend_cash WHERE isin LIKE {isin}')

