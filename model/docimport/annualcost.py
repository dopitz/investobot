from .field import Field, parse_fields, parse_name_value_unit
from model.documents import Doc, DocType
from datetime import datetime

class AnnualCost(Doc):
    def split_cost_details(pages):
        text = '\n'.join([p.extract_text() for p in pages[2:-1]])

        # remove header
        text = text.replace('Detaillierte Kostenübersicht im Berichtszeitraum auf Wertpapierebene', '')
        # clean lines
        lines = [l.strip() for l in text.split('\n')]
        # extract lines starting with ISIN, will give us blocks with cost information
        plines = [c for c, l in enumerate(lines) if l.startswith('ISIN')]

        content_text = ['\n'.join(lines[p-1:p+7]) for p in plines]

        lines = [l for l in pages[1].extract_text().split('\n') if l.startswith('Berichtszeitraum')]
        report_period_end = datetime.strptime(lines[0].split()[2][1:], '%d.%m.%Y')
        
        return content_text, report_period_end


    def __init__(self, text: str, report_date: datetime):
        self.parse(text)
        self.content['ReportDate'] = {
            'source' : 'Berichtszeitraum Ende',
            'value' : str(report_date),
        }

    def parse(self, text: str):

        lines = text.split('\n')

        fields = [
            Field('Wertpapierdienstleistungskosten', 'ServiceFee', parse_name_value_unit),
            Field('Produktkosten', 'ProductCost', parse_name_value_unit),
            Field('Gesamtkosten Gattung', 'TotalFees', parse_name_value_unit),
            Field('Zusätzlich erhielten wir Zuwendungen', 'AdditionalFee', parse_name_value_unit),
            Field('Die Rendite Ihres Wertpapiers', None, None),
        ]

        self.content = parse_fields(fields, '\n'.join(lines[2:]))

        self.content['SecurityName'] = {
            'source' : 'Wertpapierbezeichnung',
            'value' : lines[0].strip(),
        }

        isin = lines[1].strip().split()
        isin = f'{isin[1]} ({isin[3][:-1]})'
        self.content['ISIN'] = {
            'source' : 'ISIN (WKN)',
            'value' : isin,
        }

    def get_doctype(self):
        return DocType.ANNUAL_COST

    def get_isin(self):
        return self.content['ISIN']['value'].split()[0]

    def get_application_date(self):
        return self.content['ReportDate']['value']

    def get_content(self):
        return self.content
