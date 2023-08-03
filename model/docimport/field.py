from collections import namedtuple
import sys
import datetime

Field = namedtuple('Field', 'source alias parse')


def parse_float(text):
    return float(text.replace('.', '').replace(',','.'))

def parse_name_value(text, source_name):
    return {'source': source_name, 'value': text[len(source_name):].replace("\n", " ").strip()}

def parse_name_unit_value(text, name):
    nv = parse_name_value(text, name)
    s = nv['value'].split()
    nv['unit'] = s[0]
    nv['value'] = parse_float(s[1])
    return nv

def parse_name_value_unit(text, name):
    nv = parse_name_value(text, name)
    s = nv['value'].split()
    nv['unit'] = s[1]
    nv['value'] = parse_float(s[0])
    return nv

def parse_datetime(text, name):
    nv = parse_name_value(text, name)
    nv['value'] = str(datetime.datetime.strptime(nv['value'], '%d.%m.%Y um %H:%M:%S Uhr'))
    return nv

def parse_date(text, name):
    nv = parse_name_value(text, name)
    nv['value'] = str(datetime.datetime.strptime(nv['value'], '%d.%m.%Y'))
    return nv

def parse_tax(text, name):
    nv = parse_name_value(text, name)
    s = nv['value'].split()
    nv['percent'] =  parse_float(s[0][:-1])
    offset = 0 if len(s) == 3 else 1
    nv['unit'] = s[1 + offset]
    nv['value'] = parse_float(s[2 + offset])
    return nv



def parse_fields(fields: [], text):
    positions = []
    fields = fields[:]

    # previous position
    pp = 0
    while fields:
        # find starting position of next field
        pmin = sys.maxsize
        for f in fields:
            p = text.find(f.source, pp)
            if p != -1 and p < pmin:
                pmin = p
                fmin = f

        # store position, remove field from token list
        if pmin != sys.maxsize:
            pp = pmin
            if positions:
                (f, b, e) = positions[-1]
                positions[-1] = (f, b, pmin)
            positions.append((fmin, pmin, 0))
            fields.remove(fmin)

        else:
            #print(f'fields not found: {fields}')
            break

    # we are not interested in last field
    positions.pop()

    for f,b,e in positions:
        print(f)
        print(b)
        print(e)
        print(text[b:e])
        f.parse(text[b:e], f.source)

    return {f.alias: f.parse(text[b:e], f.source) for (f,b,e) in positions}