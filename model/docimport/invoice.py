from .field import Field, parse_fields, parse_name_value, parse_name_unit_value, parse_datetime

ORDER_NR        = Field('Ordernummer', 'OrderNumber', parse_name_value)
ISIN            = Field('ISIN (WKN)', 'ISIN', parse_name_value)
SECURITY_NAME   = Field('Wertpapierbezeichnung', 'SecurityName', parse_name_value)
NOMINAL         = Field('Nominale', 'Nominal', parse_name_unit_value)
PRICE           = Field('Kurs', 'StockPrice', parse_name_unit_value)
STOCK_EXCHANGE  = Field('Handelsplatz', 'StockExchange', parse_name_value)
EXE_TIME        = Field('Ausführungstag / -zeit', 'ExecutionTime', parse_datetime)
ORDER_VALUE     = Field('Kurswert', 'OrderValue', parse_name_unit_value)
PROVISION       = Field('Provision', 'Provision', parse_name_unit_value)
TOTAL_CHARGE    = Field('Endbetrag zu Ihren Lasten', 'TotalCharge', parse_name_unit_value)
TOTAL_CREDIT    = Field('Endbetrag zu Ihren Gunsten', 'TotalCredit', parse_name_unit_value)


from model.documents import Doc, DocType

class Invoice(Doc):
    def __init__(self):
        self.fields = [
            ORDER_NR,
            ISIN,
            SECURITY_NAME,
            NOMINAL,
            PRICE,
            STOCK_EXCHANGE,
            EXE_TIME,
            ORDER_VALUE,
            PROVISION,
        ]

        self.content = {}

    def parse(self, text: str):
        self.content = parse_fields(self.fields, text)

        if PROVISION.alias not in self.content:
            self.content[PROVISION.alias] = {'name': PROVISION.source, 'value': 0, 'unit': 'EUR'}

    def get_isin(self):
        return self.content[ISIN.alias]['value'].split()[0]

    def get_application_date(self):
        return self.content[EXE_TIME.alias]['value']

    def get_content(self):
        return self.content



class InvoiceBuy(Invoice):
    def __init__(self, text: str):
        super().__init__()
        self.fields.append(TOTAL_CHARGE)
        self.fields.append(Field('Abrechnungs-IBAN', None, None))
        self.parse(text)

    def get_doctype(self):
        return DocType.INVOICE_BUY

class InvoiceSell(Invoice):
    def __init__(self, text: str):
        super().__init__()
        self.fields.append(TOTAL_CHARGE)
        self.fields.append(Field('Abrechnungs-IBAN', None, None))
        self.parse(text)

    def get_doctype(self):
        return DocType.INVOICE_SELL
