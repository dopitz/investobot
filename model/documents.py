import pandas as pd
import datetime
import json
import operator

from . import DB

import config

class DocType:
    INVOICE_BUY         = 'invoice_buy'
    INVOICE_SELL        = 'invoice_sell'
    DIVIDEND            = 'dividend'
    ADVANCE_TAX         = 'advance_tax'
    CHANGE_STOCK_IN     = 'change_in_stocks_in'
    CHANGE_STOCK_OUT    = 'change_in_stocks_out'
    CHANGE_STOCK_CANCEL = 'change_in_stocks_cancel'
    ANNUAL_COST         = 'annual_cost'


class Doc:
    def __bool__(self):
        return bool(self.get_content())

    def get_doctype(self):
        assert False, 'get_doctype not implemented'

    def get_isin(self):
        assert False, 'get_isin not implemented'

    def get_application_date(self):
        assert False, 'get_application_date not implemented'

    def get_content(self):
        assert False, 'get_content not implemented'



class Documents(DB):
    def __init__(self):
        super().__init__()
        if not self.has_table('documents') and not config.DRYRUN:
            self.execute('CREATE TABLE "documents" ("Type" TEXT, "ISIN" TEXT, "ApplicationDate" TEXT, "Content" TEXT, "ImportDate" DATE, "ID" INTEGER, "Document" TEXT)')

    
    def import_document(self, doc, import_filename: str):
        docs = None
        if isinstance(doc, Doc):
            docs = [doc]
        elif isinstance(doc, list) and all([isinstance(d, Doc) for d in doc]):
            docs = doc
        else:
            assert False, 'invalid argument'

        maxid = pd.read_sql('SELECT max(ID) from documents', self.conn)['max(ID)'][0]
        maxid = 0 if maxid is None else maxid + 1

        ds = None
        for c, doc in enumerate(docs):
            new = pd.DataFrame({
                'ID': [maxid + c], 
                'Type': [doc.get_doctype()], 
                'ISIN': [doc.get_isin()], 
                'ApplicationDate': [doc.get_application_date()], 
                'Content': [json.dumps(doc.get_content(), indent=2)], 
                'ImportDate': [datetime.date.today()], 
                'Document': import_filename
            })
            ds = new if ds is None else pd.concat([ds, new])

        if config.VERBOSE:
            print(ds)
        

        ds.ApplicationDate = pd.to_datetime(ds.ApplicationDate)

        if not config.DRYRUN:
            ds.to_sql('documents', self.conn, if_exists='append', index=False)


    def get(self, isin: str = None):
        df = pd.read_sql('SELECT * from documents ORDER BY ID', self.conn)
        if isin:
            df = df.loc[df.ISIN == isin]
        df.ApplicationDate = pd.to_datetime(df.ApplicationDate).apply(lambda x: x.date())

        # remove rows with canceled ordernumbers
        ordernr = df.Content.apply(lambda x: json.loads(x)).apply(lambda x: x['OrderNumber']['value'] if 'OrderNumber' in x else None)

        cancel = df.loc[df.Type == DocType.CHANGE_STOCK_CANCEL]
        for i,row in cancel.iterrows():
            content = json.loads(row.Content)
            df = df.loc[ordernr != content['OrderNumber']['value']]
            df = df.loc[ordernr != content['CancelOrderNumber']['value']]

        return df



def __aggregate(name, docs, doctype_map, start, start_date=None):

    date = [docs.ApplicationDate.min() - datetime.timedelta(days=1)]
    agg = [start]

    for i,row in docs.iterrows():
        content = json.loads(row.Content)
        if row.Type in doctype_map:
            date.append(row.ApplicationDate)

            v = agg[-1]
            for op, access in doctype_map[row.Type]:
                for a in access:
                    x = content
                    if a[0] in content:
                        for n in a:
                            x = x[n]
                        v = op(v, x)

            agg.append(v)

    if start_date:
        date[0] = min(date[0], start_date)

    df = pd.DataFrame({'date': date, name: agg})

    if start_date:
        df.index = pd.DatetimeIndex(df.date)
        df = df.reindex(pd.date_range(df.index.min(), datetime.date.today()), fill_value=None)
        df = df.ffill()
        df.date = df.index
        df = df.reset_index()
        df = df.drop(columns=['index'])

    return df


def get_nominal(docs, start_date=None):
    return __aggregate(
        'nominal',
        docs,
        {
            DocType.INVOICE_BUY     : [(operator.add, [['Nominal', 'value']])],
            DocType.INVOICE_SELL    : [(operator.sub, [['Nominal', 'value']])],
            DocType.CHANGE_STOCK_IN : [(operator.add, [['Nominal', 'value']])],
            DocType.CHANGE_STOCK_OUT: [(operator.sub, [['Nominal', 'value']])],
        },
        0,
        start_date
    )

def get_expenses(docs, start_date=None):
    return __aggregate(
        'expenses',
        docs,
        {
            DocType.INVOICE_BUY : [(operator.add, [['TotalCharge', 'value']])],
            DocType.INVOICE_SELL: [(operator.sub, [['TotalBenefit', 'value']])],
        },
        0,
        start_date
    )

def get_dividends(docs, start_date=None):
    return __aggregate(
        'dividends',
        docs,
        {
            DocType.DIVIDEND: [(operator.add, [['TotalCredit', 'value']])],
        },
        0,
        start_date
    )

def get_fees(docs, start_date=None):
    return __aggregate(
        'fees',
        docs,
        {
            DocType.INVOICE_BUY : [(operator.add, [['Provision', 'value']])],
            DocType.INVOICE_SELL: [(operator.add, [['Provision', 'value']])],
            DocType.ANNUAL_COST : [(operator.add, [['TotalFees', 'value']])],
        },
        0,
        start_date
    )
    
def get_taxes(docs, start_date=None):
    return __aggregate(
        'taxes',
        docs,
        {
            DocType.DIVIDEND: [(operator.add, [['SourceTax', 'EUR'], ['CapitalGainsTax', 'value'], ['SolidarityTax', 'value']])],
        },
        0,
        start_date
    )
    