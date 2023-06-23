from PyPDF2 import PdfReader
import os
import shutil
import uuid

from .invoice import InvoiceBuy, InvoiceSell
from .earnings import Dividend, AdvanceTax
from .change_stock import ChangeStocksIn, ChangeStocksOut, ChangeStocksCancel
from .annualcost import AnnualCost
from model.documents import Documents

import config

def import_folder(path: str, archive: str):
    directory = os.fsencode(path)
    count = 0
    for f in os.listdir(directory):
        fn = os.fsdecode(f)
        if fn.endswith(".pdf"):
            count = count + import_pdf(path+os.path.sep+fn, archive)

    print(f'Imported {count} documents')


def import_pdf(filename: str, archive: str):
    reader = PdfReader(filename)

    # slect import type
    page = reader.pages[0]
    text = page.extract_text()

    p = text.find('\n')
    subject = text[:p]

    import_filename = archive + os.path.sep + uuid.uuid4().hex + '.pdf'

    doc = None
    if subject.startswith('Wertpapierabrechnung') and 'Kauf' in subject:
        doc = InvoiceBuy(text)

    elif subject.startswith('Wertpapierabrechnung') and 'Verkauf' in subject:
        doc = InvoiceSell(text)

    elif subject.startswith('Dividendengutschrift'):
        doc = Dividend(text)

    elif subject.startswith('Vorabpauschale'):
        doc = AdvanceTax(text)

    elif (subject.startswith('Wertpapier') or subject.startswith('Umtausch')) and 'Eingang' in subject:
        doc = ChangeStocksIn(text)

    elif (subject.startswith('Wertpapier') or subject.startswith('Umtausch')) and 'Ausgang' in subject:
        doc = ChangeStocksOut(text)

    elif subject.startswith('Storno'):
        doc = ChangeStocksCancel(text)

    elif 'Kostenaufstellung' in text:
        text, report_date = AnnualCost.split_cost_details(reader.pages)
        doc = [AnnualCost(t, report_date) for t in text]
        
    if doc:
        Documents().import_document(doc, import_filename)
        shutil.move(filename, import_filename)
        return True

    else:
        ask = ''
        if config.HANDLE_IGNORED == 'ask':
            ask = input(f'{filename} was not imported ... (d)elete, (a)rchive, (s)kip, (D)elete all, (A)rchive all, (S)kip all?  ')
            if ask == 'D':
                config.HANDLE_IGNORED = 'delete'
            if ask == 'A':
                config.HANDLE_IGNORED = 'archive'
            if ask == 'S':
                config.HANDLE_IGNORED = 'skip'

        if config.HANDLE_IGNORED == 'archive' or ask == 'a':
            import_filename = archive + os.path.sep + os.path.basename(filename)
            shutil.move(filename, import_filename)
            if config.VERBOSE:
                print(f'{filename} was not imported ...  moving to {import_filename}')

        elif config.HANDLE_IGNORED == 'delete' or ask == 'd':
            os.remove(filename)
            if config.VERBOSE:
                print(f'{filename} was not imported ...  deleting')

        elif config.HANDLE_IGNORED == 'skip' or ask == 's':
            if config.VERBOSE:
                print(f'{filename} was not imported ...  skipping')


    return False