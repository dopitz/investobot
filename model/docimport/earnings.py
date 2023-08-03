from .field import Field, parse_fields, parse_name_value, parse_name_value_unit, parse_name_unit_value, parse_date, parse_tax, parse_float

def parse_qust(text, name):
    nv = parse_name_value(text, name)
    s = nv['value'].split('%')
    nv['percent'] =  parse_float(s[0])
    s = s[1][1:].split(')')
    nv['EUR'] = parse_float(s[0][5:-1])
    s = s[0].split()
    nv['unit'] = s[0]
    nv['value'] = parse_float(s[1])
    return nv

def parse_exchange_rate(text, name):
    nv = parse_name_value(text, name)
    s = nv['value'].split()
    nv['rate'] =  parse_float(s[0][1:-1])
    nv['unit'] = s[1]
    nv['value'] = parse_float(s[2])
    return nv


ISIN                = Field('ISIN (WKN)', 'ISIN', parse_name_value)
SECURITY_NAME       = Field('Wertpapierbezeichnung', 'SecurityName', parse_name_value)
NOMINAL             = Field('Nominale', 'Nominal', parse_name_value_unit)
DIVIDEND_RATE       = Field('Zins-/Dividendensatz', 'DividendRate', parse_name_value_unit)
EX_DAY              = Field('Ex-Tag', 'Ex-Day', parse_date)
PAY_DAY             = Field('Zahltag', 'Pay Day', parse_date)
TOTAL_CREDIT        = Field('Gesamtbetrag zu Ihren Gunsten', 'TotalCredit', parse_name_unit_value)

from model.documents import Doc, DocType

class EarningsDoc(Doc):
    def __init__(self):
        self.fields = [
            ISIN,
            SECURITY_NAME,
            NOMINAL,
            EX_DAY,
            PAY_DAY,
            TOTAL_CREDIT,
            Field('Abrechnungs-IBAN', None, None),
        ]

        self.content = {}

    def parse(self, text: str):
        self.content = parse_fields(self.fields, text)

    def get_isin(self):
        return self.content[ISIN.alias]['value'].split()[0]

    def get_application_date(self):
        return self.content[PAY_DAY.alias]['value']

    def get_content(self):
        return self.content



class Dividend(EarningsDoc):
    def __init__(self, text: str):
        super().__init__()
        self.fields = self.fields + [
            Field('Brutto', 'Gross', parse_name_unit_value),
            Field('QuSt', 'SourceTax', parse_qust),
            Field('Zwischensumme', 'Subtotal', parse_name_unit_value),
            Field('Umg. z. Dev.-Kurs', 'ExchangeRate', parse_exchange_rate),
            Field('Kapitalertragsteuer', 'CapitalGainsTax', parse_tax),
            Field('Solidaritätszuschlag', 'SolidarityTax', parse_tax),
        ]
        self.parse(text)

    def get_doctype(self):
        return DocType.DIVIDEND

class AdvanceTax(EarningsDoc):
    def __init__(self, text: str):
        super().__init__()
        self.fields = self.fields + [
            Field('Vorabpauschale gem. § 18 InvStG', 'AdvanceTax', parse_name_unit_value),
            Field('KapSt-pflichtiger Kapitalertrag', 'TaxableAmount', parse_name_unit_value),
        ]
        self.parse(text)

    def get_doctype(self):
        return DocType.ADVANCE_TAX
