#!/usr/bin/env python3

import sys

from tools.complete import Complete
from tools.backup import Backup
from tools.docimport import Docimport
from tools.alias import Alias
from tools.tracker import Tracker
from tools.stats import Stats

import model.estimate_provision

tools = {
    'backup': Backup(),
    'docimport': Docimport(),
    'alias': Alias(),
    'tracker': Tracker(),
    'stats': Stats(),
}

if len(sys.argv) >= 2:

    if sys.argv[1] == 'complete':
        Complete().run(tools)
        exit()

    if sys.argv[1] in tools:
        tools[sys.argv[1]].run()
        exit()

print("help")
exit()




import config
from model.documents import Documents
from model.aliases import Aliases

from args import parse_cmd
args = parse_cmd()


print(args)

config.VERBOSE          = args.verbose
config.DRYRUN           = args.dryrun
config.HANDLE_IGNORED   = args.ignored

if args.tool == 'import':
    import docimport
    docimport.import_folder(args.input, args.archive)

if args.tool == 'complete':
    aliases = Aliases()

    if args.alias:
        [print(a) for a in aliases.get_similar_aliases(args.alias)]
    elif args.isin:
        [print(i) for i in aliases.get_similar_isins(args.isin)]
    else:
        print()


if args.tool == 'alias':
    aliases = Aliases()

    # isin and alias specified means, we create this alias
    if args.isin and args.alias:
        isin = args.isin
        if not args.strong_match:
            isin = aliases.get_similar_isins(isin)
            if not isin or len(isin) > 1:
                print('aoeuaoeu')
            isin = isin[0]
        aliases.make_alias(args.isin, args.alias)

    # find alias and create a new one (if alias is pointing to a unique isin)
    elif args.alias and args.new_alias:
        isin = aliases.get_isin(args.alias, args.strong_match, unique=True)
        if not isin:
            print(f'Could not create new alias. Alias "{args.alias}" not found or ambiguous:')
            print(aliases.get_isin_like(args.alias))
            exit()

        aliases.make_alias(isin, args.new_alias)

    # only isin specified lists all aliases for this isin
    elif args.isin:
        print(aliases.get_aliases(args.isin, args.strong_match).sort_values(by='ISIN'))

    # only alias specified lists all isins for this alias
    elif args.alias:
        print(aliases.get_isin(args.alias, args.strong_match))
    
    # nothing specified will create aliases for every SecurityName in imported documents' content
    else:
        import json

        docs = Documents().get()
        for i, row in docs.iterrows():
            isin = row.ISIN
            name = json.loads(row.Content)['SecurityName']['value']

            aliases.make_alias(isin, name)



if args.tool == 'yahoo-tracker':

    aliases = Aliases()
    isin = None

    if args.alias:
        isin = aliases.get_isin(args.alias, args.strong_match, unique=True)

    if args.isin:
        isin = aliases.get_similar_isins(isin)(args.alias, args.strong_match, unique=True)


        

    #Aliases().make_alias('DE0007100000', 'Mercedes-Benz Group AG Namens-Aktien o.N.')
    #print(Aliases().get_aliases('DE0007100000'))
    #print(Aliases().get_isin('Mercedes-Benz Group AG Namens-Aktien o.N.'))
    #print(Aliases().get_isin_like('Mercedes'))
    

if args.tool == 'summary':
    pass

if args.tool == 'detail':
    pass


