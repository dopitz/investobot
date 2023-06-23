from .field import Field, parse_fields, parse_name_value, parse_name_value_unit, parse_name_unit_value, parse_date, parse_tax, parse_float

from model.documents import Doc, DocType


class ChangeStocksDoc(Doc):
    def __init__(self, text: str):
        self.parse(text)

    def parse(self, text: str):
        import datetime

        table_headline = 'Nominale / Stück Wertpapier-Informationen Schlusstag Auftragsnummer'
        p = text.find(table_headline)
        if p == -1:
            return False


        text = text[p+len(table_headline)+1:]

        s = text.split()

        p = s.index('(WKN):')

        self.content = {
            'SecurityName': {
                'source' : 'Wertpapierbezeichnung',
                'value' : ' '.join(s[4:p-1]),
            },
            'ISIN': {
                'source' : 'ISIN (WKN)',
                'value' : ' '.join(s[p+1:p+3]),
            },
            'Nominal' : {
                'source': 'Nominale',
                'value': parse_float(s[0]),
                'unit': s[1],
            },
            'ClosingDay' : {
                'source': 'Schlusstag',
                'value': str(datetime.datetime.strptime(s[2], '%d.%m.%Y')),
            },
            'OrderNumber' : {
                'source': 'Auftragsnummer',
                'value': s[3],
            },
        }

        if 'Auftragsnummer' in s:
            p = s.index('Auftragsnummer')
            self.content['CancelOrderNumber'] = {
                    'source': 'Storno',
                    'value': s[p+1][:-1],
                }


    def get_isin(self):
        return self.content['ISIN']['value'].split()[0]

    def get_application_date(self):
        return self.content['ClosingDay']['value']

    def get_content(self):
        return self.content


class ChangeStocksIn(ChangeStocksDoc):
    def get_doctype(self):
        return DocType.CHANGE_STOCK_IN

class ChangeStocksOut(ChangeStocksDoc):
    def get_doctype(self):
        return DocType.CHANGE_STOCK_OUT

class ChangeStocksCancel(ChangeStocksDoc):
    def get_doctype(self):
        return DocType.CHANGE_STOCK_CANCEL